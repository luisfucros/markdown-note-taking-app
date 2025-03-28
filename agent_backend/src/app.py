from auth_lib import database, oauth2
from auth_lib.schemas import user_schemas, note_schemas
from note_bot.agent.prompts import grammar_agent_prompt
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
import asyncio
from note_bot.bot import client
from note_bot.bot import Bot
import os


logger = logging.getLogger(__name__)


app = FastAPI(
    title="Note Bot API",
    description="Note Bot API",
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

bot = Bot()


@app.websocket("/ws/bot")
async def websocket_chat(websocket: WebSocket, db: Session = Depends(database.get_db)):
    request_header_dict = dict(websocket.headers)
    access_token = request_header_dict.get("authorization", "").replace("Bearer ", "")
    if access_token == "":
        await websocket.close(code=1008)
        raise HTTPException(status_code=401, detail="Missing access token")

    oauth2.get_current_user(access_token, db)
    
    await websocket.accept()
    bot = Bot()
    try:
        while True:
            data = await asyncio.wait_for(websocket.receive_json(), timeout=60)
            messages = data.get("messages", [])
            if not messages:
                await websocket.send_json({"type":"error", "message": "Messages cannot be empty"})
                continue
            await bot.run(messages, access_token, websocket)
    except WebSocketDisconnect:
        print("WebSocket disconnected")

@app.post("/bot/grammar", response_model=note_schemas.Note)
async def grammar_check(user_input: note_schemas.Note,
                         current_user: user_schemas.UserOut = Depends(oauth2.get_current_user)):
    response = await client.responses.create(
        model=os.getenv("MODEL_NAME", "gpt-4o-mini-2024-07-18"),
        input=grammar_agent_prompt.format(user_input=user_input.note)
    )

    return note_schemas.Note(note=response.output_text)
