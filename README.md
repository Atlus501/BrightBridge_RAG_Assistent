# BrightBridge_RAG_Assistent
This will be my first RAG project. The LLM will be one of OpenAI's and I'm going to use fine-tuned transformers to detect suspicious prompts

### Architectural Choices
The below image is a high level view of the architecure.
<img width="797" height="470" alt="image" src="https://github.com/user-attachments/assets/2f8d6aa4-dbaf-4196-a25c-d403aba3e54d" />
* the overall system is seperated into two microservices:
 * the naive RAG system that has been enhanced by adding Redis Langcache and transformer guardrails.
 * the user context manager that retrieves user conversation snippets from Redis Agent Memory.

Explanation of User Context Manager 
 * Redis Agent Memory -- a good Redis Cloud service for storing and retrieving user session information. Having this information on hand could enhance the LLM's response by providing additional context. An optimization is that only small portions of the user's conversations would be stored at a time. Storing too much data could lead to latency and diminishing returns on the benefits of the context. To balance utility and privacy, the session memories would only have a ttl of one day. 
 *  Cryptographer -- a class responsible for encrypting/decrypting conversation snippets using AES-GCM. Due to the senstive nature of the stored data, it is imperative that they are properly secured. If I just retrieve session information through session_ids, then that would lead to a Broken Object Level Authorization, where attackers could brute force session_ids until they find valid ones. The solution to that is encrypting user data with a password. In that case, the attacker would need to guess both a valid session_id and password, which is much more unlikely. The reason why I picked AES-GCM is that it's the industry standard for symmetrical encryption. 

* When the FastAPI backend initially starts, all dependencies will be created and injected into these service classes. 

### General File Structure
* analytics -- folder that contains sample analytics about the RAG agent's performance.
* RAG_enhanced_LLMs -- folder that contains the various versions of notebooks used to prototype the RAGs. All of them are a direct iteration from the previous file. 
  * v0 -- the basic RAG. Mostly copied from the tutorial.
  * v1 -- added the llama-prompt-guard transformer as a guardrail.
  * v2 -- added the custom transformer for suicide detection.
  * v3 -- added the redis session storage & some architectural improvements.
  * v4 -- added cryptographer for AES-GCM encryption/decryption of redis session storage & some architectural improvements.
  * v5 -- architectural changes (like object factory and registry), comments, class descriptions, more robust error handling. At least according to Gemini Flash, a highly production worthy project
    (unfortunately, I don't have access to any professionals to help me judge that aren't busy).
  * v6 -- major architecural adjustments (seperate RAG and context retrieval into two services). Adds redis langcache to quickly retrieve FAQs. Highly scalable and production ready
* fine_tuning -- folder that contains the notebook used for finetuning elements of the RAG.
* backend -- folder that contains the python code for the deployable, fastapi version of the backend
  * tests -- folder that contains the notebook and python files used to test the backend

###Env file structure
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

###Instructions for running the backend
If one is running the backend version of this project, I'd recommend the following steps:
1. clone the repository and change directory to backend
2. use venv to create a virtual python environment.
3. use pip install -r requirements.txt
4. use the hugging face secret to authenticate using hf auth login --token "{hugging_secret}"
5. python -m main
6. in another terminal, use ngrok http 8080

After following these steps, the fastapi backend should be active. I haven't made a frontent for this project, so the main method of communication would be to use the notebook in /backend/tests to communicate with the backend. 
