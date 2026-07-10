import logging

from fastapi import APIRouter, Response, Request, status
from pydantic import ValidationError

from services.helper_functions import get_rag_response
from api.schemas.request_body import RAG_Request_Body

router = APIRouter()

#api used for responding to requests
@router.post("/respond", status_code=status.HTTP_200_OK)
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