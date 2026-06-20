#ifndef GRAPH_H
#define GRAPH_H

#include "db_handler.h"
#include <unordered_map>
#include <vector>

class SignalGraph {
public:
    SignalGraph();
    ~SignalGraph();

    // Adds a signal node to the graph
    void addNode(const SignalNode& node);
    
    // Adds a directional edge (relationship) between two signals
    void addEdge(int from_id, int to_id);
    
    // Prints the graph for debugging
    void printGraph() const;

private:
    std::unordered_map<int, SignalNode> nodes_;
    std::unordered_map<int, std::vector<int>> adjacency_list_;
};

#endif // GRAPH_H
