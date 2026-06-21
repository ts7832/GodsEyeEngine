import sqlite3
import os
import yfinance as yf

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'godseye.db'))

def update_pnl():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Fetch all starred theses with an entry price
        cursor.execute("SELECT id, target_instrument, position_type, entry_price FROM Theses WHERE is_starred = 1 AND target_instrument IS NOT NULL AND target_instrument != 'UNKNOWN' AND entry_price IS NOT NULL")
        rows = cursor.fetchall()
        
        for row in rows:
            thesis_id, target, pos_type, entry_price = row
            try:
                ticker = yf.Ticker(target)
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                
                if current_price:
                    if pos_type and pos_type.upper() == 'SHORT':
                        pnl = ((entry_price - current_price) / entry_price) * 100
                    else:
                        pnl = ((current_price - entry_price) / entry_price) * 100
                        
                    cursor.execute("UPDATE Theses SET current_price = ?, pnl_percentage = ? WHERE id = ?", (current_price, pnl, thesis_id))
                    print(f"Updated PnL for Thesis #{thesis_id} ({target}): {pnl:.2f}%")
            except Exception as e:
                print(f"Failed to update PnL for {target}: {e}")
                
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error in update_pnl: {e}")

if __name__ == "__main__":
    print("Initiating PnL Tracker...")
    update_pnl()
    print("PnL Tracking complete.")
