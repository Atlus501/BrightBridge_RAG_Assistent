import logging

from fastapi import APIRouter, Response, Request, status
from pydantic import ValidationError

from api.schemas.request_body import RAG_Request_Body

router = APIRouter()

#api used for responding to requests
@router.post("/respond", status_code=status.HTTP_200_OK)
async def get_response(request_body : RAG_Request_Body, request: Request, response : Response):
    try:
        rag = request.app.state.rag

        rag_response = await rag.invoke(request_body.prompt,
                                        request_body.past_conv)

        table = rag_response.maketrans({"<": "_", ">": "_"})

        stored_string = f"User: {request_body.prompt[:128]}...\n Assistant: {response[:128]}...\n"
        rag_response = rag_response.translate(table)

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