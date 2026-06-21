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
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None
            print("WARNING: GEMINI_API_KEY not set or library not installed. Falling back to local simulation.")

    def inject_to_db(self, thesis_desc, assumptions, tags, signal_id):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Combine desc and tags
            full_desc = f"{thesis_desc}\n\nTags: {' '.join(tags)}"
            current_time = int(time.time())
            
            # Insert Thesis
            cursor.execute('''
                INSERT INTO Theses (description, status, confidence, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (full_desc, 'ACTIVE', 0.8, current_time, current_time))
            
            thesis_id = cursor.lastrowid
            
            # Insert Assumptions
            for assumption in assumptions:
                cursor.execute('''
                    INSERT INTO Assumptions (thesis_id, description, active)
                    VALUES (?, ?, ?)
                ''', (thesis_id, assumption, 1))
                
            # Insert ThesisSignals mapping if signal_id provided
            if signal_id:
                cursor.execute('''
                    INSERT INTO ThesisSignals (thesis_id, signal_id)
                    VALUES (?, ?)
                ''', (thesis_id, signal_id))
                
            conn.commit()
            conn.close()
            print(f">>> Successfully injected Thesis #{thesis_id} and {len(assumptions)} Assumptions into godseye.db")
        except Exception as e:
            print(f"Database injection error: {e}")

    def evaluate_asset_signal(self, asset_data_json, signal_id=None):
        print(f"\n[LLM Request] Evaluating Asset Signal through the Council of Titans...")
        cio_feedback = self.rag.get_relevant_feedback()

        prompt = f"""
        You are the Council of Titans module of the God's Eye Engine.
        Evaluate the following asset data against three distinct mental models.
        
        {BURRY_FRAMEWORK}
        {BUFFETT_FRAMEWORK}
        {SOROS_FRAMEWORK}
        
        ASSET DATA (Includes 5-Year Scans & Solvency Metrics):
        {asset_data_json}
        
        CRITICAL INSTRUCTION: Do not blindly extrapolate the 5-year trends into the future. Use them only to understand the historical trajectory and structural decay/growth of the business.
        
        PREVIOUS CIO FEEDBACK TO ADHERE TO:
        {cio_feedback}
        
        You MUST output ONLY a valid JSON object. Do not include any markdown formatting or explanation. The JSON must match exactly this structure:
        {{
            "thesis": "A concise paragraph explaining your core investment thesis based on the asset data.",
            "assumptions": [
                "Assumption 1 that must hold true for this thesis to survive",
                "Assumption 2 that must hold true",
                "Assumption 3"
            ],
            "tags": ["[BURRY-ALIGNED]", "[SOROS-REJECT]"]
        }}
        """
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                raw_text = response.text
                # Clean up markdown if the LLM still returns it
                clean_json = re.sub(r'```json\n|\n```|```', '', raw_text).strip()
                data = json.loads(clean_json)
                
                print("\n[AI generated structured Thesis & Assumptions]")
                self.inject_to_db(data['thesis'], data.get('assumptions', []), data.get('tags', []), signal_id)
                return data
            except Exception as e:
                print(f"LLM API Error: {e}")
                
        # Simulated Fallback
        simulated_data = {
            "thesis": "The company shows strong free cash flow and a wide moat, but the stock is currently highly overvalued and crowded by momentum traders.",
            "assumptions": [
                "Market sentiment continues to over-value growth",
                "Macro environment remains favorable to Tech",
                "No major regulatory crackdowns occur"
            ],
            "tags": ["[BUFFETT-REJECT]", "[BURRY-REJECT]", "[SOROS-ALIGNED]"]
        }
        self.inject_to_db(simulated_data['thesis'], simulated_data['assumptions'], simulated_data['tags'], signal_id)
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
