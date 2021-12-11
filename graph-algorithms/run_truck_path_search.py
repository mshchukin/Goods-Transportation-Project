"""
Description
-----------

Dependencies:
- python 3.6.4 
- networkx 2.1

1. This program stores in a networkx graph the information imported from a .txt file created by the generator. The file name is passed using the paramenter 'input-dot-graph'.

2. The truck load capacity should be informed, as well as the initial conditions: 

'truck-cap-max': an integer which represents the truck load capacity
'truck-initial-load': an integer with the number of goods already in the truck
'truck-start-node': an integer which is the node id where the truck starts 

3. The algorithm proposed tries to return a path in the graph which represents the sequence of nodes the truck visited. 

The algorithm seeks to decide if the truck either goes to a warehouse or a store. 

This decision is based on a threshold(load-threshold-factor) for the current truck load. If it is above the threshold, the decision is to go to the store with the path with the least cost and which still have demand.

On the other hand, if the current truck load is bellow the threshold, the decision is to go to the warehouse with the path with the least cost and which still have goods to supply.


# Example to run:

>>> python run_truck_path_search.py --name goto_warehouse_or_store --input_dot_graph graph --truck_cap_max 6 --truck-start-node 0 --truck-initial-load 0 --load-threshold-factor 0.5 --log-alg

"""

import networkx as nx
from graph import import_graph_from, get_stores, get_warehouses
from utilities import TicTac

import copy 

import datetime
import argparse

INF = 9999999999999999999

# # Execution arguments
parser = argparse.ArgumentParser()
parser.add_argument('--name', type=str,
                    help="A name for the experiment.")

# Input Graph from .txt file
parser.add_argument('--input_dot_graph', type=str,
                    help="The .txt file in dot format containig the graph.")

# --- Specific problem parameters
parser.add_argument('--truck_cap_max', type=int, default=1,
                    help="truck load max capacity.")

# --- Initial state parameters
parser.add_argument('--truck-start-node', type=int,
                    help="Truck start node.")                    
parser.add_argument('--truck-initial-load', type=int, default=0,
                    help="Truck initial load.")

# --- Algorithms parameters
parser.add_argument('--load-threshold-factor', type=float, default=0.5,
                    help="For the greedy algorithm which decides to either go to a warehouse or a store, the load threshold factor.")  

# --- Logger parameters
parser.add_argument('--log-alg', action='store_true',
                    help="Print or not algorithm steps.")    

args = parser.parse_args()
_exp_name = args.name
_truck_cap_max = args.truck_cap_max
_load_threshold_factor = args.load_threshold_factor
_truck_initial_load = args.truck_initial_load
_truck_start_node = args.truck_start_node
_input_dot_graph = args.input_dot_graph
_load_threshold = _load_threshold_factor* _truck_cap_max
_log_alg = args.log_alg

# EXPERIMENT SETUP
timers = TicTac()
# Start global timer
timers.tic()

# networkx graph object
graph = nx.Graph()

# --- Import graph from text file created by the generator
import_graph_from(graph=graph, path="../graph-generator/{}.txt".format(_input_dot_graph))

# Logging the algorithm 
save_path_algo = open("{:%Y_%m_%d__%H_%M}_alg_log.txt".format(datetime.datetime.now()),"w+")

# START
truck_curr_node = _truck_start_node
truck_curr_load = _truck_initial_load

list_paths = []
_, store_demand_list = get_stores(graph)
_, warehouse_supply_list = get_warehouses(graph)
# total demand and supplies
tot_dem = sum(store_demand_list)
tot_sup = sum(warehouse_supply_list)

iteration = 0
while sum(store_demand_list) != 0 and (truck_curr_load + sum(warehouse_supply_list)) != 0:
    path_to_go = []
    
    iteration +=1
    if _log_alg:
        save_path_algo.write("\n----------- Iteration {}: Truck at node {}\nCurrent STATUS:\nTotal Demand: {}/{}  Demand list: {}\nTotal Supply: {}/{}  Supply list: {}\nTruck Current Load: {}/{}\n\n".format(iteration, truck_curr_node, sum(store_demand_list), tot_dem, store_demand_list, sum(warehouse_supply_list), tot_sup, warehouse_supply_list, truck_curr_load, _truck_cap_max))
    
    # go to the costless warehouse
    if truck_curr_load < _load_threshold:
        if _log_alg:
            save_path_algo.write("\n----- A) Decision: GOTO A WAREHOUSE, as the load {} is bellow the threshold {}:\n".format(truck_curr_load, _load_threshold))
        
        warehouses_ids_list, warehouse_supply_list = get_warehouses(graph)
        
        if _log_alg:
            save_path_algo.write("\n----- B) Searching the warehouse with the least path cost >>>\nSupplies list:{}\n".format(warehouse_supply_list))
        
        costless_warehouse_id = None
        costless_warehouse_cost = INF
        for ii in range(len(warehouses_ids_list)):
            warehouse_id = warehouses_ids_list[ii]
            warehouse_supply = warehouse_supply_list[ii]
            # print(warehouse_id, " ", warehouse_supply)
            
            if warehouse_supply > 0:
        
                curr_path = nx.shortest_path(graph,source=truck_curr_node,target=warehouse_id, weight="cost")
                curr_path_length = nx.shortest_path_length(graph,source=truck_curr_node,target=warehouse_id, weight="cost")
                if _log_alg: # log or not
                    save_path_algo.write("--- current W id: {}\n".format(warehouse_id))
                    save_path_algo.write("--- path to current W: {}\n".format(curr_path))
                    save_path_algo.write("--- path cost: {}\n\n".format(curr_path_length))
                if curr_path_length < costless_warehouse_cost:
                    costless_warehouse_cost = curr_path_length
                    costless_warehouse_id = warehouse_id
                    path_to_go = curr_path
                # save_path_algo.write("--- GOTO: costless warehouse to go: {}\n".format(costless_warehouse_id))
        if _log_alg:
            save_path_algo.write("******Final Decision:\nGOTO warehouse {}\n".format(costless_warehouse_id))
        # update supply of the store
        if not costless_warehouse_id == None:
            n_available_supplies = graph.nodes[costless_warehouse_id]["supply"]
            # print("n_available_supplies: ", n_available_supplies)
            # extra truck capacity, it will remain supplies
            if (n_available_supplies + truck_curr_load) > _truck_cap_max:
                truck_load_available = _truck_cap_max - truck_curr_load
                # update warehouse supplies
                graph.nodes[costless_warehouse_id]["supply"] -= truck_load_available
                if _log_alg:
                    save_path_algo.write("GET {} supplies from this warehouse\n\n".format(truck_load_available)) 
                # truck at full capacity
                truck_curr_load = _truck_cap_max
            elif (n_available_supplies + truck_curr_load) <= _truck_cap_max:
                remaining_supplies = _truck_cap_max - (n_available_supplies + truck_curr_load)
                # update warehouse supplies
                graph.nodes[costless_warehouse_id]["supply"] = 0
                if _log_alg:
                    save_path_algo.write("GET all supplies from this warehouse\n\n")
                # load truck with all the warehouse supplies 
                truck_curr_load = n_available_supplies + truck_curr_load
            else:
                raise Exception("Should not get into here.")
            
            truck_curr_node = costless_warehouse_id
            
            
    # go to the costless store
    elif truck_curr_load >= _load_threshold:
        if _log_alg:
            save_path_algo.write("\n----- A) Decision: GOTO A STORE, as the load {} is above the threshold {}:\n".format(truck_curr_load, _load_threshold))
        
        store_ids_list, store_demand_list = get_stores(graph)

        if _log_alg:
            save_path_algo.write("\n----- B) Searching the store with least path cost >>>\nDemand list:{}\n".format(store_demand_list))

        costless_store_id = None
        costless_store_cost = INF
        for ii in range(len(store_ids_list)):
            store_id = store_ids_list[ii]
            store_demand = store_demand_list[ii]
            # save_path_algo.write(store_id, " ", store_demand)
            
            # the store demand should be > 0
            if store_demand > 0:

                curr_path = nx.shortest_path(graph,source=truck_curr_node,target=store_id, weight="cost")
                curr_path_length = nx.shortest_path_length(graph,source=truck_curr_node,target=store_id, weight="cost")
                if _log_alg: # log or not
                    save_path_algo.write("--- current S id: {}\n".format(store_id))
                    save_path_algo.write("--- path to current S: {}\n".format(curr_path))
                    save_path_algo.write("--- path cost: {}\n\n".format(curr_path_length))
                if curr_path_length < costless_store_cost:
                    costless_store_cost = curr_path_length
                    costless_store_id = store_id
                    path_to_go = curr_path
                    
                # save_path_algo.write("--- GOTO: costless store to go: {}\n".format(costless_store_id))

        if _log_alg:
            save_path_algo.write("******Final Decision:\nGOTO store {}\n".format(costless_store_id))
        # update demand of the store
        if not costless_store_id == None:
            n_available_demand = graph.nodes[costless_store_id]["demand"]

            # truck has more than enough supplies for the store
            if truck_curr_load >= n_available_demand:
                # update store demand
                graph.nodes[costless_store_id]["demand"] = 0
                if _log_alg:
                    save_path_algo.write("SUPPLY the entire demand from this store\n\n") 
                # truck at full capacity
                truck_curr_load -= n_available_demand
            
            # supply the maximum the truck has
            elif truck_curr_load < n_available_demand:
                # update store demand
                graph.nodes[costless_store_id]["demand"] -= truck_curr_load
                if _log_alg:
                    save_path_algo.write("SUPPLY the store with the current truck load of {}\n\n".format(truck_curr_load)) 
                # load truck with all the warehouse supplies 
                truck_curr_load = 0
            else:
                raise Exception("Should not get into here.")
            
            truck_curr_node = costless_store_id

    # if a path from current node to a next one was found
    if path_to_go:
        list_paths.append(path_to_go)
    else:
        raise Exception("Can't reach node!!")
    
    # get stores demand list to check if there is still demand
    _, store_demand_list = get_stores(graph)
    # get warehouses supply list to check if there is still suplies left
    _, warehouse_supply_list = get_warehouses(graph)

save_path_algo.write("\n\n------------ Final State of global demand and supply:\n")
_, store_demand_list = get_stores(graph)
_, warehouse_supply_list = get_warehouses(graph)

save_path_algo.write("Remainging demand: {}\n".format(sum(store_demand_list)))
save_path_algo.write("Remainging supplies: {}\n".format(sum(warehouse_supply_list)))
save_path_algo.write("\n\n------------ Final State of global demand and supply\n")

exp_total_time = timers.tac()
save_path_algo.write("\nTotal time of the experiment:{}\n\n".format(exp_total_time))
save_path_algo.write("\nTruck started at node ({}) with initial load of ({}), and capacity of ({})\n".format(_truck_start_node,_truck_initial_load, _truck_cap_max))
save_path_algo.write("\nThe algorithm used a threshold factor of ({})\n".format(_load_threshold_factor))

save_path_algo.write("\nThe imported graph file name is '{}'\n".format(_input_dot_graph))


print("Computing the truck's path overall cost...")
over_cost = 0
for path in list_paths:
    for i in range(0,len(path)-1):
        # print("edge: {}, {}".format(path[i], path[i+1]))
        # print("cost: ", graph[path[i]][path[i+1]]['cost'])
        over_cost += graph[path[i]][path[i+1]]['cost']

save_path_algo.write("\nThe overall cost of the truck's path is: {}".format(over_cost))
save_path_algo.write("\nThe list of paths is: \n")
for path in list_paths:
    save_path_algo.write(str(path) + "\n")

# Closing file to log the algorithm
save_path_algo.close()


# --- Result path >>>>>>>>>>>>>>>
print("\n\nTruck path: \n{}\n\n".format(list_paths))
print("Experiment time: {} s".format(exp_total_time))

# --- Save path to .txt file
save_folder = "{:%Y_%m_%d__%H_%M}_{}.txt".format(datetime.datetime.now(), _exp_name)
save_path_found = open(save_folder,"w+")
print("Path saved to text file: ", save_folder)

save_path_found.write("Truck started node: {}\nTruck initial load: {}\nTruck max capacity: {}\n".format(_truck_start_node,_truck_initial_load, _truck_cap_max))
save_path_found.write("\nThe algorithm used a threshold factor of ({})\n".format(_load_threshold_factor))

save_path_found.write("Truck path overall cost: " + str(over_cost) + "\n")
for path in list_paths:
    save_path_found.write(str(path) + "\n")
save_path_found.close()

# --- Save .dot file with truck path
node_counter = 0
graph_to_save = copy.copy(graph)
for path in list_paths:
    for node_id in path:
        graph_to_save.nodes[node_id]["label"] += "{}, ".format(node_counter)
        node_counter+=1

nx.drawing.nx_pydot.write_dot(graph_to_save, "{}.dot".format(save_folder.replace(".txt","")))
print("Generated graph .dot file with the sequence of nodes the truck should go: \n {}".format(save_folder))