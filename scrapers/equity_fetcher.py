import os
import sys
import sqlite3
import json
import time

# Support for local .libs directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.libs')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'brain')))

try:
    import yfinance as yf
except ImportError:
    print("yfinance not installed. Please install it using: pip3 install yfinance")
    sys.exit(1)

from llm_agent import GodsEyeAnalyst

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'godseye.db'))
analyst = GodsEyeAnalyst()

def save_signal_and_evaluate(source, content, confidence):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Signals (source, domain, content, timestamp, confidence)
        VALUES (?, ?, ?, ?, ?)
    ''', (source, 'equities', content, int(time.time()), confidence))
    signal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"Triggering AI Council for Signal #{signal_id} ({source})...")
    analyst.evaluate_asset_signal(content, signal_id)

def fetch_equity_data(ticker):
    print(f"Fetching data for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if 'symbol' not in info and 'regularMarketPrice' not in info:
            print(f"Failed to fetch valid data for {ticker}")
            return
            
        metrics = {
            "Ticker": ticker,
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Currency": info.get("financialCurrency", info.get("currency")),
            "Price_To_Book": info.get("priceToBook"),
            "Free_Cash_Flow": info.get("freeCashflow"),
            "Total_Cash": info.get("totalCash"),
            "Total_Debt": info.get("totalDebt"),
            "Shares_Outstanding": info.get("sharesOutstanding"),
            "Short_Ratio": info.get("shortRatio"),
            "Short_Percent_Of_Float": info.get("shortPercentOfFloat"),
            "Return_On_Equity": info.get("returnOnEquity"),
            "Debt_To_Equity": info.get("debtToEquity"),
            "Operating_Margins": info.get("operatingMargins"),
            "Forward_PE": info.get("forwardPE"),
            "Trailing_PE": info.get("trailingPE"),
            "Analyst_Rating": info.get("recommendationKey"),
            "Target_Mean_Price": info.get("targetMeanPrice"),
            "Current_Price": info.get("currentPrice")
        }
        
        # Calculate volume surge (Proxy for capitulation / reflexivity) using a 1y baseline
        try:
            hist = stock.history(period="1y")
            if not hist.empty:
                avg_vol = hist['Volume'].mean()
                recent_vol = hist['Volume'].iloc[-5:].mean()
                metrics["Volume_Surge_Ratio"] = round(recent_vol / avg_vol, 2) if avg_vol > 0 else 1.0
        except Exception as e:
            metrics["Volume_Surge_Ratio"] = None

        # 5-Year Financial Trend Analysis
        try:
            financials = stock.financials
            if not financials.empty:
                if 'Total Revenue' in financials.index:
                    revs = financials.loc['Total Revenue'].dropna()
                    if len(revs) >= 2:
                        oldest_rev = revs.iloc[-1]
                        newest_rev = revs.iloc[0]
                        if oldest_rev > 0:
                            metrics["5_Year_Revenue_Growth"] = f"{round(((newest_rev - oldest_rev) / oldest_rev) * 100, 2)}%"
                        
                if 'Net Income' in financials.index:
                    incomes = financials.loc['Net Income'].dropna()
                    if len(incomes) >= 2:
                        oldest_inc = incomes.iloc[-1]
                        newest_inc = incomes.iloc[0]
                        if oldest_inc > 0:
                            metrics["5_Year_Net_Income_Growth"] = f"{round(((newest_inc - oldest_inc) / oldest_inc) * 100, 2)}%"
        except Exception as e:
            pass

        # Format the insight for the LLM
        content = f"Equity Data for {ticker} (Includes 5-Year Deep Scan & Solvency Metrics):\n" + json.dumps(metrics, indent=2)
        
        # We assign high confidence to direct financial data
        save_signal_and_evaluate(f"YahooFinance-{ticker}", content, 0.95)
        print(f"Saved equity signal for {ticker}")
        
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")

if __name__ == "__main__":
    # Example Tickers spanning different titan philosophies:
    # AAPL (Tech monopoly, Buffett)
    # GME (Meme/Reflexivity, Soros)
    # WBD (Hated Value, Burry)
    # INTC (Turnaround/Value trap)
    target_tickers = ["AAPL", "GME", "WBD", "INTC"]
    
    print("Initiating God's Eye Equity Fetcher...")
    for t in target_tickers:
        fetch_equity_data(t)
        time.sleep(2) # Be polite to Yahoo Finance APIs
