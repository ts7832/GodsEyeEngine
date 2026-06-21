import os
import json
import time
import sqlite3
import re
from rag_memory import CIOFeedbackRAG

try:
    import google.generativeai as genai
except ImportError:
    genai = None

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'godseye.db'))

BURRY_FRAMEWORK = """
MICHAEL BURRY FRAMEWORK (Contrarian Value & Capitulation):
Find forced stupidity, hated value, tangible book, and capitulation.
- Look for "emotional exhaustion" and high volume turnover (capitulation).
- Is Tangible Book Value growing? Is the balance sheet strong?
- Is it hated by Wall Street (poor analyst ratings)?
- Ignore "cheap" if it's dying. We want cheap + hated + solvent.
"""

BUFFETT_FRAMEWORK = """
WARREN BUFFETT / CHARLIE MUNGER FRAMEWORK (Quality Compounders):
Find wonderful businesses at fair prices.
- Look for high Return on Equity (ROE).
- Look for Free Cash Flow consistency and high Operating Margins (The "Moat").
- Look for manageable Debt-to-Equity.
- Ignore hype and turnaround stories. Quality is king.
"""

SOROS_FRAMEWORK = """
GEORGE SOROS FRAMEWORK (Reflexivity & Narratives):
Find reflexive loops where narrative alters fundamentals.
- Look for extreme momentum or short squeezes.
- Look for high Short Interest (potential for violent reflexive upside).
- Are fundamentals disconnected from the narrative?
- Look for "bubble" mechanics or supply-side gluttony.
"""

class GodsEyeAnalyst:
    def __init__(self):
        self.rag = CIOFeedbackRAG()
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key and genai:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            print("WARNING: GEMINI_API_KEY not set or library not installed. Falling back to local simulation.")

    def get_tracked_theses(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, description, alpha_score, target_instrument FROM Theses WHERE is_tracked = 1")
            rows = cursor.fetchall()
            tracked = [dict(row) for row in rows]
            conn.close()
            return tracked
        except Exception as e:
            print(f"Error fetching tracked theses: {e}")
            return []

    def inject_to_db(self, thesis_desc, assumptions, tags, target_instrument, position_type, alpha_score, signal_id, impacted_thesis_id=None, title='UNCLASSIFIED ASSET'):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            current_time = int(time.time())
            
            if impacted_thesis_id:
                # Update existing tracked thesis
                cursor.execute('''
                    UPDATE Theses 
                    SET description = ?, updated_at = ?, alpha_score = ?, title = ?
                    WHERE id = ?
                ''', (thesis_desc, current_time, alpha_score, title, impacted_thesis_id))
                thesis_id = impacted_thesis_id
                
                # Delete old assumptions and replace them with the updated ones
                cursor.execute("DELETE FROM Assumptions WHERE thesis_id = ?", (thesis_id,))
                for assumption in assumptions:
                    desc = assumption.get("description", assumption) if isinstance(assumption, dict) else str(assumption)
                    status = assumption.get("status", "NEUTRAL") if isinstance(assumption, dict) else "NEUTRAL"
                    cursor.execute('''
                        INSERT INTO Assumptions (thesis_id, description, active, status)
                        VALUES (?, ?, ?, ?)
                    ''', (thesis_id, desc, 1, status))
                    
                print(f">>> Successfully UPDATED Tracked Thesis #{thesis_id} with new data.")
            else:
                # Insert brand new Thesis
                full_desc = f"{thesis_desc}\n\nTags: {' '.join(tags)}"
                cursor.execute('''
                    INSERT INTO Theses (description, status, confidence, created_at, updated_at, target_instrument, position_type, alpha_score, title)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (full_desc, 'ACTIVE', 0.8, current_time, current_time, target_instrument, position_type, alpha_score, title))
                thesis_id = cursor.lastrowid
                
                for assumption in assumptions:
                    desc = assumption.get("description", assumption) if isinstance(assumption, dict) else str(assumption)
                    status = assumption.get("status", "NEUTRAL") if isinstance(assumption, dict) else "NEUTRAL"
                    cursor.execute('''
                        INSERT INTO Assumptions (thesis_id, description, active, status)
                        VALUES (?, ?, ?, ?)
                    ''', (thesis_id, desc, 1, status))
                print(f">>> Successfully injected NEW Thesis #{thesis_id} into godseye.db")

            # Always link the new signal
            if signal_id:
                cursor.execute("INSERT OR IGNORE INTO ThesisSignals (thesis_id, signal_id) VALUES (?, ?)", (thesis_id, signal_id))
                
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database injection error: {e}")

    def evaluate_asset_signal(self, asset_data_json, signal_id=None):
        print(f"\n[LLM Request] Evaluating Asset Signal through the Council of Titans...")
        cio_feedback = self.rag.get_relevant_feedback()
        tracked_theses = self.get_tracked_theses()
        
        tracked_context = "NO TRACKED THESES CURRENTLY EXIST."
        if tracked_theses:
            tracked_context = "CURRENTLY TRACKED THESES:\n" + json.dumps(tracked_theses, indent=2)

        prompt = f"""
        You are the Council of Titans module of the God's Eye Engine.
        Evaluate the following asset data against three distinct mental models.
        
        {BURRY_FRAMEWORK}
        {BUFFETT_FRAMEWORK}
        {SOROS_FRAMEWORK}
        
        ASSET DATA:
        {asset_data_json}
        
        CRITICAL INSTRUCTION: Do not blindly extrapolate 5-year trends into the future. 
        
        DEDUPLICATION & UPDATE LOGIC:
        Review the USER'S TRACKED THESES below. Does this new asset data significantly impact any of them?
        If YES: You must output the ID of the thesis you are updating as 'impacted_thesis_id'. Update the description, recalculate the alpha_score, and explicitly mark the existing assumptions as "STRENGTHENED" or "WEAKENED" by this new data.
        If NO: Set 'impacted_thesis_id' to null, and generate a brand new thesis.
        
        {tracked_context}
        
        PREVIOUS CIO FEEDBACK TO ADHERE TO:
        {cio_feedback}
        
        ALPHA SCORE CALCULATION:
        Assign an alpha_score (0-100) representing the Probability of Outsized Profit based on Contrarian Asymmetry, Quality Discount, and Reflexive Momentum.
        
        You MUST output ONLY a valid JSON object. Do not include markdown. The JSON must match exactly:
        {{
            "impacted_thesis_id": null, // OR the integer ID of the tracked thesis you are updating
            "title": "A punchy 2-4 word title (e.g., Semiconductor Short, Argentine Bonds)",
            "thesis": "A concise paragraph explaining your core investment thesis...",
            "target_instrument": "AAPL",
            "position_type": "LONG",
            "alpha_score": 85,
            "assumptions": [
                {{"description": "Assumption 1", "status": "STRENGTHENED"}},
                {{"description": "Assumption 2", "status": "NEUTRAL"}},
                {{"description": "Assumption 3", "status": "WEAKENED"}}
            ],
            "tags": ["[BURRY-ALIGNED]"]
        }}
        """
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                raw_text = response.text
                clean_json = re.sub(r'```json\n|\n```|```', '', raw_text).strip()
                data = json.loads(clean_json)
                
                self.inject_to_db(
                    data['thesis'], 
                    data.get('assumptions', []), 
                    data.get('tags', []), 
                    data.get('target_instrument', 'UNKNOWN'),
                    data.get('position_type', 'UNKNOWN'),
                    data.get('alpha_score', 50),
                    signal_id,
                    data.get('impacted_thesis_id'),
                    data.get('title', 'UNCLASSIFIED ASSET')
                )
                return data
            except Exception as e:
                print(f"LLM API Error: {e}")
                
        # Simulated Fallback
        impact_id = None
        if tracked_theses:
            impact_id = tracked_theses[0]['id']
            
        long_assumption = "Market sentiment continues to aggressively over-value growth equities despite tightening macroeconomic conditions and rising capital costs. Retail trading volumes have surged to unprecendented highs, creating a reflexive loop where price action dictates fundamental narratives rather than the inverse. This creates a highly fragile structural environment where any liquidity shock could trigger a cascading sell-off, particularly in tech names with massive P/E multiples that require flawless execution to justify their current valuations. The underlying moat remains strong, but the current premium leaves zero margin for error."
        
        import random
        
        simulated_data = {
            "impacted_thesis_id": impact_id,
            "title": "Tech Bubble Momentum Short",
            "thesis": "The company shows strong free cash flow and a wide moat, but the stock is currently highly overvalued and crowded by momentum traders.",
            "target_instrument": "UNKNOWN",
            "position_type": "SHORT",
            "alpha_score": random.randint(45, 95),
            "assumptions": [
                {"description": long_assumption, "status": "WEAKENED"},
                {"description": "Macro environment remains favorable to Tech", "status": "NEUTRAL"},
                {"description": "No major regulatory crackdowns occur", "status": "NEUTRAL"}
            ],
            "tags": ["[BUFFETT-REJECT]", "[BURRY-REJECT]", "[SOROS-ALIGNED]"]
        }
        self.inject_to_db(
            simulated_data['thesis'], 
            simulated_data['assumptions'], 
            simulated_data['tags'], 
            simulated_data['target_instrument'],
            simulated_data['position_type'],
            simulated_data['alpha_score'],
            signal_id,
            simulated_data.get('impacted_thesis_id'),
            simulated_data['title']
        )
        return simulated_data

if __name__ == "__main__":
    analyst = GodsEyeAnalyst()
    print("God's Eye Analyst Initialized.")
    
    # Simulate a raw signal from equity_fetcher being passed to the DB first
    # So we can link it
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Signals (source, domain, content, timestamp) VALUES (?, ?, ?, ?)", 
                       ("yfinance", "equity", "AAPL P/E is 35, high momentum", int(time.time())))
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
    except Exception:
        signal_id = None
    
    sample_asset_data = '{"Instrument": "AAPL", "PE_Ratio": 35.5, "Momentum": "High", "FreeCashFlow": "Strong"}'
    evaluation = analyst.evaluate_asset_signal(sample_asset_data, signal_id)
    print("\n[Asset Evaluation Generated & Injected]")
