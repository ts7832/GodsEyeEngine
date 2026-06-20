import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../godseye.db")

class CIOFeedbackRAG:
    def __init__(self):
        self.db_path = DB_PATH
        
    def get_relevant_feedback(self, context_keywords=None):
        """
        In a full implementation, this uses embeddings to do a vector search 
        against the CIO_Feedback table.
        For V1, we pull recent feedback to inject into the LLM context.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Pull recent feedback, limit 10
        try:
            cursor.execute("SELECT feedback_text FROM CIO_Feedback ORDER BY timestamp DESC LIMIT 10")
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            # Table might be empty or locked
            rows = []
        finally:
            conn.close()
        
        feedback_list = [row[0] for row in rows]
        
        if not feedback_list:
            return "No previous CIO feedback."
            
        return "\n".join(f"- {fb}" for fb in feedback_list)
        
    def add_feedback(self, text, thesis_id=None):
        import time
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CIO_Feedback (thesis_id, feedback_text, timestamp)
            VALUES (?, ?, ?)
        """, (thesis_id, text, int(time.time())))
        conn.commit()
        conn.close()
