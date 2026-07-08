import os
from dotenv import load_dotenv
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from src.cryptographer import Cryptographer
from src.redis_manager import Redis_Manager
from src.guardrails.guardrail_registry import Guardrail_Registry
from src.guardrails.guardrail_factory import Guardrail_Factory
from src.redis_cache_manager import Redis_Cache_Manager
from src.enhanced_rag import Enhanced_RAG_v6

"""
Guardrail configurations
"""
GUARDRAIL_CONFIGS = [
        {
            "name": "prompt_guardrail",

            "factory_parameters" : {
            "model_name": "meta-llama/Llama-Prompt-Guard-2-86M",
            "desired_output": "LABEL_0",
            "response" :
                """Our system has detected a potential injection or jailbreak
                    attack on the LLM. If this was a false alarm,
                    please contact helloworld4846@gmail.com for feedback, and further
                    tuning of the malicious system. In your message, please screenshot
                    your prompt and the LLM response for reproducability.
                    We apologize for any inconveniences caused, as this is still
                    an experimental feature.
                """,
            }

        },
        {
            "name": "suicide_guardrail",

            "factory_parameters" : {
            "model_path": "transformer_config",
            "desired_output": 0,
            "response" :
                """
                    Our system has detected that you may have suicidal thoughts
                    or tendencies. We at BrightBridge strongly discourages this.
                    No matter what, you are loved, and will be missed when you are
                    gone. Instead of self-harm, we highly recommend you seek therapy
                    or contact us through helloworld4846@gmail.com for some advice instead.
                    If this was a false alarm, please contact the same email for
                    feedback for further tuning of the suicide detection system.
                    We apologize for any inconveniences caused, as this is still
                    an experimental feature.
                """
            }
        }
    ]

"""
Loads .env variables
"""
def load_env():
    load_dotenv()

"""
Sets up the registry
"""
def setup_registry():
    # Instantiate the factory and registry
    guardrail_factory = Guardrail_Factory()
    guardrail_registry = Guardrail_Registry()

    # Register the factory methods directly (they accept all necessary parameters)
    guardrail_registry.register_guardrail_creator("prompt_guardrail", guardrail_factory.create_prompt_guardrail)
    guardrail_registry.register_guardrail_creator("suicide_guardrail", guardrail_factory.create_suicide_guardrail)

    return guardrail_registry

"""
Sets up the context manager
"""
def set_up_context_manager():
    cryptographer = Cryptographer()

    #creating the redis manager
    redis_manager = Redis_Manager(num_recent_messages=3, cryptographer=cryptographer)

    return redis_manager


"""
Sets up dependencies for the RAG via dependency injection
"""
def setup_rag():

    guardrail_registry = setup_registry()

    # Instantiate guardrails from the config using the registry
    guardrails = []
    for config in GUARDRAIL_CONFIGS:
        creator_name = config["name"]
        # Get the base factory method from the registry
        creator_method = guardrail_registry.get_guardrail_creator(creator_name)

        # Prepare arguments for the factory method
        # All arguments needed by the factory method (except 'self') are now in the config.
        factory_args = config["factory_parameters"]

        # Call the factory method with the prepared arguments
        guardrails.append(creator_method(**factory_args))

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    #creating the vector database retriever
    #gemini as llm
    llm =  ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                api_key=GEMINI_API_KEY)

    # Get Embeddings Model
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2",
                                            google_api_key=GEMINI_API_KEY)

    #connects the Chroma object to the cloud instance
    vector_store = Chroma(
        collection_name="intimate_relationships_collection",
        embedding_function=embeddings,
        chroma_cloud_api_key=os.getenv("CHROMA_API_KEY"),
        tenant=os.getenv("CHROMA_TENANT"),
        database="Demo",
    )

    # Set Chroma Vector Store as the Retriever
    retriever = vector_store.as_retriever()

    # Create the Prompt Template
    prompt_template = """Use the context provided to answer
    the user's question below. However, if there is no context,
    tell the user there is no verified information about their question,
    and try to answer the question based on your own knowledge.
    To enhance your knowledge of the situation, you are also provided your
    chat history.

    context: {context}

    chat_history: {chat_history}

    question: {query}

    answer: """

    cache = Redis_Cache_Manager()

    rag = Enhanced_RAG_v6(llm, retriever, prompt_template)
    rag.set_guardrails(guardrails)
    rag.set_cache(cache)

    return rag

#workflow of the user
async def get_rag_response(response_body, rag):

    response = await rag.invoke(response_body.prompt,
                                session_token.past_conv)

    stored_string = f"User: {prompt[:128]}...\n Assistant: {response[:128]}...\n"
    return response, stored_string
