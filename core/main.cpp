#include <iostream>
#include "db_handler.h"
#include "graph.h"
#include "thesis.h"

int main() {
    std::cout << "Initializing God's Eye Engine (Core Daemon)...\n";

    // Initialize DB Connection
    DBHandler db("../godseye.db");
    if (!db.connect()) {
        return 1;
    }

    // Initialize the Graph and Thesis Registry
    SignalGraph graph;
    ThesisRegistry registry;

    // --- Simulated Demo for Testing ---
    std::cout << "\n[1] Setting up simulated environment...\n";

    // Create a mock thesis
    Thesis t1 = {1, "Long US Equities due to loose monetary policy", "ACTIVE", 0.8, {101}};
    registry.addThesis(t1);

    // Create a mock assumption that t1 depends on
    Assumption a1 = {101, 1, "Federal Reserve will cut rates in Q4", true, {1}};
    registry.addAssumption(a1);

    registry.printRegistry();

    // Simulate an event that breaks the assumption
    std::cout << "\n[2] Simulating incoming signal: High Inflation Print...\n";
    std::cout << "Signal suggests rates will NOT be cut.\n";
    
    // Trigger the cascade
    registry.propagateInvalidation(101);

    std::cout << "\n[3] Post-Event State:\n";
    registry.printRegistry();

    // Wait and listen (mock loop)
    std::cout << "\nDaemon running. Waiting for real signals (Ctrl+C to exit)...\n";
    
    // In a real system, this would be an infinite loop periodically checking SQLite
    // while (true) {
    //    sleep(10);
    //    poll_db();
    // }

    db.disconnect();
    return 0;
}
