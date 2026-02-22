
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def ping():
    return {"result": "healthy"}

def main():
    print("Hello from datalama!")


if __name__ == "__main__":
    main()
