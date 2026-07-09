from langcache import LangCache
import logging
import os

"""
This is the class that interacts with the redis LangCache to retrieve responses for FAQs.
"""
class Redis_Cache_Manager:
  """
  Constructor for the redis cache manager.
  """
  def __init__(self):
    self.logger = logging.getLogger(__name__)
    self.redis_url = os.getenv('REDIS_LANGCACHE_URL') # Renamed for clarity, this is the Redis connection URL
    self.cache_id = os.getenv('REDIS_LANGCACHE_CACHE_ID')
    self.api_key = os.getenv('REDIS_CACHE_API')
    # Explicitly define the LangCache API server URL, defaulting to the standard endpoint
    self.langcache_api_url = os.getenv('LANGCACHE_API_URL', 'https://api.langcache.io')

  """
  Inserts FAQ into database
  """
  async def insert_prompt(self, prompt, response):
    try:
      async with LangCache(
            server_url=self.redis_url, # Pass Redis URL, though it's ignored if api_key is present
            cache_id=self.cache_id,
            api_key=self.api_key,
        ) as lang_cache:

            res = await lang_cache.set_async(prompt=prompt, response=response)
            return res

    except Exception as e:
      self.logger.error(f"An unexpected error occurred while inserting the prompt: {str(e)}")
      raise RuntimeError(f"An unexpected error occurred while inserting the prompt") from e

  """
  Delete FAQ from database
  """
  async def delete_prompt(self, entry_id):
    try:
      async with LangCache(
            server_url=self.redis_url, # Pass Redis URL, though it's ignored if api_key is present
            cache_id=self.cache_id,
            api_key=self.api_key,
        ) as lang_cache:

            await lang_cache.delete_by_id_async(entry_id=entry_id)

    except Exception as e:
      self.logger.error(f"An unexpected error occurred while deleting the prompt: {str(e)}")
      raise RuntimeError(f"An unexpected error occurred while deleting the prompt") from e

  """
  Searches the database for reponses to FAQs using vectoized searches.
  """
  async def search_prompt(self, prompt):
    try:
      async with LangCache(
            server_url=self.redis_url, # Pass Redis URL, though it's ignored if api_key is present
            cache_id=self.cache_id,
            api_key=self.api_key,
        ) as lang_cache:

            res = await lang_cache.search_async(prompt=prompt,
                                                similarity_threshold=0.9)
            return res
    except Exception as e:
      self.logger.error(f"An unexpected error occurred while searching the prompt: {str(e)}")
      raise RuntimeError(f"An unexpected error occurred while searching the prompt") from e

  """
  Prints out self keys
  """
  def print_keys(self):
    print(f"url:{self.redis_url}")
    print(f"cache_id:{self.cache_id}")
    print(f"api_key:{self.api_key}")