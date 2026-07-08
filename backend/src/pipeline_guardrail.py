from transformers import pipeline
from guardrail import Guardrail
import logging

"""
The guardrail subclass that uses pipelines intead of transformers. Currently used for
prompt injection detection.
"""
class Pipeline_Guardrail(Guardrail):
  """
  Constructor for the Pipeline_Guardrail that tkes in response, desired_output, and pipeline.
  Desired output is the non-problematic output. Pipeline is the specific pipeline object.
  """
  def __init__(self, response: str, desired_output: str, pipeline=None):
    #accesses superclass methods
    super().__init__(response)

    self.pipeline = pipeline
    self.desired_output = desired_output

  """
  Sets the pipeline to an existing pipeline from hugging face. The parameters are model_type
  (the specific type of pipeline) and the model name. The model_type should be a
  custom class imported from the transformers module.
  """
  def set_pipeline(self, model_type, model_name: str) -> None:
    try:
      self.pipeline = pipeline(model_type, model=model_name)
    except ValueError:
      self.logger.error(f"Invalid model type or model name provided: {model_type}, {model_name}")
      raise ValueError("Invalid model type or model name provided.")
    except Exception as e:
      self.logger.error(f"An unexpected error occurred while setting the pipeline: {str(e)}")
      raise RuntimeError("An unexpected error occurred while setting the pipeline.") from e

  """
  Returns output from pipeline and sees if it the output is the desired output.
  (Desired output being the non-problematic result). If the output is problematic,
  it will return true and later trigger an error.
  """
  async def test_input_logic(self, prompt: str) -> bool:
    try:
      guard_test = self.pipeline(prompt)
      return guard_test[0]['label'] != self.desired_output
    except Exception as e:
      self.logger.error(f"An unexpected error occurred while testing the input: {str(e)}")
      raise RuntimeError("An unexpected error occurred while testing the input.") from e