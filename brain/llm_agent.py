import os
import json
from rag_memory import CIOFeedbackRAG

# Import google SDK (Assuming installed: pip install google-generativeai)
# import google.generativeai as genai

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
        
        # Configuration for actual Gemini API
        # api_key = os.environ.get("GEMINI_API_KEY")
        # if api_key:
        #     genai.configure(api_key=api_key)
        #     self.model = genai.GenerativeModel('gemini-1.5-pro')
        # else:
        #     self.model = None

    def evaluate_asset_signal(self, asset_data_json):
        print(f"\n[LLM Request] Evaluating Asset Signal through the Council of Titans...")
        cio_feedback = self.rag.get_relevant_feedback()

        prompt = f"""
        You are the Council of Titans module of the God's Eye Engine.
        Evaluate the following asset data (which may be an equity, sovereign bond, or macro instrument) against three distinct mental models.
        
        {BURRY_FRAMEWORK}
        
        {BUFFETT_FRAMEWORK}
        
        {SOROS_FRAMEWORK}
        
        ASSET DATA:
        {asset_data_json}
        
        PREVIOUS CIO FEEDBACK TO ADHERE TO:
        {cio_feedback}
        
        Based on the data, provide a brief thesis. Include exact TAGS at the end to indicate alignment:
        Available Tags: [BURRY-ALIGNED] [BURRY-REJECT] [BUFFETT-ALIGNED] [BUFFETT-REJECT] [SOROS-ALIGNED] [SOROS-REJECT]
        """
        
        # if self.model:
        #     response = self.model.generate_content(prompt)
        #     return response.text
        
        # Simulated LLM Response for V1 local testing
        return "Thesis: The company shows strong free cash flow and a wide moat, but the stock is currently highly overvalued and crowded by momentum traders.\nTags: [BUFFETT-REJECT] [BURRY-REJECT] [SOROS-ALIGNED]"

    def generate_counterfactual(self, thesis_description):
        print(f"\n[LLM Request] Generating Counterfactual for: {thesis_description}")
        
        cio_feedback = self.rag.get_relevant_feedback()
        
        prompt = f"""
        You are the Devil's Advocate module of the God's Eye Engine.
        Your job is to take the following active thesis and construct the strongest possible
        counter-thesis using 2nd-order, contrarian thinking (aligned with Soros reflexivity).
        
        THESIS: {thesis_description}
        
        PREVIOUS CIO FEEDBACK TO ADHERE TO:
        {cio_feedback}
        
        Generate the counter-thesis in 3 bullet points.
        """
        
        # if self.model:
        #     response = self.model.generate_content(prompt)
        #     return response.text
        
        # Simulated LLM Response for V1 local testing
        return "1. The market has already priced in the expected scenario.\n2. Supply chain disruptions will actually create deflationary localized pressure.\n3. Institutional positioning is overwhelmingly one-sided, setting up a reflexive short-squeeze."

if __name__ == "__main__":
    analyst = GodsEyeAnalyst()
    print("God's Eye Analyst Initialized.")
    
    # Test RAG insertion
    analyst.rag.add_feedback("I don't agree with Michael Burry's call on $LULU, focus on geopolitical supply chains instead.")
    
    sample_asset_data = '{"Instrument": "Argentinian Sovereign Bond", "Yield": "25%", "Narrative": "Default imminent but structural reforms passing."}'
    evaluation = analyst.evaluate_asset_signal(sample_asset_data)
    print("\n[Asset Evaluation Generated]")
    print(evaluation)
