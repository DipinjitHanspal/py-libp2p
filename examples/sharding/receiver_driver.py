import asyncio
import json 
import multiaddr
import sys
import concurrent.futures
from libp2p.peer.id import ID
from sender import SenderNode
from receiver import ReceiverNode
from libp2p.peer.peerinfo import info_from_p2p_addr
from tests.utils import cleanup

from easy_sqs import EasySqs

ACK_PROTOCOL = "/ack/1.0.0"

"""
Driver is called in the following way
python receiver_driver.py topology_config.json "my_node_id"
"""

async def connect(node1, node2_addr):
    # node1 connects to node2
    info = info_from_p2p_addr(node2_addr)
    await node1.connect(info)

async def main():
    """
    Read in topology config file, which contains
    a map of node IDs to peer IDs, an adjacency list (named topology) using node IDs,
    a map of node IDs to topics, and ACK_PROTOCOL

    {
        "node_id_map": {
            "sender": "sender multiaddr",
            "some id 0": "some multiaddr",
            "some id 1": "some multiaddr",
            ...
        },
        "topology": {
            "sender": ["some id 0", "some id 1", ...],
            "0": ["some id 0", "some id 1", ...],
            "1": ["some id 0", "some id 1", ...],
            ...
        },
        "topic_map": {
            "some id 0": "some topic name 1",
            "some id 1": "some topic name 2",
            "some id 2": "some topic name 3"
        },
        "ACK_PROTOCOL": "some ack protocol"
    }

    Ex.
    
    {
        "node_id_map": {
            "sender": "/ip4/127.0.0.1/tcp/8000",
            "0": "/ip4/127.0.0.1/tcp/8001",
            "1": "/ip4/127.0.0.1/tcp/8002",
            "2": "/ip4/127.0.0.1/tcp/8003"
        },
        "topology": {
            "sender": ["0"],
            "0": ["1", "2"],
            "1": ["0"],
            "2": ["0"]
        },
        "topic_map": {
            "0": "topic1",
            "1": "topic1",
            "2": "topic1"
        },
        "ACK_PROTOCOL": "/ack/1.0.0"
    }

    """
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=300)
    topology_config_dict = json.loads(open(sys.argv[1]).read())
    aws_config = json.loads(open("aws_config.json").read())

    sqs_url = topology_config_dict["SQS_URL"]
    sqs_client = EasySqs(aws_config)

    my_node_id = sys.argv[2]

    # Get my topic
    my_topic = topology_config_dict["topic_map"][my_node_id]

    # Create Receiver Node
    print("Creating receiver")
    my_transport_opt_str = topology_config_dict["node_id_map"][my_node_id]
    receiver_node = \
        await ReceiverNode.create(my_node_id, my_transport_opt_str, ACK_PROTOCOL, my_topic, topology_config_dict, sqs_client, sqs_url, pool)
    print("Receiver created")
    
    # Return since all logic is now done in receiver.py
    return

    # Connect receiver node to all other relevant receiver nodes
    await asyncio.sleep(5)
    for neighbor in topology_config_dict["topology"][my_node_id]:
        neighbor_addr_str = topology_config_dict["node_id_map"][neighbor]

        # Add p2p part
        neighbor_addr_str += "/p2p/" + ID("peer-" + neighbor).pretty()

        # Convert neighbor_addr_str to multiaddr
        neighbor_addr = multiaddr.Multiaddr(neighbor_addr_str)
        await connect(receiver_node.libp2p_node, neighbor_addr)

    # Get sender info as multiaddr
    sender_addr_str = topology_config_dict["node_id_map"]["sender"]

    # Convert sender_info_str to multiaddr
    sender_addr = multiaddr.Multiaddr(sender_addr_str + '/p2p/' + ID('peer-sender').pretty())

    # Start listening for messages from sender
    print("Start receiving called")
    sender_info = info_from_p2p_addr(sender_addr)
    receiver_node.libp2p_node.peerstore.add_addrs(sender_info.peer_id, sender_info.addrs, 10)
    asyncio.ensure_future(receiver_node.start_receiving(sender_info))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()
