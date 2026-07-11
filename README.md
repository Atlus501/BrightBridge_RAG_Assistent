# BrightBridge_RAG_Assistent
This will be my first RAG project. The LLM will be one of OpenAI's and I'm going to use fine-tuned transformers to detect suspicious prompts. This will be a 100% python project. The reason that I used a lot of notebooks is bc/ I prefer to prototype with google colab (especially with GPUs to help me train models). Naturally, the production level code will be pure python scripts though.

### Architectural Choices
The below image is a high level view of the architecure.
<img width="797" height="470" alt="image" src="https://github.com/user-attachments/assets/2f8d6aa4-dbaf-4196-a25c-d403aba3e54d" />
* the overall system is seperated into two services:
 * the naive RAG system that has been enhanced by adding Redis Langcache and transformer guardrails.
 * the user context manager that retrieves user conversation snippets from Redis Agent Memory.

Explanation of User Context Manager Components
 * Redis Agent Memory -- a good Redis Cloud service for storing and retrieving user session information. Having this information on hand could enhance the LLM's response by providing additional context. An optimization is that only small portions of the user's conversations would be stored at a time. Storing too much data could lead to latency and diminishing returns on the benefits of the context. To balance utility and privacy, the session memories would only have a ttl of one day. 
 *  Cryptographer -- a class responsible for encrypting/decrypting conversation snippets using AES-GCM. Due to the senstive nature of the stored data, it is imperative that they are properly secured. If I just retrieve session information through session_ids, then that would lead to a Broken Object Level Authorization, where attackers could brute force session_ids until they find valid ones. The solution to that is encrypting user data with a password. In that case, the attacker would need to guess both a valid session_id and password, which is much more unlikely. The reason why I picked AES-GCM is that it's the industry standard for symmetrical encryption. 

Explaination of Enhanced RAG Components
* ChromaDB (cloud instance) and Gemini llm & embedder are the core of the RAG. The text gets embedded by the embedder, gets searched in ChromaDB, and then gets fed into Gemini. The reason I picked these services is because they are relatively efficient and have lower cost of entry for prototyping. 
* Redis Langcache -- an efficient cloud service that could lookup FAQs efficiently. To improve user experience, FAQs will be stored in the Redis Langcache database. If there is a cache hit, a early response will be returned. This way, generic questions will be met with rapid responses. Also, it just massively speeds up the responses in general. Based on my observations, a cache hit would return a response in ~1-2 seconds. On the othe hand, a cache miss would inflate the response time to ~7-9 seconds.
* Guardrail -- guardrail classes are in place to provide custom, automatic responses to prompt injection attacks and suicidal prompts. It is essential that a seperate mechanism needs to be present bc/ llms are trivially easy to manipulate and could struggle with these scenarios. I chose transformers because of their ability to analyze texts. Thus, I fined tuned one on suicidal prompt datasets. I was thinking about adding a vector search mechanism (since they would be easier to update and analyze semantic meaning), but considering how high the latency for answers could be, adding another mechanism seems unwise. 
 * To increase maintainability, I used a guardrail factory, registry, and config files that encapsualated knowledge on how to create these guardrails. This design is easier to maintain because if ever needed to change the logic or structure of these guardrails, I just need to change a small amount of code these files instead of changing code every single time I call a constructor. 

* When the FastAPI backend initially starts, all dependencies will be created and injected into these service classes. 

### General user workflow
1. Default session token is generated (if there wasn't one present). That information includes, a securely generated password, actor_id, session_id = None, and past_conv = [].
2. If a valid session_id is present, the background service retrieves information from Redis Agent Memory based on the information in session token and decrypts the conversational context. 
3. User enters a prompt and sends it to the RAG service. If present, past conversational context will also be sent to the RAG.
4. Depending on if the guardrails were triggered, a cache hit in langcache occured, or if appropriate context was found in the ChromaDB instance, a response will be returned (with varying levels of latency.
5. Both the user prompt and response will be shortened and appended to the past_conv part of the session token/context. 
6. A background async function will save the last conversation to the Redis Agent Memory instance. (Also encrypts the conversation for user protection). Depending on how it's configured, it could save the messages every once in a while or mass saves them every x times the assistant responds.  

### General directory structure (folders only)
* prototypes -- various versions of notebooks used to prototype the RAGs. All of them are a direct iteration from the previous file. 
  * v0 -- the basic RAG. Mostly copied from the tutorial.
  * v1 -- added the llama-prompt-guard transformer as a guardrail.
  * v2 -- added the custom transformer for suicide detection.
  * v3 -- added the redis session storage & some architectural improvements.
  * v4 -- added cryptographer for AES-GCM encryption/decryption of redis session storage & some architectural improvements.
  * v5 -- architectural changes (like object factory and registry), comments, class descriptions, more robust error handling. At least according to Gemini Flash, a highly production worthy project
    (unfortunately, I don't have access to any professionals to help me judge that aren't busy).
  * v6 -- major architecural adjustments (seperate RAG and context retrieval into two services). Adds redis langcache to quickly retrieve FAQs. Highly scalable and production ready
* analytics -- contains sample analytics about the RAG agent's performance.
* backend -- python code for the deployable, fastapi version of the backend
  * api -- assets for the api (routers & schemas)
    * routes -- routers used for backend
    * schemas -- pydantic data schemas used for responses and requests
  * config -- configuration files for theregistr and transformer
    * registry_config -- configuration files for object registry
    * transformer_config -- configuration files for the custom, fine-tuned transformers
  * infrastructure -- infrastructure logic code
    * databases -- classes that interace with databases
  *  services -- python scripts for business logic services
     * rag -- business logic related to the RAG
       * guardrails -- python files for guardrails
     * context_manager -- business logic related to the context manager
  * tests -- notebooks and python files used to test the backend
* fine_tuning -- notebooks used for finetuning elements and testing of the RAG

### Env file structure
The .env file for this project should include the following:
* REDIS_CACHE_API
* REDIS_LANGCACHE_URL
* REDIS_LANGCACHE_CACHE_ID
* REDIS_STORE_ID
* REDIS_ENDPOINT
* REDIS_API_KEY
* CHROMA_API_KEY
* CHROMA_TENANT
* GEMINI_API
* HUGGING_SECRET

### Prerequesites for running the backend
* Redis Langcache and Agent Memory instance and all of its relevant information for the .env file.
 * make sure the langcache isn't empty
* Gemini api key
* Chromadb instance and all of its relevant information for the .env file
* Hugging face secrets
* your own configuration files for the transformer (because my models.safetensors file is too big for github) or change it to use a pipeline instead

### Instructions for running the backend
1. clone the repository and change directory to backend
2. use venv to create a virtual python environment.
3. use pip install -r requirements.txt
4. use the hugging face secret to authenticate using hf auth login --token "{hugging_secret}"
5. python -m main

After following these steps, the fastapi backend should be active. I haven't made a frontent for this project, so the main method of communication would be to use the notebook in /backend/tests to communicate with the backend. 

For testing the project, perhaps use python -m tests.endpoint_test to verify that each of the endpoints are behaving just as expected
