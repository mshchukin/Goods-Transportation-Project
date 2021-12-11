// Graph generator - Testing Environment by Mikhail Shchukin (c) 2019
// Compiles in Visual Studio Express 2012
// Requires C++11 support compile flags if compiled on older UNIX/Linux environments

#include <vector>
#include <string>
#include <time.h>
#include <math.h>
#include <iostream>
#include <fstream>
#include <random>
#include <string>



using namespace std;

// seed the PRNG
random_device rd;
mt19937 mt(rd());
uniform_real_distribution<double> dist(0.0, RAND_MAX);

// a flag that determines the format of the output file 
// false = simple-text format for further processing
// true = GraphViz format to export graph as picture later 
const bool saveGraphForm = true;

// a flag that determines if the console output is needed
// false = no results are displayed after generation - works faster
// true = results are being shown in console for each node/edge - might work exceptionally slow with bigger graphs
const bool displayResults = true;

// the default square km size of the map
const float MAX_MAP_SIZE = 1000.0;

// a custom function to generate pseudorandom floats between MIN and MAX
// note: this can be easily type-casted like "(int)rnd_num(x,y)" to integers with float part truncated
float rnd_num(float MIN, float MAX){
	return MIN + (float)(dist(mt)) /( (float) (RAND_MAX/(MAX - MIN))); // pseurandom enough to work
}

// function to do a flip of the coin - yes or no? - one or zero will know
bool coinflip(){
	if (rnd_num(0.0,1.0) > 0.5) {
		return true;
	} else {
		return false;
	}
}

// movement graph data structures
struct edge { 
int dest_id; // edge destination node id
float distance; // distance to travel
int time; // time to spend on travel
};

struct node {
int id;
int type; // 0 - joint; 1 - store; 2 - warehouse
vector<int> supply;
vector<int> demand;
float x,y; // node coordinates
vector<edge> edges; // storage for edges of the node
bool hasSpreadEdges; // flag to check if the node yet tried to edges
};

vector<node> nodes;

int main() {
	cout << "Shipping roadmap graph generator by Mikhail Shchukin." << endl;

	cout << "Please enter the number of nodes to generate: " ;
	int max_nodes;
	cin >> max_nodes;

	if (max_nodes < 2) { 
		cout << "Hey, you will then have a useless graph with no edges." << endl;
		return 1; // stop the program and go cry		
	}

	cout << "Please enter the maximum number of edges to spawn per node: " ;
	int max_edges_per_node;
	cin >> max_edges_per_node;

	if (max_edges_per_node < 1) {
		cout << "Hey, you will then have no edges at all." << endl;
		return 1; // stop the program and go cry		
	}

	if (max_edges_per_node > max_nodes - 1) {
		cout << "Hey, you will then have too many edges." << endl;
		return 1; // stop the program and go cry		
	}

	cout << "How many stores would you like to have on the map?: " ;
	int max_stores;
	cin >> max_stores;

	if (max_stores < 1) { 
		cout << "Hey, will then have no stores at all." << endl;
		return 1; // stop the program and go cry		
	}

	cout << "How many warehouses would you like to have on the map?: " ;
	int max_warehouses;
	cin >> max_warehouses;

	if (max_warehouses < 1) { 
		cout << "Hey, will then have no warehouses at all." << endl;
		return 1; // stop the program and go cry		
	}

	if (max_stores + max_warehouses > max_nodes) {
		cout << "Hey, you want more warehouses/stores than the number of nodes to be generated." << endl;
		return 1; // stop the program and go cry
	}

	int good_types;
	cout << "How many types of goods would you have?: " ;
	cin >> good_types;
	if (good_types < 1) { 
		cout << "Hey, will then have no goods at all." << endl;
		return 1; // stop the program and go cry		
	}

	// ask the total number of goods supplied/demanded
	vector<int> supply;
	vector<int> demand;
	int total = 0;
	for (int i=0; i<good_types; i++){
		cout << "What is the total number of goods of type [" << i+1 << "] supplied by warehouses?: ";
		int buff;
		cin >> buff;
		supply.push_back(buff); // load this type of good's total supply
		cout << "What is the total number of goods of type [" << i+1 << "] demanded by stores?: ";
		cin >> buff;
		demand.push_back(buff); // load this type of good's total demand
	}

	cout << "Okay, I am going to generate the shipping roadmap graph now. Hold on tight." << endl;

	// create the requested number of nodes
	for (int i=0; i<max_nodes; i++){
		node n; //dummy node for reusage in loop
		n.id = i; // assign node id
		n.type = 0; // during initial placement - all nodes are type 0, joints. may be converted into stores/warehouses later
		n.hasSpreadEdges = false; // all new-born nodes will have to produce edges
		// assign random node coordinates
		n.x = rnd_num(0.0,MAX_MAP_SIZE);
		n.y = rnd_num(0.0,MAX_MAP_SIZE);
		for (int i=0; i<good_types; i++){ // initialize the arrays
			n.supply.push_back(0);
			n.demand.push_back(0);
		}
		nodes.push_back(n); // load the created node into the global storage
	}

	// now turn random joint nodes into stores and warehouses
	vector<int> store_ids;
	vector<int> warehouse_ids;
	// create stores
	for (int i=0; i<max_stores; i++){
		int replacement_node_id = (int)rnd_num(0.0,(float)nodes.size()); // pick any node id
		int dummy = 0;
		do {
			replacement_node_id = (int)rnd_num(0.0,(float)nodes.size()); // pick any node id again
		} while (nodes[replacement_node_id].type > 0); // re-roll the loop if a non-joint node was selected for replacement
		store_ids.push_back(replacement_node_id); // record the store id
		nodes[replacement_node_id].type = 1; // replace this joint with a store
	}
	// create warehouses
	for (int i=0; i<max_warehouses; i++){
		int replacement_node_id = (int)rnd_num(0.0,(float)nodes.size()); // pick any node id
		int dummy = 0;
		do {
			replacement_node_id = (int)rnd_num(0.0,(float)nodes.size()); // pick any node id again
		} while (nodes[replacement_node_id].type > 0); // re-roll the loop if a non-joint node was selected for replacement
		warehouse_ids.push_back(replacement_node_id); // record the store id
		nodes[replacement_node_id].type = 2; // replace this joint with a warehouse
	}

	// load the shipping problem parameters
	for (int i=0; i<good_types; i++){
		// fill warehouses with goods
		while (supply[i] > 0) {
			for (unsigned int w=0; w<warehouse_ids.size(); w++){
				if (supply[i] != 0){ // if any supply left
					nodes[warehouse_ids[w]].supply[i] += 1; // load good to warehouse
					supply[i]--; // reduce remaining supply of that type by 1
				}
			}		
		}

		while (demand[i] > 0){
			// set the demands of each store
			for (unsigned int s=0; s<store_ids.size(); s++){
				if (demand[i] != 0){ // if any demand left
					nodes[store_ids[s]].demand[i] += 1; // load good to warehouse
					demand[i]--; // reduce remaining supply of that type by 1
				}	
			}		
		}
	
	}

	// once the nodes have been created, let's create the edges between them
	for (unsigned int i=0; i<nodes.size(); i++){
		for (int e=0; e<max_edges_per_node; e++){
			if (coinflip()) {
				edge e; //dummy edge for reusage in loop
				// pick the destination node
				while (true) {
					e.dest_id = (int)rnd_num(0.0,(float)nodes.size()); // pick any node id
					if (e.dest_id != i){ // for any edge: destination != source
						break;
					}
				} // re-roll the loop if edge source and destination nodes are the same
				// generate edge distance
				e.distance = sqrtf(powf(nodes[i].x - nodes[e.dest_id].x, 2) + powf(nodes[i].y - nodes[e.dest_id].y, 2));
				// generate edge time
				float assumed_velocity = rnd_num(40.0,100.0); // pick the assumed average velocity (km/h) allowed for this edge
				e.time = (int)((e.distance / assumed_velocity) * 60); // for now - let it be minutes of transition
				nodes[i].edges.push_back(e); // record the edge to the node
			}
		}
		if (nodes[i].edges.size() == 0) { // if the loop above generated no edges - just generate at least one to keep graph connected
			edge e; //dummy edge for reusage in loop
			// pick the destination node
			while (true) {
				e.dest_id = (int)rnd_num(0.0,(float)nodes.size()); // pick any node id
				if (e.dest_id != i){ // for any edge: destination != source
					break;
				}
			} // re-roll the loop if edge source and destination nodes are the same
			// generate edge distance
			e.distance = sqrtf(powf(nodes[i].x - nodes[e.dest_id].x, 2) + powf(nodes[i].y - nodes[e.dest_id].y, 2));
			// generate edge time
			float assumed_velocity = rnd_num(40.0,100.0); // pick the assumed average velocity (km/h) allowed for this edge
			e.time = (int)((e.distance / assumed_velocity) * 60); // for now - let it be minutes of transition
			nodes[i].edges.push_back(e); // record the edge to the node
		}
		nodes[i].hasSpreadEdges = true; // this node has produced nodes, toggle the flag
	}

	// display the results and save them to file
	ofstream graph;
	graph.open("graph.txt");

	// GraphViz needs some header information to know that this graph is undirected
	if (saveGraphForm){
		graph << "graph G {" << endl;
	}

	cout << "The shipping roadmap graph has been constructed." << endl;
	for (unsigned int i=0; i<nodes.size(); i++){
		string nodeType = "";
		
		// display node type
		if (displayResults){
			cout << "Node [" << nodes[i].id << "]";
			switch(nodes[i].type){
			case 0:
				cout << " is a JOINT" << endl;
				nodeType = "J";
				break;
			case 1:
				cout << " is a STORE" << endl;
				nodeType = "S";
				break;
			case 2:
				cout << " is a WAREHOUSE" << endl;
				nodeType = "W";
				break;
			}		
		}

		if (saveGraphForm){
			graph << "\"" << nodes[i].id << "\" [label=\"" << nodes[i].id << " " << nodeType << "\", type=" << nodes[i].type <<  ", supply=" << nodes[i].supply[0] << ", demand=" << nodes[i].demand[0] << "]" << endl;
		}
		
		
		// display edges of current node
		for (unsigned int k=0; k<nodes[i].edges.size(); k++){
			if (displayResults){
				cout << "> Edge between nodes [" << nodes[i].id << "] and [" << nodes[i].edges[k].dest_id << "]" << endl;
				cout << ">> Distance: " << nodes[i].edges[k].distance << "; Time to traverse: " << nodes[i].edges[k].time << endl;			
			}

			// save to file in GraphViz syntax
			// nodes[i].id
			if (saveGraphForm){
				graph << '"' << nodes[i].id << "\"--\"" << nodes[i].edges[k].dest_id << "\"[label=\"" << " d = " << nodes[i].edges[k].distance << "\\n" << " t = " << nodes[i].edges[k].time << "\", distance=" << nodes[i].edges[k].distance << ", time=" << nodes[i].edges[k].time  << "]"<< endl;
			}

		}

	}

	// GraphViz undirected graph is done, closing it with final bracket
	if (saveGraphForm){
		graph << "}";
	}
	// close the file - saving is done
	graph.close();

return 0; // quit program
}
