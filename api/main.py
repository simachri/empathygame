import os

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

port = os.environ['PORT']
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(port))
