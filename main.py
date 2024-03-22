"""Main entrypoint for the app."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes

import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

#============================================================================================
from langsmithHandler import SendFeedbackBody, UpdateFeedbackBody, GetTraceBody, LangsmithHandler
if os.environ.get('LANGCHAIN_API_KEY'):
    langsmithHandler = LangsmithHandler()
    @app.post("/feedback")
    async def send_feedback_route(body: SendFeedbackBody):
        return await langsmithHandler.send_feedback(body)

    @app.patch("/feedback")
    async def update_feedback_route(body: UpdateFeedbackBody):
        return await langsmithHandler.update_feedback(body)

    @app.post("/get_trace")
    async def get_trace_route(body: GetTraceBody):
        return await langsmithHandler.get_trace(body)

#============================================================================================
from chat import ChatApplication, ChatRequest
chatApp = ChatApplication()
add_routes(
    app, chatApp.chain, path="/chat", input_type=ChatRequest, config_keys=["configurable"]
)

#============================================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
