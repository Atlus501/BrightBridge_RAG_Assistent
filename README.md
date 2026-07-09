# BrightBridge_RAG_Assistent
This will be my first RAG project. The LLM will be one of OpenAI's and I'm going to use fine-tuned transformers to detect suspicious prompts

General File Structure
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

If one is running the backend version of this project, I'd recommend the following steps:
1. clone the repository and change directory to backend
2. use venv to create a virtual python environment.
3. use pip install -r requirements.txt
4. use the hugging face secret to authenticate using hf auth login --token "{hugging_secret}"
5. python -m main
6. in another terminal, use ngrok http 8080

After following these steps, the fastapi backend should be active. I haven't made a frontent for this project, so the main method of communication would be to use the notebook in /backend/tests to communicate with the backend. 
