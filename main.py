from server.main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting AarogyaX server...")
    uvicorn.run("server.main:app", host="0.0.0.0", port=5000, reload=True)