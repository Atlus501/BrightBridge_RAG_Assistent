# BrightBridge_RAG_Assistent
This will be my first RAG project. The LLM will be one of OpenAI's and I'm going to use fine-tuned transformers to detect suspicious prompts

General File Structure
* analytics -- folder that contains sample analytics about the RAG agent's performance.
* RAG_enhanced_LLMs -- folder that contains the various versions of notebooks used to prototype the RAGs.
* fine_tuning -- folder that contains the notebook used for finetuning elements of the RAG.

The folder "RAG_enhanced_LLMs" has various versions of the RAG at various levels of security/utility. All of the files end with vX (with X being the version number). Each version will be an iteration on the direct previous version (e.g., v3 will have all the improvements from v1 to v2). All versions will includes the embedder (since the embedders use most of the same dependencies and the dependencies take a while to load)
* v0 -- the basic RAG. Mostly copied from the tutorial.
* v1 -- added the llama-prompt-guard transformer as a guardrail.
* v2 -- added the custom transformer for suicide detection.
* v3 -- added the redis session storage & some architectural improvements.
* v4 -- added cryptographer for AES-GCM encryption/decryption of redis session storage & some architectural improvements.
* v5 -- architectural changes (like object factory and registry), comments, class descriptions, more robust error handling. At least according to Gemini Flash, a highly production worthy project
  (unfortunately, I don't have access to any professionals to help me judge that aren't busy).
* v6 -- major architecural adjustments (seperate RAG and context retrieval into two services). Adds redis langcache to quickly retrieve FAQs. Highly scalable and production ready

I'm keeping all the versions because depending on my needs (the tradeoff between security, utility, and speed), I may choose to adapt different versions of the RAG_enhanced_LLM. 

Transformer_Fine_Tuner is the notebook used for loading and finetuning transformers & loading and processing datasets from hugging face. 
