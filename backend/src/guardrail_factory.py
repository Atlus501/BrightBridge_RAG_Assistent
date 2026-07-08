from transformers import AutoModelForSequenceClassification, AutoTokenizer
import logging
from pathlib import Path

from transformer_guardrail import Transformer_Guardrail
from pipeline_guardrail import Pipeline_Guardrail

"""
Class for guardrail factory. How this factory works is that it provides a collection of
methods that encapsulates the knowledge of how specific guardrails are created.
"""
class Guardrail_Factory:
  """
  Constructor for the guardrail factory
  """
  def __init__(self):
    self.logger = logging.getLogger(__name__)

  """
  Function for creating guardrails against prompt injections. Response is the custom
  response returned when encountering an error. Desired output is the value that indicates
  a non-problematic output. Model name is the hugging face model name.
  """
  def create_prompt_guardrail(self, response: str, desired_output: str, model_name: str) -> 'Pipeline_Guardrail':
    try:
      if not isinstance(response, str):
        raise ValueError("Responses must be strings.")
      if not isinstance(desired_output, str):
        raise ValueError("Desired outputs must be strings.")
      if not isinstance(model_name, str):
        raise ValueError("Model names must be strings.")

      guardrail = Pipeline_Guardrail(response, desired_output)
      # The pipeline type is fixed for this guardrail, but the model name is configurable
      guardrail.set_pipeline("text-classification", model_name)
      return guardrail

    except ValueError:
      self.logger.error("Invalid model name provided.")
      raise ValueError("Invalid model name provided.")
    except Exception as e:
      self.logger.error(f"An unexpected error occurred while creating the prompt guardrail: {str(e)}")
      raise RuntimeError("An unexpected error occurred while creating the prompt guardrail.") from e

  """
  Function for creating guardrails against suicide inputs. Response is the custom
  response returned when encountering an error. Desired output is the value that indicates
  a non-problematic output. Model name is the hugging face model name.
  """
  def create_suicide_guardrail(self, response: str, model_path: str, desired_output: int) -> 'Transformer_Guardrail':
    try:
      if not isinstance(response, str):
        raise ValueError("Responses must be strings.")
      if not isinstance(model_path, str):
        raise ValueError("Model paths must be strings.")
      if not isinstance(desired_output, int):
        raise ValueError("Desired outputs must be integers.")

      guardrail = Transformer_Guardrail(response, desired_output)

      # The model and tokenizer types are fixed for this type of guardrail, but the path is configurable
      if model_path is not None:
        CURRENT_DIR = Path(__file__).resolve().parent
        model_path = str(CURRENT_DIR / ".." / model_path)
        guardrail.upload_model(AutoModelForSequenceClassification, AutoTokenizer, model_path)
      return guardrail

    except ValueError:
      self.logger.error(f"Invalid path provided. {model_path}")
      raise ValueError("Invalid path provided.")
    except Exception as e:
      self.logger.error(f"An unexpected error occurred while creating the suicide guardrail: {str(e)}")
      raise RuntimeError("An unexpected error occurred while creating the suicide guardrail.") from e