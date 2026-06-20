#include "graph.h"
#include <iostream>

SignalGraph::SignalGraph() {}

SignalGraph::~SignalGraph() {}

void SignalGraph::addNode(const SignalNode& node) {
    nodes_[node.id] = node;
    // Ensure an entry in the adjacency list exists even if it has no edges initially
    if (adjacency_list_.find(node.id) == adjacency_list_.end()) {
        adjacency_list_[node.id] = std::vector<int>();
    }
}

void SignalGraph::addEdge(int from_id, int to_id) {
    if (nodes_.find(from_id) != nodes_.end() && nodes_.find(to_id) != nodes_.end()) {
        adjacency_list_[from_id].push_back(to_id);
    } else {
        std::cerr << "Warning: Attempted to add edge between non-existent nodes (" 
                  << from_id << " -> " << to_id << ")\n";
    }
}

void SignalGraph::printGraph() const {
    std::cout << "--- Signal Graph ---\n";
    for (const auto& pair : adjacency_list_) {
        int node_id = pair.first;
        std::cout << "Node " << node_id << " (" << nodes_.at(node_id).domain << ") connects to: ";
        for (int connected_id : pair.second) {
            std::cout << connected_id << " ";
        }
        std::cout << "\n";
    }
    std::cout << "--------------------\n";
}
