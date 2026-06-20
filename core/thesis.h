#ifndef THESIS_H
#define THESIS_H

#include <string>
#include <vector>
#include <unordered_map>

struct Assumption {
    int id;
    int thesis_id;
    std::string description;
    bool active;
    std::vector<int> dependent_theses; // IDs of theses that depend on this
};

struct Thesis {
    int id;
    std::string description;
    std::string status;
    double confidence;
    std::vector<int> assumption_ids;
};

class ThesisRegistry {
public:
    ThesisRegistry();
    ~ThesisRegistry();

    void addThesis(const Thesis& thesis);
    void addAssumption(const Assumption& assumption);

    // Core 2nd-order logic: propagates invalidation through the DAG
    void propagateInvalidation(int assumption_id);

    void printRegistry() const;

private:
    std::unordered_map<int, Thesis> theses_;
    std::unordered_map<int, Assumption> assumptions_;
};

#endif // THESIS_H
