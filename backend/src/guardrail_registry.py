"""
Class for registering guardrails
"""
class Guardrail_Registry:
  def __init__(self):
    self.registry = {}

  """
  Register a callable (e.g., a factory method or lambda) that creates a guardrail.
  """
  def register_guardrail_creator(self, guardrail_type: str, creator_function: callable):
    self.registry[guardrail_type] = creator_function

  """
  Get the creator function, which can then be called with specific arguments.
  """
  def get_guardrail_creator(self, guardrail_type: str) -> callable:
    if guardrail_type not in self.registry:
      raise ValueError(f"Guardrail type '{guardrail_type}' not registered.")
    return self.registry[guardrail_type]