import multiaddr
import asyncio

from libp2p import new_node
from libp2p.peer.peerinfo import info_from_p2p_addr
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub
from tests.pubsub.utils import message_id_generator
from libp2p.peer.id import ID

TOPIC = "eth"
SUPPORTED_PUBSUB_PROTOCOLS = ["/floodsub/1.0.0"]

class ReceiverNode():
    """
    Node which has an internal balance mapping, meant to serve as 
    a dummy crypto blockchain. There is no actual blockchain, just a simple
    map indicating how much crypto each user in the mappings holds
    """

    def __init__(self):
        self.next_msg_id_func = message_id_generator(0)

    async def connect(self, node1, node2_addr):
        # node1 connects to node2
        info = info_from_p2p_addr(node2_addr)
        await node1.connect(info)

    @classmethod
    async def create(cls, node_id, transport_opt_str, ack_protocol, topic, topology_config_dict):
        """
        Create a new ReceiverNode and attach a libp2p node, a floodsub, and a pubsub
        instance to this new node

        We use create as this serves as a factory function and allows us
        to use async await, unlike the init function
        """
        self = ReceiverNode()

        id_opt = ID("peer-" + node_id)

        libp2p_node = await new_node(id_opt=id_opt, transport_opt=[transport_opt_str])
        await libp2p_node.get_network().listen(multiaddr.Multiaddr(transport_opt_str))

        self.libp2p_node = libp2p_node

        self.floodsub = FloodSub(SUPPORTED_PUBSUB_PROTOCOLS)
        self.pubsub = Pubsub(self.libp2p_node, self.floodsub, "a")

        print('subbing to: ' + topic)
        self.pubsub_messages = await self.pubsub.subscribe(topic)
        self.topic = topic

        self.ack_protocol = ack_protocol

        self.topology_config_dict = topology_config_dict

        async def command_stream_handler(stream):
            print("Command stream handler entered")
            nonlocal topology_config_dict, node_id
            start_cmd = (await stream.read()).decode()
            print("Command received")
            if start_cmd == "start":
                print("Starting")
                # Connect receiver node to all other relevant receiver nodes, if receiver node
                # is listed in adjacency list
                if node_id in self.topology_config_dict["topology"]:
                    for neighbor in self.topology_config_dict["topology"][node_id]:
                        neighbor_addr_str = self.topology_config_dict["node_id_map"][neighbor]

                        # Add p2p part
                        neighbor_addr_str += "/p2p/" + ID("peer-" + neighbor).pretty()

                        # Convert neighbor_addr_str to multiaddr
                        neighbor_addr = multiaddr.Multiaddr(neighbor_addr_str)
                        await self.connect(self.libp2p_node, neighbor_addr)

                # Get sender info as multiaddr
                sender_addr_str = self.topology_config_dict["node_id_map"]["sender"]

                # Convert sender_info_str to multiaddr
                sender_addr = multiaddr.Multiaddr(sender_addr_str + '/p2p/' + ID('peer-sender').pretty())

                # Start listening for messages from sender
                print("Start receiving called")
                sender_info = info_from_p2p_addr(sender_addr)
                self.libp2p_node.peerstore.add_addrs(sender_info.peer_id, sender_info.addrs, 10)
                asyncio.ensure_future(self.start_receiving(sender_info))
            else:
                print("Invalid command")

        self.libp2p_node.set_stream_handler("/command/1.0.0", command_stream_handler)

        return self

    async def wait_for_end(self, ack_stream):
        # Continue waiting for end message, even if None (i.e. timeout) is received
        msg = await ack_stream.read()
        while msg is None:
            msg = await ack_stream.read()
        msg = msg.decode()
        if msg == "end":
            self.should_listen = False
            print("End received")

    async def start_receiving(self, sender_node_info):
        print("Receiving started")

        print("My sender is " + sender_node_info.peer_id.pretty())
        ack_stream = await self.libp2p_node.new_stream(sender_node_info.peer_id, [self.ack_protocol])
        print("Ack stream created")
        asyncio.ensure_future(self.wait_for_end(ack_stream))

        print("Listening for ack messages")
        self.should_listen = True
        ack_msg = self.topic
        encoded_ack_msg = ack_msg.encode()
        while self.should_listen:
            print('about to read pubsub')
            msg = await self.pubsub_messages.get()
            print('about to write ack')
            await ack_stream.write(encoded_ack_msg)
            print('acked back')
        print("Receiver closed")
