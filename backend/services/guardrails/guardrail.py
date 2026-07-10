import logging

"""
This is the superclass that all guardrails should inherit from.
It is kept intentionally minimal to ensure maximum adaptability for future changes.
The only notable method is that when test(prompt) is called, it will try to use
the test_input(prompt) function to test the input. If the input is true, it will raise
an exception in test(prompt). The specific response will be configured in the constructor.
The intention is that subclasses will adjust test_input_logic(prompt)
to fit their specific needs. The Keep in mind that both the test and test_input_logic
functions are async functions.
"""
class Guardrail:
  """
  Constructor for the guardrail. The response input is going to be the customized message
  that's going to be outputted if the guardrail detects a problem.
  """
  def __init__(self, response: str):
    self.response = response
    self.logger = logging.getLogger(__name__)

  """
  Intentionally customized asynchronous test_input function that tests user prompts.
  """
  async def test_input_logic(self, prompt: str) -> bool:
    return False

  """
  Asyncrhonous function that is going to inherited in all subclasses. This function
  will be called whenever the RAG wants the guardrail to test a prompt.
  """
  async def test(self, prompt: str) -> None:
    positive_test = await self.test_input_logic(prompt)
    if positive_test:
      self.logger.error(f"The user has submitted a problmatic input: {prompt}")
      raise ValueError(self.response)