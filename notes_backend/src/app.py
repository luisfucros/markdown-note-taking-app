import models
from configs.database import engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, note, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Markdown Note Taking API",
    description="Markdown Note Taking API",
    version="0.1.0",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(note.router)
app.include_router(auth.router)
