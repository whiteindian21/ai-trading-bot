from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ccxt
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure you have this environment variable

class BotRequest(BaseModel):
    exchange: str  # 'binance', 'coinbasepro', 'oanda', etc.
    apiKey: str
    apiSecret: str
    strategyPrompt: str

@app.post("/start-bot")
def start_bot(data: BotRequest):
    # Ensure OpenAI API key is set
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable is not set.")
    
    try:
        exchange_class = getattr(ccxt, data.exchange)
    except AttributeError:
        raise HTTPException(status_code=400, detail="Unsupported exchange.")

    exchange = exchange_class({
        'apiKey': data.apiKey,
        'secret': data.apiSecret
    })

    try:
        balance = exchange.fetch_balance()
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

    ai_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a trading strategy bot."},
            {"role": "user", "content": data.strategyPrompt}
        ]
    )

    return {
        "status": "success",
        "exchange": data.exchange,
        "balance_summary": {k: v['total'] for k, v in balance['total'].items() if v > 0},
        "strategy": ai_response['choices'][0]['message']['content']
    }
