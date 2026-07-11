from fastapi import FastAPI, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn
import os

from api.routes.context_manager import router as context_router
from api.routes.rag import router as rag_router

from services.rag.setup import load_env, setup_rag
from services.context_manager.setup import set_up_context_manager

allowed_origins = [
    "http://localhost:8000", # If you also test locally
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # [Startup]: Triggered before the server starts accepting requests
    logging.basicConfig(level=logging.WARNING, filename="brightbridge.log", format='%(asctime)s - %(levelname)s - %(message)s')
    app.state.rag = setup_rag()
    app.state.context_manager = set_up_context_manager()

    yield

    logging.warning("Shutting down backend services...")


#sets up fastapi and logging configurations
app = FastAPI(
    title = "brightbridge assistant backend",
    lifespan = lifespan,
    description="Asynchronous backend service managing text context vector lookups",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,           # Allowed domains list
    allow_credentials=True,          # Permit cookies / auth headers
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allow all custom HTTP headers
)

app.include_router(rag_router, prefix="/rag", tags=["RAG"])
app.include_router(context_router, prefix="/context", tags=["Context Manager"])

"""
Function that initially welcomes the user as the are connected to the endpoint.
"""
@app.get("/", status_code=status.HTTP_200_OK)
async def respond():
    response_body = {
        "response" : "you have been connected",
    }
    return response_body

#the code that will trigger if is it is set to be the main code
if __name__ == "__main__":
    load_env()
    SERVER_IP = os.getenv("SERVER_IP")
    SERVER_PORT = int(os.getenv("SERVER_PORT"))
    uvicorn.run("main:app", host=SERVER_IP, port=SERVER_PORT, reload=True)
