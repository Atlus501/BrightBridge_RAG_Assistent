from fastapi import FastAPI, Response, status
from pydantic import ValidationError
import logging
import uvicorn
import os

from data_objects.request_body import RAG_Request_Body, Context_Request_Body
from src.helper_functions import load_env, setup_rag, set_up_context_manager, get_rag_response

#sets up fastapi and logging configurations
app = FastAPI()
logging.basicConfig(level=logging.WARNING, filename="brightbridge.log", format='%(asctime)s - %(levelname)s - %(message)s')

#loads the environmental variables
load_env()

#creates the rag
rag = setup_rag()

#creates the redis_manager
context_manager = set_up_context_manager()

#api used for responding to requests
@app.post("/respond", status_code=status.HTTP_200_OK)
async def get_response(request_body : RAG_Request_Body, response : Response):
    try:
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
async def post_past_context(request_body : Context_Request_Body, response : Response):
    try:
        res = await context_manager.save_context(request_body.actor_id,
                                                 request_body.past_conv,
                                                 role="user",
                                                 session_id=request_body.session_id)
        response_body = {
            "response" : "session successfully created/stored",
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
            "response" : str(e),
        }
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response_body

@app.post("/get_past_context", status_code=status.HTTP_200_OK)
async def get_past_context(request_body : Context_Request_Body, response : Response):
    try:
        decrypted_history, session_id = await context_manager.get_context(request_body.actor_id, 
                                                request_body.password, 
                                                request_body.session_id)
        response_body = {
            "past_convs" : decrypted_history,
            "session_id" : session_id,
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
    SERVER_IP = os.getenv("SERVER_IP")
    SERVER_PORT = int(os.getenv("SERVER_PORT"))
    uvicorn.run("main:app", host=SERVER_IP, port=SERVER_PORT, reload=True)
