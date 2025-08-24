from fastapi import FastAPI
from chart_module import router as chart_router
app = FastAPI()
# Include chart route
app.include_router(chart_router)
@app.get("/")
async def root():
    return {"message": "Cambo AI Trader Station is up and running!"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
