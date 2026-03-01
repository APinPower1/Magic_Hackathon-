from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, events

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Registration & Capacity Manager")

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(registrations.router)

@app.get("/")
def root():
    return {"message": "Event Registration API is running"}