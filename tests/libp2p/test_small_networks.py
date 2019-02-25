import multiaddr
import pytest

from tests.utils import cleanup
from libp2p import new_node
from libp2p.peer.peerinfo import info_from_p2p_addr

# pylint: disable=too-many-locals

@pytest.mark.asyncio
async def test_triangle_nodes_connection():
    node_a = await new_node(transport_opt=["/ip4/127.0.0.1/tcp/0"])
    node_b = await new_node(transport_opt=["/ip4/127.0.0.1/tcp/0"])
    node_c = await new_node(transport_opt=["/ip4/127.0.0.1/tcp/0"])

    async def stream_handler(stream):
        while True:
            read_string = (await stream.read()).decode()

            response = "ack:" + read_string
            await stream.write(response.encode())

    node_a.set_stream_handler("/echo/1.0.0", stream_handler)
    node_b.set_stream_handler("/echo/1.0.0", stream_handler)
    node_c.set_stream_handler("/echo/1.0.0", stream_handler)

    # Associate the peer with local ip address (see default parameters of Libp2p())
    # Associate all permutations
    node_a.get_peerstore().add_addrs(node_b.get_id(), node_b.get_addrs(), 10)
    node_a.get_peerstore().add_addrs(node_c.get_id(), node_c.get_addrs(), 10)

    node_b.get_peerstore().add_addrs(node_a.get_id(), node_a.get_addrs(), 10)
    node_b.get_peerstore().add_addrs(node_c.get_id(), node_c.get_addrs(), 10)

    node_c.get_peerstore().add_addrs(node_a.get_id(), node_a.get_addrs(), 10)
    node_c.get_peerstore().add_addrs(node_b.get_id(), node_b.get_addrs(), 10)

    stream_a_to_b = await node_a.new_stream(node_b.get_id(), ["/echo/1.0.0"])
    stream_a_to_c = await node_a.new_stream(node_c.get_id(), ["/echo/1.0.0"])

    stream_b_to_a = await node_b.new_stream(node_a.get_id(), ["/echo/1.0.0"])
    stream_b_to_c = await node_b.new_stream(node_c.get_id(), ["/echo/1.0.0"])

    stream_c_to_a = await node_c.new_stream(node_a.get_id(), ["/echo/1.0.0"])
    stream_c_to_b = await node_c.new_stream(node_b.get_id(), ["/echo/1.0.0"])

    messages = ["hello" + str(x) for x in range(5)]
    streams = [stream_a_to_b, stream_a_to_c, stream_b_to_a, stream_b_to_c,
               stream_c_to_a, stream_c_to_b]

    for message in messages:
        for stream in streams:
            await stream.write(message.encode())

            response = (await stream.read()).decode()

            assert response == ("ack:" + message)

    # Success, terminate pending tasks.
    await cleanup()
