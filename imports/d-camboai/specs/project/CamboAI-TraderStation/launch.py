from fastapi import FastAPI
import uvicorn

# Import core modules
from chart_module import ChartModule
from strategy_engine import StrategyEngine
from sentiment_panel import SentimentPanel

app = FastAPI()

# Initialize modules
chart = ChartModule()
engine = StrategyEngine()
sentiment = SentimentPanel()

@app.get("/")
def read_root():
    return {
        "message": "Cambo AI Trader Station is live!",
        "modules": ["ChartModule", "StrategyEngine", "SentimentPanel"]
    }

@app.get("/chart")
def get_chart():
    return chart.hydrate()

@app.get("/strategy")
def get_strategy():
    return engine.hydrate()

@app.get("/sentiment")
def get_sentiment():
    return sentiment.hydrate()
    
if __name__ == "__main__":
    uvicorn.run("launch:app", host="127.0.0.1", port=8000, reload=True)
