# main.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
import ccxt

app = FastAPI()

class BotRequest(BaseModel):
    openai_key: str
    trading_key: str

@app.post("/start-bot")
async def start_bot(req: BotRequest):
    # Set up OpenAI
    openai.api_key = req.openai_key

    # Example: Use OpenAI to generate some logic
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": "What's the best crypto to buy today?"
        }]
    )
    advice = response.choices[0].message.content

    # Example: Connect to Binance (use CCXT)
    try:
        exchange = ccxt.binance({
            'apiKey': req.trading_key,
            'secret': 'user-secret-here'  # replace this for real use
        })
        balance = exchange.fetch_balance()
        return {"message": "Bot started", "advice": advice, "balance": balance}
    except Exception as e:
        return {"error": str(e)}
