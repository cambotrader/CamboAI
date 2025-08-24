print("Testing Python execution")
try:
    import fastapi
    print("FastAPI imported successfully")
except Exception as e:
    print(f"FastAPI import error: {e}")

try:
    import uvicorn
    print("Uvicorn imported successfully")
except Exception as e:
    print(f"Uvicorn import error: {e}")

print("Test complete")
