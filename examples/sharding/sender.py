import asyncio
import multiaddr

from timeit import default_timer as timer

from tests.utils import cleanup
from tests.pubsub.utils import generate_RPC_packet, message_id_generator
from libp2p import new_node
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub
from libp2p.peer.id import ID

SUPPORTED_PUBSUB_PROTOCOLS = ["/floodsub/1.0.0"]
TOPIC = "eth"

class SenderNode():
    """
    SenderNode which pings ReceiverNodes continuously to perform benchmarking
    """

    def __init__(self):
        self.next_msg_id_func = message_id_generator(0)
        self.ack_queue = asyncio.Queue()

    @classmethod
    async def create(cls, my_node_id, transport_opt_str, ack_protocol):
        """
        Create a new DummyAccountNode and attach a libp2p node, a floodsub, and a pubsub
        instance to this new node

        We use create as this serves as a factory function and allows us
        to use async await, unlike the init function
        """
        self = SenderNode()

        id_opt = ID("peer-" + my_node_id)
        print("My sender is " + id_opt.pretty())

        libp2p_node = await new_node(id_opt=id_opt, transport_opt=[transport_opt_str])
        await libp2p_node.get_network().listen(multiaddr.Multiaddr(transport_opt_str))

        self.libp2p_node = libp2p_node

        self.floodsub = FloodSub(SUPPORTED_PUBSUB_PROTOCOLS)
        self.pubsub = Pubsub(self.libp2p_node, self.floodsub, "a")
        await self.pubsub.subscribe(TOPIC)

        self.test_being_performed = True

        self.all_streams = []
        async def ack_stream_handler(stream):
            self.all_streams.append(stream)

            while self.test_being_performed:
                # This Ack is what times out when multi-topic tests finish
                ack = await stream.read()
                if ack is not None:
                    print("Ack waiting")
                    await self.ack_queue.put(ack)
                    print("Ack received!")
                else:
                    print("FUCK")
                    break
            # Reached once test_being_performed is False
            # Notify receivers test is over
            print("Writing end")
            await stream.write("end".encode())

        # Set handler for acks
        self.ack_protocol = ack_protocol
        self.libp2p_node.set_stream_handler(self.ack_protocol, ack_stream_handler)

        return self

    async def perform_test(self, num_receivers_in_each_topic, topics, time_length):
        # Time and loop
        print("Perform test called")
        print(num_receivers_in_each_topic)
        my_id = str(self.libp2p_node.get_id())
        msg_contents = "transaction"

        num_sent_in_each_topic = {}
        num_acks_in_each_topic = {}
        for topic in topics:
            num_sent_in_each_topic[topic] = 0
            num_acks_in_each_topic[topic] = 0

        self.topic_ack_queues = {}
        for topic in topics:
            self.topic_ack_queues[topic] = asyncio.Queue()
        completed_topics_count = 0
        num_topics = len(topics)
        async def handle_ack_queues():
            start = timer()
            curr_time = timer()

            print("Handling ack queues")
            nonlocal completed_topics_count, num_topics
            while completed_topics_count < num_topics:
                print("handling ack queue waiting")
                ack = await self.ack_queue.get()
                print("handling ack queue got!")
                decoded_ack = ack.decode()
                print("handling ack queue decoded ack is " + decoded_ack)
                await self.topic_ack_queues[decoded_ack].put(decoded_ack)
                print("handling ack queue decoded ack put")

                curr_time = timer()

        async def end_all_async():
            # Add None to ack_queue to break out of the loop.
            # Note: This is necessary given the current code or the code will never
            # terminate
            await self.ack_queue.put(None)

            # This is not necessary but is useful for turning off the receivers gracefully
            for stream in self.all_streams:
                await stream.write("end".encode())

        async def perform_test_on_topic(topic):
            print("Performing test on topic " + topic)
            start = timer()
            curr_time = timer()

            # Perform test while time is not up here AND
            # while time is not up in handle_ack_queues, which is checked with the
            # self.test_being_performed boolean
            while (curr_time - start) < time_length:
                # Send message on single topic
                print("Generating packet")
                packet = generate_RPC_packet(my_id, [topic], msg_contents, self.next_msg_id_func())

                await self.floodsub.publish(my_id, packet.SerializeToString())
                print("Publishing packet")
                num_sent_in_each_topic[topic] += 1
                
                # Wait for acks
                num_acks = 0

                # While number of acks is below threshold AND
                # while time is not up in handle_ack_queues, which is checked with the
                # self.test_being_performed boolean 
                # TODO: Check safety of this. Does this make sense in the asyncio
                # event-driven setting?
                while num_acks < num_receivers_in_each_topic[topic]:
                    print("Test- Waiting for ack on " + topic)
                    ack = await self.topic_ack_queues[topic].get()
                    print("Test- Ack got on " + topic)
                    num_acks += 1
                num_acks_in_each_topic[topic] += 1
                curr_time = timer()
            print("Left while")
            nonlocal completed_topics_count, num_topics
            print("Test completed " + topic)
            completed_topics_count += 1
            if completed_topics_count == num_topics:
                self.test_being_performed = False
                print("End all async")
                await end_all_async()

        tasks = [asyncio.ensure_future(handle_ack_queues())]

        for topic in topics:
            tasks.append(asyncio.ensure_future(perform_test_on_topic(topic)))

        gathered = await asyncio.gather(*tasks, return_exceptions=True)

        # Do something interesting with test results
        print("Num sent: " + str(num_sent_in_each_topic))
        print("Num fully ack: " + str(num_acks_in_each_topic))
        
        # End test
        self.test_being_performed = False
