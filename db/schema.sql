-- God's Eye Engine V1 - SQLite Schema

-- Signals: The raw data points collected from scrapers (news, macro, social)
CREATE TABLE IF NOT EXISTS Signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,       -- e.g., 'FRED', 'Twitter', 'Substack'
    domain TEXT NOT NULL,       -- e.g., 'macro', 'geopolitical', 'social'
    content TEXT NOT NULL,      -- The actual insight, metric, or headline
    timestamp INTEGER NOT NULL, -- Unix epoch time
    confidence REAL DEFAULT 0.5 -- 0.0 to 1.0 (how reliable is the source)
);

-- SignalEdges: Represents the Adjacency List (Graph) of connected signals
CREATE TABLE IF NOT EXISTS SignalEdges (
    from_id INTEGER NOT NULL,
    to_id INTEGER NOT NULL,
    relationship_type TEXT,     -- e.g., 'correlates', 'contradicts', 'temporal'
    FOREIGN KEY(from_id) REFERENCES Signals(id),
    FOREIGN KEY(to_id) REFERENCES Signals(id),
    PRIMARY KEY (from_id, to_id)
);

-- Theses: The high-level beliefs or investment ideas
CREATE TABLE IF NOT EXISTS Theses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE', -- 'ACTIVE', 'FLAGGED', 'INVALIDATED'
    confidence REAL DEFAULT 0.5,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

-- Assumptions: The Directed Acyclic Graph (DAG) dependencies for each Thesis
CREATE TABLE IF NOT EXISTS Assumptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thesis_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,     -- 1 if valid, 0 if invalidated by a signal
    FOREIGN KEY(thesis_id) REFERENCES Theses(id)
);

-- CIO_Feedback: The memory layer / feedback-weighted RAG system
CREATE TABLE IF NOT EXISTS CIO_Feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thesis_id INTEGER,            -- Can be NULL if general feedback
    feedback_text TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    FOREIGN KEY(thesis_id) REFERENCES Theses(id)
);

-- ThesisSignals: The memory bridge connecting raw intel signals to the final thesis
CREATE TABLE IF NOT EXISTS ThesisSignals (
    thesis_id INTEGER NOT NULL,
    signal_id INTEGER NOT NULL,
    FOREIGN KEY(thesis_id) REFERENCES Theses(id),
    FOREIGN KEY(signal_id) REFERENCES Signals(id),
    PRIMARY KEY (thesis_id, signal_id)
);
