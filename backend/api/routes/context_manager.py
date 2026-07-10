import logging

from fastapi import APIRouter, Response, Request, status
from pydantic import ValidationError

from api.schemas.request_body import Context_Request_Body

router = APIRouter()

@router.post("/store", status_code=status.HTTP_201_CREATED)
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

@router.post("/retrieve", status_code=status.HTTP_200_OK)
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