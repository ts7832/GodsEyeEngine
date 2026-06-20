#ifndef DB_HANDLER_H
#define DB_HANDLER_H

#include <sqlite3.h>
#include <string>
#include <vector>
#include <iostream>

struct SignalNode {
    int id;
    std::string source;
    std::string domain;
    std::string content;
    double confidence;
    long long timestamp;
};

class DBHandler {
public:
    DBHandler(const std::string& db_path);
    ~DBHandler();

    bool connect();
    void disconnect();

    // Fetch all signals
    std::vector<SignalNode> fetchAllSignals();
    
    // Additional methods will be added here (insert signal, fetch theses, etc.)

private:
    std::string db_path_;
    sqlite3* db_;
};

#endif // DB_HANDLER_H
