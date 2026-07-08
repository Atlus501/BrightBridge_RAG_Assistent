import logging

from src.guardrail import Guardrail

"""
Class for guardrails that uses transformers and tokenizers instead of pipelines.
There are two ways to set the tokenizer and transformer model (composition through
the constructor and a method to upload a model using downloaded weights and config files)
"""
class Transformer_Guardrail(Guardrail):
  """
  Constructor for transformer_guardrails class. One can input a custom response when
  the guardrail detects problematic inputs, a desired output that indicates non problematic
  inputs during test_input_logic, and a model and tokenizer object.
  """
  def __init__(self, response: str, desired_output: str, model=None, tokenizer=None):
    super().__init__(response)
    self.model = model
    self.tokenizer = tokenizer

    try:
      self.desired_output = int(desired_output) # Ensure desired_output is an integer for comparison
    except ValueError:
      self.logger.error("desired_output must be an integer.")
      raise ValueError("desired_output must be an integer.")

  """
  Method for uploaing models using downloaded config files and weights. Developers can
  specify a specific hugging face model and tokenizer type to use. Plus, devs can also
  specify the path where the config and weights files are located.
  """
  def upload_model(self, model_type, tokenizer_type, path) -> None:
    try:
      self.model = model_type.from_pretrained(path)
      self.tokenizer = tokenizer_type.from_pretrained(path)

    except ValueError:
      self.logger.error("Invalid path provided.")
      raise ValueError("Invalid path provided.")
    except Exception as e:
      self.logger.error(f"An unexpected error occurred while uploading the model: {str(e)}")
      raise RuntimeError("An unexpected error occurred while uploading the model.") from e

  """
  Async function that returns output from transformer and outputs a result of
  if the transformer finds the prompt problematic. If the output is problematic,
  it will return true and later trigger an error.
  """
  async def test_input_logic(self, prompt: str) -> bool:
    try:
      tokenize_prompt = self.tokenizer(prompt, padding=True, truncation=True, return_tensors="pt")
      self.model.eval()

      with torch.no_grad():
        suicide_test = self.model(**tokenize_prompt)
        return bool(suicide_test['logits'].argmax() != self.desired_output)

    except Exception as e:
      self.logger.error(f"An unexpected error occurred while testing the input: {str(e)}")
      raise RuntimeError("An unexpected error occurred while testing the input.") from e