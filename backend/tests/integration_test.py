import asyncio
import nest_asyncio
import logging

from data_objects.request_body import RAG_Request_Body
from src.helper_functions import load_dotenv, setup_rag, get_rag_response

async def integration_test(prompt):
    load_dotenv()
    rag = setup_rag()

    session_token = {
        "session_id" : None,
        "password" : "sldfkjpoaf6asdfjshf5",
        "test_actor_id" : "test123",
        "SameSite" : "Strict",
        "past_conv" : [],
    }

    response = await get_rag_response(session_token : RAG_Request_Body, rag)
    return response

if __name__ == "__main__":
    nest_asyncio.apply()
    logging.basicConfig(level=logging.WARNING, filename="brightbridge.log", format='%(asctime)s - %(levelname)s - %(message)s')

    cache_test_prompt = "what are some good relationship therapy options?"
    prompt = "what are some good foundations for a healthy relationship?"

    response = asyncio.run(integration_test(prompt))
    print(response)