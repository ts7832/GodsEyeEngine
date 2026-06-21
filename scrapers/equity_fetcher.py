import os
import sys
import sqlite3
import json
import time

# Support for local .libs directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.libs')))

try:
    import yfinance as yf
except ImportError:
    print("yfinance not installed. Please install it using: pip3 install yfinance")
    sys.exit(1)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'godseye.db'))

def save_signal(source, content, confidence):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Signals (source, domain, content, timestamp, confidence)
        VALUES (?, ?, ?, ?, ?)
    ''', (source, 'equities', content, int(time.time()), confidence))
    conn.commit()
    conn.close()

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
            "Price_To_Book": info.get("priceToBook"),
            "Free_Cash_Flow": info.get("freeCashflow"),
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
        
        # Calculate volume surge (Proxy for capitulation / reflexivity)
        try:
            hist = stock.history(period="3mo")
            if not hist.empty:
                avg_vol = hist['Volume'].mean()
                recent_vol = hist['Volume'].iloc[-5:].mean()
                metrics["Volume_Surge_Ratio"] = round(recent_vol / avg_vol, 2) if avg_vol > 0 else 1.0
        except Exception as e:
            metrics["Volume_Surge_Ratio"] = None

        # Format the insight for the LLM
        content = f"Equity Data for {ticker}:\n" + json.dumps(metrics, indent=2)
        
        # We assign high confidence to direct financial data
        save_signal(f"YahooFinance-{ticker}", content, 0.95)
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
