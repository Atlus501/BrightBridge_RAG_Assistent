import asyncio
import nest_asyncio
import logging

from api.schemas.request_body import RAG_Request_Body
from services.rag.setup import load_dotenv, setup_rag

async def integration_test(prompt):
    load_dotenv()
    rag = setup_rag()

    request_token = RAG_Request_Body(
        past_conv = [],
        prompt = prompt
    )

    response = await rag.invoke(request_token.prompt, request_token.past_conv)
    return response

if __name__ == "__main__":
    nest_asyncio.apply()
    logging.basicConfig(level=logging.WARNING, filename="brightbridge.log", format='%(asctime)s - %(levelname)s - %(message)s')

    cache_test_prompt = "what are some good relationship therapy options?"
    prompt = "what are some good foundations for a healthy relationship?"

    response = asyncio.run(integration_test(prompt))
    print(response)