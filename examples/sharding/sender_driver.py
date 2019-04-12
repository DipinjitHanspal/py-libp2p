import asyncio
import json 
import multiaddr
import sys
import time
import concurrent.futures
from libp2p.peer.id import ID
from sender import SenderNode
from receiver import ReceiverNode
from libp2p.peer.peerinfo import info_from_p2p_addr
from tests.utils import cleanup

from easy_sqs import EasySqs

SLEEP_TIME = 5

async def connect(node1, node2_addr):
    # node1 connects to node2
    info = info_from_p2p_addr(node2_addr)
    await node1.connect(info)

async def main():
    """
    Read in topology config file, which contains
    a map of node IDs to peer IDs, an adjacency list (named topology) using node IDs,
    a map of node IDs to topics, and ACK_PROTOCOL
    """
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=300)
    topology_config_dict = json.loads(open(sys.argv[1]).read())
    aws_config = json.loads(open("examples/sharding/aws_config.json").read())

    sqs_url = topology_config_dict["SQS_URL"]
    sqs_client = EasySqs(aws_config)

    my_node_id = sys.argv[2]

    ack_protocol = topology_config_dict["ACK_PROTOCOL"]

    # Create sender
    print("Creating sender")
    my_transport_opt_str = topology_config_dict["node_id_map"][my_node_id]
    sender_node = await SenderNode.create(my_node_id, my_transport_opt_str, ack_protocol, sqs_client, sqs_url, pool)
    print("Sender created")

    # Allow for all nodes to start up
    # await asyncio.sleep(SLEEP_TIME)

    # new_key = RSA.generate(2048, e=65537)
    # id_opt = id_from_public_key(new_key.publickey())

    # Connect sender node to all other relevant nodes
    print("Connecting")
    for neighbor in topology_config_dict["topology"][my_node_id]:
        neighbor_addr_str = topology_config_dict["node_id_map"][neighbor]

        # Add p2p part
        id_opt = ID("peer-" + neighbor)
        neighbor_addr_str += "/p2p/" + id_opt.pretty()

        # Convert neighbor_addr_str to multiaddr
        neighbor_addr = multiaddr.Multiaddr(neighbor_addr_str)
        await connect(sender_node.libp2p_node, neighbor_addr)
    print("Connected")

    # Get list of all nodes
    all_nodes = list(topology_config_dict["topology"].keys())
    for neighbors_list in topology_config_dict["topology"].values():
        for node in neighbors_list:
            if node not in all_nodes:
                all_nodes.append(node)

    # return

    # Tell all nodes to connect to each other
    for node_id in all_nodes:
        if node_id != "sender":
            id_opt = ID("peer-" + node_id)
            node_addr_str = topology_config_dict["node_id_map"][node_id]
            node_addr_str += "/p2p/" + id_opt.pretty()
            print("Connecting to " + node_addr_str)
            node_addr = multiaddr.Multiaddr(node_addr_str)
            node_info = info_from_p2p_addr(node_addr)
            await sender_node.libp2p_node.connect(node_info)
            command_stream = await sender_node.libp2p_node.new_stream(node_info.peer_id, ["/command/1.0.0"])
            await command_stream.write("start".encode())

    # Wait 2 seconds for nodes to connect
    await asyncio.sleep(2)

    # NOTE: Every node in the network is now a floodsub peer of sender since the PubSub_notifee
    # will ensure that (which is correct). For benchmarking, we do not want this, so we remove
    # all floodsub peers that are not neighbors of sender in the topology
    for node_id in all_nodes:
        if node_id not in topology_config_dict["topology"][my_node_id]:
            # I use this bulk of code because I know it works to get peer_id from info 
            # and I didn't want to deal with errors
            id_opt = ID("peer-" + node_id)
            node_addr_str = topology_config_dict["node_id_map"][node_id]
            node_addr_str += "/p2p/" + id_opt.pretty()
            node_addr = multiaddr.Multiaddr(node_addr_str)
            node_info = info_from_p2p_addr(node_addr)
            sender_node.floodsub.remove_peer(node_info.peer_id)
            print("Removing peer " + node_id + ", id " + str(node_info.peer_id))


    # Perform throughput test
    # Start sending messages and perform throughput test
    # Determine number of receivers in each topic
    topic_map = topology_config_dict["topic_map"]
    topics = list(dict.fromkeys(topic_map.values()))

    num_receivers_in_each_topic = {}
    for topic in topic_map.values():
        if topic in num_receivers_in_each_topic:
            num_receivers_in_each_topic[topic] = num_receivers_in_each_topic[topic] + 1
        else:
            num_receivers_in_each_topic[topic] = 1
        # num_receivers_in_each_topic[topic] = len(topic_map[topic])
    print("Performing test")
    await asyncio.sleep(0.5)
    await sender_node.perform_test(num_receivers_in_each_topic, topics, 10)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()
