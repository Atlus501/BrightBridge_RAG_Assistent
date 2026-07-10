import asyncio
import nest_asyncio
import logging

from core.data_objects.request_body import RAG_Request_Body
from src.helper_functions import load_dotenv, setup_rag, get_rag_response

async def integration_test(prompt):
    load_dotenv()
    rag = setup_rag()

    request_token = RAG_Request_Body(
        past_conv = [],
        prompt = prompt
    )

    response = await get_rag_response(request_token, rag)
    return response

if __name__ == "__main__":
    nest_asyncio.apply()
    logging.basicConfig(level=logging.WARNING, filename="brightbridge.log", format='%(asctime)s - %(levelname)s - %(message)s')

    cache_test_prompt = "what are some good relationship therapy options?"
    prompt = "what are some good foundations for a healthy relationship?"

    response = asyncio.run(integration_test(prompt))
    print(response)