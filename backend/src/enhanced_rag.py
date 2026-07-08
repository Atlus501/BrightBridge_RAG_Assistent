import asyncio
import logging
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.guardrails.guardrail import Guardrail

"""
Class for the RAG. This is the class where all dependencies should be injected and flow to.
The soul of the software and the main function is the invoke method. All other ones
are setting dependencies or handling service logic.
"""
class Enhanced_RAG_v6:
  """
  Initializes RAG with the necessary dependencies. These dependencies include the LLM,
  prompt template, retriever, and the char_store_limit.
  """
  def __init__(self, llm, retriever, prompt_template, char_store_limit=128):

    # Create Prompt Instance from template
    custom_rag_prompt = PromptTemplate.from_template(prompt_template)
    self.char_store_limit = char_store_limit
    self.guardrails = []
    self.cache = None
    self.logger = logging.getLogger(__name__)

    self.rag_chain = (
    {
        "context": lambda x: self.format_docs(retriever.invoke(x["input"])),
        "query": lambda x: x["input"],
        "chat_history": lambda x: x["chat_history"],
    }
    | custom_rag_prompt
    | llm
    | StrOutputParser()
    )

  """
  Adds the cache manager
  """
  def set_cache(self, cache):
    self.cache = cache

  """
  Searches the cache for a response to the prompt. The purpose is to efficiently answer FAQs
  """
  async def search_cache(self, prompt):
    if self.cache == None:
      warnings.warn("no cache is present")
      return None

    try:
      res = await self.cache.search_prompt(prompt)

      if res.data == []:
        return None
      else:
        return res.data[0].response
    except Exception as e:
      self.logger.error(f"An issue as occured while trying to retrieve data from the cache: {str(e)}")
      raise RuntimeError("An issue as occured while trying to retrieving data from the cache") from e

  """
  Adding the assets for the guardrails
  """
  def set_guardrails(self, guardrails: list[Guardrail]):

    for guardrail in guardrails:
      if not isinstance(guardrail, Guardrail):
        raise ValueError("Guardrails must be a list of Guardrails")

    self.guardrails = guardrails

  """
  Create Document Parsing Function to String
  """
  def format_docs(self, docs):
      return "\n\n".join(doc.page_content for doc in docs)

  """
  Verifies input types for invoke
  """
  def verify_input_types(self, prompt, past_conv):
    #type checking each output to ensure predictable outputs
    if not isinstance(prompt, str):
      raise TypeError(f"Please input the prompt as a string: {prompt}")
    for conv in past_conv:
      if not isinstance(conv, str):
        raise TypeError(f"Please input the past_conv as a list of strings: {conv}")

  """
  Function for invoking the RAG.
  Params: prompt, actor_id, password, past_conv
  Returns: response
  """
  async def use_rag(self, prompt, past_conv):
    return await self.rag_chain.ainvoke({"input" : prompt, "chat_history" : past_conv})

  """
  Invokes the prompt. Takes in the prompt, actor id, password, and session id from users.
  Then, verifies the prompt using the asynchronous guardrails. Just processes the output
  through the guardrails and then passing it to the RAG.
  """
  async def invoke(self, prompt: str, past_conv = []):
    try:
      #code for handling malicious prompts and inputs
      self.verify_input_types(prompt, past_conv)

      #activates tests for each guardrail asynchronously and the guardrails will
      #raise exceptions if they find anything wrong
      async with asyncio.TaskGroup() as tg:
        for guardrail in self.guardrails:
            task = tg.create_task(guardrail.test(prompt))

      #searches the cache for a response to the prompt
      cache_response = await self.search_cache(prompt)

      if cache_response != None:
        return cache_response

      response = await self.use_rag(prompt, past_conv)
      return response

    # If a guardrail raised an exception, it will be in the ExceptionGroup
    # We expect only one for simplicity here, but a more robust system might iterate.
    except TypeError as e:
      self.logger.error(f"Invalid values were used when the RAG is triggered: {str(e)}")
      return str(e)
    except ExceptionGroup as eg:
      if eg.exceptions and isinstance(eg.exceptions[0], Exception):
        self.logger.error(f"An unexpected error occurred while invoking the RAG: {str(eg.exceptions[0])[:50]}...")
        return str(eg.exceptions[0])
      else:
        # Fallback if the ExceptionGroup doesn't contain a simple Exception
        self.logger.error(f"An unexpected error occurred while invoking the RAG: {str(eg)}")
        return str(eg)
    except RuntimeError as e:
      self.logger.error(f"An unexpected runtime error occurred while invoking the RAG: {str(e)}")
      return str(e)
    except Exception as e:
      self.logger.error(f"An unexpected miscellaneous error occurred while invoking the RAG: {str(e)}")
      return str(e)