#include "db_handler.h"
#include <iostream>

DBHandler::DBHandler(const std::string& db_path) : db_path_(db_path), db_(nullptr) {}

DBHandler::~DBHandler() {
    disconnect();
}

bool DBHandler::connect() {
    int rc = sqlite3_open(db_path_.c_str(), &db_);
    if (rc) {
        std::cerr << "Can't open database: " << sqlite3_errmsg(db_) << "\n";
        return false;
    }
    std::cout << "Opened database successfully\n";
    return true;
}

void DBHandler::disconnect() {
    if (db_) {
        sqlite3_close(db_);
        db_ = nullptr;
    }
}

std::vector<SignalNode> DBHandler::fetchAllSignals() {
    std::vector<SignalNode> signals;
    const char* sql = "SELECT id, source, domain, content, confidence, timestamp FROM Signals;";
    sqlite3_stmt* stmt;

    int rc = sqlite3_prepare_v2(db_, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        std::cerr << "Failed to fetch signals: " << sqlite3_errmsg(db_) << "\n";
        return signals;
    }

    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        SignalNode node;
        node.id = sqlite3_column_int(stmt, 0);
        node.source = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        node.domain = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
        node.content = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
        node.confidence = sqlite3_column_double(stmt, 4);
        node.timestamp = sqlite3_column_int64(stmt, 5);
        signals.push_back(node);
    }

    sqlite3_finalize(stmt);
    return signals;
}
