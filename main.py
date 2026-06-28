from fastapi import FastAPI
from routers import auth, users




app = FastAPI(title="Crypto Price Tracker")

app.include_router(auth.router)
app.include_router(users.router)