from fastapi import FastAPI, Response, Request, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import ValidationError
import logging
import uvicorn
import os

from api.schemas.request_body import RAG_Request_Body, Context_Request_Body
from services.helper_functions import load_env, setup_rag, set_up_context_manager, get_rag_response

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

#api used for responding to requests
@app.post("/respond", status_code=status.HTTP_200_OK)
async def get_response(request_body : RAG_Request_Body, request: Request, response : Response):
    try:
        rag = request.app.state.rag

        rag_response, stored_string = await get_rag_response(request_body, rag)
        response_body = {
            "response" : rag_response,
            "stored_string" : stored_string,
        }
        return response_body

    except ValidationError as e:
        response_body = {
            "response" : "invalid data types"
        }
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response_body

    except Exception as e:
        response_body = {
            "response" : str(e),
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return response_body 


@app.post("/store_past_context", status_code=status.HTTP_201_CREATED)
async def post_past_context(request_body : Context_Request_Body, request : Request, response : Response):
    try:
        context_manager = request.app.state.context_manager

        res = await context_manager.save_context(request_body.actor_id,
                                                 request_body.conv_to_be_saved,
                                                 request_body.password,
                                                 role="user",
                                                 session_id=request_body.session_id)
        response_body = {
            "response" : "session successfully created/stored",
            "session_id" : res,
        }
        return response_body

    except ValidationError:
        response_body = {
            "response" : "please use use the proper data fields",
        }
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response_body

    except Exception as e:
        response_body = {
            "response" : str(e),
        }
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response_body

@app.post("/get_past_context", status_code=status.HTTP_200_OK)
async def get_past_context(request_body : Context_Request_Body, request : Request, response : Response):
    try:
        context_manager = request.app.state.context_manager

        decrypted_history = await context_manager.get_context(request_body.actor_id, 
                                                              request_body.password, 
                                                              request_body.session_id)
        response_body = {
            "past_convs" : decrypted_history,
        }
        return response_body

    except ValidationError:
        response_body = {
            "response" : "please use use the proper data fields"
        }
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response_body

    except Exception as e:
        response_body = {
            "past_convos" : [],
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return response_body 

#the code that will trigger if is it is set to be the main code
if __name__ == "__main__":
    load_env()
    SERVER_IP = os.getenv("SERVER_IP")
    SERVER_PORT = int(os.getenv("SERVER_PORT"))
    uvicorn.run("main:app", host=SERVER_IP, port=SERVER_PORT, reload=True)
