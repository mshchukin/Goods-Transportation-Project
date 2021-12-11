# cs820-project
CS820 Artificial Intelligence Group Project repository.

The `graph-generator` folder contains the code related to roadmap graph generation, that involves saving the resulting graph in a formatted `.txt`file.

The `graph-algorithms` folder the code related to processing the graphs generated in the form of the `.txt' files. The algorithm(s) will read the graph structure, determine the best way to solve the shipping problem on it (i.e. maximizing and/or equalizing the amount of goods delivered + minimizing the overall costs of shipping), and then the results will be displayed to the console and/or saved to another '.txt' formatted file.

Algorith Description
-----------

1. The program stores in a networkx graph the information imported from a .txt file created by the generator. The file name is passed using the paramenter `input-dot-graph`.

2. The truck load capacity should be informed, as well as the initial conditions: 

* `truck-cap-max`: an integer which represents the truck load capacity

* `truck-initial-load`: an integer with the number of goods already in the truck

* `truck-start-node`: an integer which is the node id where the truck starts 

3. The algorithm proposed tries to return a path in the graph which represents the sequence of nodes the truck visited. 

The algorithm seeks to decide if the truck either goes to a warehouse or a store. 

This decision is based on a threshold(`load-threshold-factor`) for the current truck load. If it is above the threshold, the decision is to go to the store with the COSTLESS path and which still have demand.

On the other hand, if the current truck load is bellow the threshold, the decision is to go to the warehouse with the COSTLESS path and which still have goods to supply.


# Example to run:
>>> python run_truck_path_search.py --name goto_warehouse_or_store --input_dot_graph graph --truck_cap_max 6 --truck-start-node 0 --truck-initial-load 0 --load-threshold-factor 0.5