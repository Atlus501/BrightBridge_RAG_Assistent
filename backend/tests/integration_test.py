import asyncio
import nest_asyncio
import logging

from src.helper_functions import load_dotenv, setup_rag, test_prompt

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

    response = await test_prompt(session_token, prompt, rag)
    return repsonse

if __name__ == "__main__":
    nest_asyncio.apply()
    logging.basicConfig(level=logging.WARNING, filename="brightbridge.log", format='%(asctime)s - %(levelname)s - %(message)s')

    cache_test_prompt = "what are some good relationship therapy options?"
    prompt = "what are some good foundations for a healthy relationship?"

    response = asyncio.run(integration_test(prompt))
    print(response)