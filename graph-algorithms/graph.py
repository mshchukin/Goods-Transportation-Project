import networkx as nx 
import re

def import_graph_from(graph, path=None):

    with open(path) as inputfile:
        print("Reading .dot >>>>>>>>>>>>>")
        for line in inputfile:
            print(line)
            
            # --- A node
            regex_node = re.findall("^\"[0-9]*\"\ ", line)
            if regex_node:
                # Get node id
                node_id = int(regex_node[0].replace("\"", " ").strip())
                # Get node parameters
                regex_para_node = re.findall(r"\[.*\]", line)
                if regex_para_node:
                    # "0" [label="0WAREHOUSE", type=2, supply=6, demand=0]
                    str_params = regex_para_node[0].replace("["," ").replace("]", " ").strip().split(",")
    
                    node_label = ""
                    node_type = -1
                    node_demand = -1
                    node_supply = -1
                    for param in str_params:
                        param_key_value = param.strip().split("=")
                        if param_key_value[0] == "label":
                            node_label = param_key_value[1] + ": "
                        elif param_key_value[0] == "type":
                            node_type = int(param_key_value[1])
                        elif param_key_value[0] == "supply":
                            node_supply = int(param_key_value[1])
                        elif param_key_value[0] == "demand":
                            node_demand = int(param_key_value[1])

                    graph.add_node(node_id, label = node_label, type = node_type, supply = node_supply, demand=node_demand)
                else:
                    raise Exception("Error while converting Node params")

            # --- An edge
            regex_edge = re.findall("^\"[0-9]*\"--\"[0-9]*", line)
            if regex_edge:
                # Get edge ids
                ids = regex_edge[0].replace("\"", " ").strip().split(" -- ")
                node_id1 = int(ids[0])
                node_id2 = int(ids[1])
                # Get edge parameters
                regex_para_edge = re.findall(r"\[.*\]", line)
                if regex_para_edge:
                    # "0"--"8"[label=" d = 435.738\n t = 112", distance=435.738, time=112]
                    str_params = regex_para_edge[0].replace("["," ").replace("]"," ").strip().split(",")
                    edge_label = ""
                    edge_dist = -1
                    edge_time = -1
                
                    for param in str_params:
                        
                        param_key_value = param.strip().split("=")
                        if param_key_value[0] == "label":
                            edge_label = param_key_value[1] + param_key_value[2] + param_key_value[3]
                        elif param_key_value[0] == "distance":
                            edge_dist = float(param_key_value[1])
                        elif param_key_value[0] == "time":
                            edge_time = float(param_key_value[1])

                        edge_label = "cost: {}".format(edge_simple_cost(edge_dist,edge_time))
                        graph.add_edge(node_id1, node_id2, label=edge_label, cost= edge_simple_cost(edge_dist,edge_time) )
                else:
                    raise Exception("Error while converting Edge params")
    
# print the graph nodes or edges
def print_graph(graph, nodes_dict, out_nodes=True, out_edges=True):
    if out_nodes:
        for node in graph.nodes():
            print("node:", nodes_dict[node]['label'], " type: ", nodes_dict[node]['type'], " suppy : ", nodes_dict[node]['supply'], " demand: ", nodes_dict[node]['demand'])

    if out_edges:
        for edge in graph.edges():
            print("edge:", edge, " d: ",  graph[edge[0]][edge[1]]['distance'], " t: ", graph[edge[0]][edge[1]]['time'])

def get_all_nodes_dict(graph):
    return dict(graph.nodes())

def get_all_edges_dict(graph):
    return dict(graph.edges())

def get_warehouses(graph, print_warehouse_info=False):
    # returns lists of: warehouses ids and supplies
    warehouses_ids_list = []
    warehouses_supplies_list  = []

    nodes_dict = get_all_nodes_dict(graph)
    
    for node_id in nodes_dict.keys():
        # Warehouse
        if nodes_dict[node_id]['type'] == 2:
            if print_warehouse_info:
                print("warehouse: " , node_id, "  supply: ", nodes_dict[node_id]['supply'])

            warehouses_ids_list.append(node_id)
            warehouses_supplies_list.append(nodes_dict[node_id]['supply'])

    return warehouses_ids_list, warehouses_supplies_list

def get_stores(graph, print_store_info=False):
    # returns lists of: store ids and demands
    stores_ids_list = []
    stores_demand_list  = []

    nodes_dict = get_all_nodes_dict(graph)
    
    for node_id in nodes_dict.keys():
        # Store
        if nodes_dict[node_id]['type'] == 1:
            if print_store_info:
                print("store: " , node_id, "  demand: ", nodes_dict[node_id]['demand'])

            stores_ids_list.append(node_id)
            stores_demand_list.append(nodes_dict[node_id]['demand'])

    return stores_ids_list, stores_demand_list

def edge_simple_cost(distance, time):
    return distance + time


def get_edges(graph, print_edge_info=False):
    # returns lists of: tuples (node_id1, node_id2), distance, time, edge cost,
    edges_tuples_list = []
    edges_dist_list =[]
    edges_time_list =[]
    edges_cost_list = [] 

    edges_dict = get_all_edges_dict(graph)
    
    # for n1_id, n2_id in edges_dict.keys():
    for edge in edges_dict.keys():
        edges_tuples_list.append(edge)
        edge_dist = edges_dict[edge]['distance']
        edge_time = edges_dict[edge]['time']
        if print_edge_info:
            print("edge: ", edge, "  dist:", edge_dist, "  time:", edge_time)
        
        edges_dist_list.append(edge_dist)
        edges_time_list.append(edge_time)
        # compute cost
        edges_cost_list.append(edge_simple_cost(edge_dist,edge_time))

    return edges_tuples_list, edges_dist_list, edges_time_list, edges_cost_list 


def write_graph(graph):
    print("Graph")
    
    # # Nodes dict: keys are the int node_id: 0, value is a dict with nodes properties
    nodes_dict = get_all_nodes_dict(graph)
    print("nodes_dict: ", len(nodes_dict))
    # # Edges dict: keys are tuples with nodes ids: (0, 1), value is a dict with edge properties
    edges_dict = get_all_edges_dict(graph)
    print("edges_dict: ", len(edges_dict))

    warehouses_ids_list, warehouses_supplies_list = get_warehouses(graph)
    print("warehouses_ids_list: ", warehouses_ids_list)
    print("warehouses_supplies_list: ", warehouses_supplies_list)
    
    stores_ids_list, stores_demand_list = get_stores(graph)
    print("stores_ids_list: ", stores_ids_list)
    print("stores_demand_list: ", stores_demand_list)

if __name__ == "__main__":
    graph = nx.Graph()

    import_graph_from(graph=graph, path="../graph-generator/graph1.txt")
    
    print(list(graph.edges()))
    print(list(graph.nodes()))
    write_graph(graph)

