#include "thesis.h"
#include <iostream>

ThesisRegistry::ThesisRegistry() {}
ThesisRegistry::~ThesisRegistry() {}

void ThesisRegistry::addThesis(const Thesis& thesis) {
    theses_[thesis.id] = thesis;
}

void ThesisRegistry::addAssumption(const Assumption& assumption) {
    assumptions_[assumption.id] = assumption;
}

void ThesisRegistry::propagateInvalidation(int assumption_id) {
    if (assumptions_.find(assumption_id) == assumptions_.end()) {
        std::cerr << "Assumption " << assumption_id << " not found.\n";
        return;
    }

    // Mark the assumption as invalidated
    assumptions_[assumption_id].active = false;
    std::cout << ">>> INVALDATION EVENT: Assumption " << assumption_id 
              << " ('" << assumptions_[assumption_id].description << "') has been invalidated.\n";

    // Cascade: Invalidate or flag dependent theses
    for (int thesis_id : assumptions_[assumption_id].dependent_theses) {
        if (theses_.find(thesis_id) != theses_.end()) {
            theses_[thesis_id].status = "FLAGGED";
            theses_[thesis_id].confidence *= 0.5; // Halve the confidence
            std::cout << ">>> CASCADE: Thesis " << thesis_id 
                      << " ('" << theses_[thesis_id].description << "') FLAGGED for CIO review. Confidence dropped to " 
                      << theses_[thesis_id].confidence << "\n";
        }
    }
}

void ThesisRegistry::printRegistry() const {
    std::cout << "--- Thesis Registry ---\n";
    for (const auto& pair : theses_) {
        std::cout << "Thesis " << pair.first << ": " << pair.second.description 
                  << " [Status: " << pair.second.status << ", Confidence: " << pair.second.confidence << "]\n";
    }
    std::cout << "-----------------------\n";
}
