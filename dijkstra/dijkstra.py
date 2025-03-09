import sys
import json
import math  # If you want to use math.inf for infinity

from dataclasses import dataclass
from subnets_and_masks.netfuncs import find_router_for_ip


Node = str
NodeWeight = int

AdjacencyList = dict[Node, tuple[Node, NodeWeight]]
Nodes = list[Node]

Graph = dict[Node, set[tuple[Node, NodeWeight]]]


@dataclass
class ConnectionInfo:
    netmask: str
    interface: str
    ad: int


@dataclass
class NetworkInfo:
    connections: dict[str, str]
    netmask: str
    if_count: int
    if_prefix: str


Routers = dict[str, NetworkInfo]


def parse_routers(routers: Routers) -> Graph:
    graph: Graph = {}

    for network, network_info in routers.items():
        netmask = network_info["netmask"]
        network_id = f"{network}{netmask}"

        if network_id not in graph.keys():
            graph[network_id] = set()

        for connection, connection_info in network_info["connections"].items():
            connection_netmask = connection_info["netmask"]
            connection_weight = connection_info["ad"]
            connection_id = f"{connection}{connection_netmask}"

            # add vertex to graph structure:
            graph[network_id].add((connection_id, connection_weight))

            # if connection_id not in graph.keys():
            #     graph[connection_id] = set()
            # graph[connection_id].add((network_id, connection_weight))

    return graph


def dijkstras_shortest_path(routers: Routers, src_ip: str, dest_ip: str) -> Nodes:
    """
    This function takes a dictionary representing the network, a source
    IP, and a destination IP, and returns a list with all the routers
    along the shortest path.

    The source and destination IPs are **not** included in this path.

    Note that the source IP and destination IP will probably not be
    routers! They will be on the same subnet as the router. You'll have
    to search the routers to find the one on the same subnet as the
    source IP. Same for the destination IP. [Hint: make use of your
    find_router_for_ip() function from the last project!]

    The dictionary keys are router IPs, and the values are dictionaries
    with a bunch of information, including the routers that are directly
    connected to the key.

    This partial example shows that router `10.31.98.1` is connected to
    three other routers: `10.34.166.1`, `10.34.194.1`, and `10.34.46.1`:

    {
        "10.34.98.1": {
            "connections": {
                "10.34.166.1": {
                    "netmask": "/24",
                    "interface": "en0",
                    "ad": 70
                },
                "10.34.194.1": {
                    "netmask": "/24",
                    "interface": "en1",
                    "ad": 93
                },
                "10.34.46.1": {
                    "netmask": "/24",
                    "interface": "en2",
                    "ad": 64
                }
            },
            "netmask": "/24",
            "if_count": 3,
            "if_prefix": "en"
        },
        ...

    The "ad" (Administrative Distance) field is the edge weight for that
    connection.

    **Strong recommendation**: make functions to do subtasks within this
    function. Having it all built as a single wall of code is a recipe
    for madness.
    """

    graph = parse_routers(routers)

    source_network = find_router_for_ip(routers, src_ip)
    destination_network = find_router_for_ip(routers, dest_ip)

    source_node = None
    destination_node = None

    for node in graph.keys():
        if node.startswith(source_network):
            source_node = node
        if node.startswith(destination_network):
            destination_node = node

    if source_node == destination_node:
        return []

    return do_dijkstra_shortest_path(graph, source_node, destination_node)


def do_dijkstra_shortest_path(graph: Graph, source_node: Node, destination_node: Node):
    nodes_to_visit: Nodes = []
    distances: dict[Node, int] = {}
    parent: dict[Node, Node] = {}

    for node in graph.keys():
        parent[node] = None
        distances[node] = math.inf
        nodes_to_visit.append(node)

    distances[source_node] = 0

    while len(nodes_to_visit) > 0:
        closest_node = find_closest_node(nodes_to_visit, distances)
        nodes_to_visit.remove(closest_node)

        for neighbor, neighbor_weight in graph[closest_node]:
            if neighbor in nodes_to_visit:
                total_distance = neighbor_weight + distances[closest_node]
                if total_distance < distances[neighbor]:
                    distances[neighbor] = total_distance
                    parent[neighbor] = closest_node

    routers_list = reconstruct_path(parent, source_node, destination_node)
    return routers_list


def reconstruct_path(
    parent: dict[Node, Node], source_node: Node, destination_node: Node
) -> Nodes:

    routers: Nodes = []

    current_node = destination_node

    while True:
        routers.append(current_node)

        current_node = parent[current_node]

        if current_node is None:
            # got to the finish
            break

    return list(reversed(routers))


def find_closest_node(nodes: Nodes, distances: dict[Node, int]) -> Node:
    if len(nodes) < 1:
        return None

    shortest_distance = math.inf
    closest_node = None

    for node in nodes:
        if distances[node] < shortest_distance:
            closest_node = node
            shortest_distance = distances[node]

    return closest_node


# ------------------------------
# DO NOT MODIFY BELOW THIS LINE
# ------------------------------
def read_routers(file_name):
    with open(file_name) as fp:
        data = fp.read()

    return json.loads(data)


def find_routes(routers, src_dest_pairs):
    for src_ip, dest_ip in src_dest_pairs:
        path = dijkstras_shortest_path(routers, src_ip, dest_ip)
        print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")


def usage():
    print("usage: dijkstra.py infile.json", file=sys.stderr)


def main(argv):
    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
