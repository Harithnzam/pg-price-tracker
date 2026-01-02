import requests
from bs4 import BeautifulSoup
import os
from supabase import create_client

# 1. Config (Use Environment Variables for security)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_pg_prices():
    # Public Gold uses a specific table for live prices
    url = "https://publicgold.com.my/index.php/liveprice.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Selecting the GAP and SAP prices
    # Note: If PG changes their website, update these selectors
    gold = soup.find(id="gap_price").text.replace('RM', '').strip()
    silver = soup.find(id="sap_price").text.replace('RM', '').strip()
    
    return float(gold), float(silver)

def get_ai_recommendation(gold, silver):
    # Fetch last recorded price to check trend
    last_data = supabase.table("price_history").select("*").order("created_at", desc=True).limit(1).execute()
    
    trend = "stable"
    if last_data.data:
        prev_gold = float(last_data.data[0]['gold_price'])
        if gold < prev_gold: trend = "dropping (Good for Buy)"
        elif gold > prev_gold: trend = "rising (Better to Hold)"

    # Simple logic for Buy/Hold
    if trend == "dropping (Good for Buy)":
        return "BUY / ACCUMULATE"
    else:
        return "HOLD / NOT BUY"

def main():
    gold, silver = get_pg_prices()
    rec = get_ai_recommendation(gold, silver)
    
    # Insert into Supabase
    supabase.table("price_history").insert({
        "gold_price": gold,
        "silver_price": silver,
        "recommendation": rec
    }).execute()
    print(f"Updated: Gold {gold}, Silver {silver}. Recommendation: {rec}")

if __name__ == "__main__":
    main()