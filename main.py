from fastapi import FastAPI
from routers import auth, users, alerts, ws




app = FastAPI(title="Crypto Price Tracker")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(alerts.router)
app.include_router(ws.router)