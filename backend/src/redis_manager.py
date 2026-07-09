from redis_agent_memory import AgentMemory, models
from redis_agent_memory.utils import parse_datetime
from datetime import datetime, timezone
import logging
import os

"""
This is the class for managing the redis database. In the workflow, this is essential
to provide valuable context to the LLM for higher quality responses. It has two
functions -- posting and retrieving session memory.
"""
class Redis_Manager:

  """
  Constructor for redis manager. It's only parameter is the number of recent messages
  to be shown in the context, for optimization purposes. The default value is 3.
  The other parameters are set by configuration files.
  """
  def __init__(self, num_recent_messages=3, cryptographer=None):
    #taking setting information from configuration files
    self.endpoint = os.getenv("REDIS_ENDPOINT")
    self.store_id = os.getenv("REDIS_STORE_ID")
    self.api_key = os.getenv("REDIS_API_KEY")
    self.logger = logging.getLogger(__name__)

    self.num_recent_messages = num_recent_messages
    self.cryptographer = cryptographer

  """
  Encrypts the message
  """
  def encrypt_message(self, password, message):
    if self.cryptographer == None:
      self.logger.warn("A cryptographer is not present.")
      warnings.warn("A cryptographer is not present. Privacy may be compromised")
      return message

    return self.cryptographer.encrypt(password, message)

  """
  Decrypts the message
  """
  def decrypt_message(self, password, message):
    if self.cryptographer == None:
      self.logger.warn("A cryptographer is not present.")
      warnings.warn("A cryptographer is not present. Privacy may be compromised")
      return message

    return self.cryptographer.decrypt(password, message)

  """
  The asynchronous function that posts conversations memory to the redis database.
  It takes in the actor_id, message, role, and session id as inputs (with the last two
  being optional). The function will always output a valid session id to be reused
  in the future. ValueErrors may trigger if the provided session_id is invalid.
  RuntimeErrors may trigger for miscellaneous errors.
  """
  async def post_session_memory(self, actor_id, message, role="user", session_id=None):
    #setting the message role
    message_role = models.MessageRole.USER if role == "user" else models.MessageRole.ASSISTANT

    if isinstance(message, list):
      message = '/n'.join(message)

    #api call for saving the session
    try:
      async with AgentMemory(self.endpoint, store_id=self.store_id, api_key=self.api_key) as agent_memory:
          content = [{"text": message,},]

          res = await agent_memory.add_session_event_async(actor_id=actor_id, role=message_role, session_id=session_id,
              content=content, created_at=parse_datetime(datetime.now(timezone.utc).isoformat()))

          return res.event.session_id

    except ValueError as e:
      self.logger.error(f"A problem has occured during message saving to the redis database: {str(e)}")
      raise ValueError(f"A problem has occured during message saving to the redis database") from e
    except Exception as e:
      self.logger.error(f"A problem has occured during message saving to the redis database: {str(e)}")
      raise RuntimeError(f"A problem has occured during message saving to the redis database") from e

  """
  The asynchronous function that retrieves past conversations from the redis database.
  Its inputs are the actor id and optional session id. Use session_id=None if no session
  has been started yet. Please reuse session_ids that are returned from the posting function.
  This function will return a list of event contents and session_id of the retrieved
  message.
  """
  async def get_session_memory(self, actor_id, session_id = None):
    # If session_id is None, it means no session has been started yet by the user.
    # So we return empty and let Enhanced_RAG_v4 handle the creation.
    if session_id is None:
      return [], None # Return an empty list for raw messages

    try:
    #api for getting conversations from the redis database
      async with AgentMemory(self.endpoint, store_id=self.store_id, api_key=self.api_key) as agent_memory:

        res = await agent_memory.get_session_memory_async(session_id=session_id)

        # Safe validation fallback
        if not res or not hasattr(res, 'events') or not res.events:
            return [], session_id # If session_id was provided but no events, return empty list

        # Retrieve only the last N messages to optimize context length and processing
        recent_events = res.events[-self.num_recent_messages:]

        # Return a list of raw text content (which are encrypted strings)
        events_content = []
        for event in recent_events:
            events_content.append(event.content[0].text)

        return events_content, session_id

    except IndexError as e:
      self.logger.error(f"A problem has occured during message retrieval from the redis database: {str(e)}")
      raise ValueError(f"A problem has occured during message retrieval from the redis database") from e
    except ValueError as e:
      self.logger.error(f"A problem has occured during message retrieval from the redis database: {str(e)}")
      raise ValueError(f"A problem has occured during message retrieval from the redis database") from e
    except Exception as e:
      # If an error occurs when trying to fetch an existing session_id,
      # it might mean the session_id is invalid or expired.
      # In this case, treat it as if no context was found for that session_id.
      self.logger.error(f"An unexpected error occurred during message retrieval for session {session_id}: {str(e)}", exc_info=True)
      raise RuntimeError(f"Failed to retrieve session memory") from e

  """
  Gets the context from the database
  """
  async def get_context(self, actor_id, password, session_id):

    try:
      # This will now return a list of encrypted strings or an empty list
      raw_events_content_list, retrieved_session_id = await self.get_session_memory(actor_id, session_id=session_id)

      decrypted_history_parts = []
      if not raw_events_content_list:
        return "", retrieved_session_id
      else:
        # Iterate and decrypt existing messages
        for encrypted_msg_str in raw_events_content_list:
          try:
            decrypted_msg = self.decrypt_message(password, encrypted_msg_str)
            decrypted_history_parts.append(decrypted_msg)
          except ValueError as e:
            self.logger.error(f"Decryption failed due to authentication tag mismatch or invalid data: {e}")
            raise ValueError("Decryption failed due to authentication tag mismatch or invalid data.") from e

        return decrypted_history_parts, retrieved_session_id

    except Exception as e:
      self.logger.error(f"An unexpected error occurred while getting the context: {str(e)}")
      raise RuntimeError("An unexpected error occurred while getting the context.") from e

  """
  Saves the context to the database
  """
  async def save_context(self, actor_id, message, password, role="user", session_id=None):
    if isinstance(message, list):
      message = '/n'.join(message)

    encrypted_string = self.encrypt_message(password, message)
    return await self.post_session_memory(actor_id, encrypted_string, role, session_id=session_id)