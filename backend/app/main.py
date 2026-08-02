from fastapi import FastAPI

app = FastAPI()
# this is the starting point of our application, we can define our routes here
@app.get("/")
async def read_root():
    return {"Hello": "World"}
    