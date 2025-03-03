import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict, Any, Optional, Tuple

from config import MODEL_NAME, MAX_LENGTH, TEMPERATURE

# Configure logging
logger = logging.getLogger(__name__)


class DeepSeekModel:
    """
    A wrapper for the DeepSeek model that handles text generation and model loading.
    """

    def __init__(self):
        """Initialize the DeepSeek model."""
        logger.info(f"Initializing DeepSeek model: {MODEL_NAME}")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            logger.debug("Tokenizer loaded successfully")

            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.debug(f"Using device: {device}")

            # Load the model
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
                device_map=device
            )
            logger.info(f"Model loaded successfully on {device}")

        except Exception as e:
            logger.error(f"Error loading DeepSeek model: {str(e)}")
            raise RuntimeError(f"Failed to load DeepSeek model: {str(e)}")

    def generate_response(
            self,
            prompt: str,
            system_prompt: Optional[str] = None,
            max_length: int = MAX_LENGTH,
            temperature: float = TEMPERATURE,
            context: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response from the model based on the given prompt.

        Args:
            prompt: The user's input prompt
            system_prompt: Optional system prompt to guide the model's behavior
            max_length: Maximum length of the generated response
            temperature: Temperature parameter for generation (higher = more creative)
            context: List of previous conversation messages

        Returns:
            The generated text response
        """
        try:
            logger.debug(f"Generating response for prompt: {prompt[:50]}...")

            # Prepare the conversation history if provided
            messages = []

            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add conversation history if provided
            if context:
                messages.extend(context)

            # Add the current user prompt
            messages.append({"role": "user", "content": prompt})

            # Format the conversation for the model
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # Tokenize the prompt
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)

            # Generate the response
            with torch.no_grad():
                output = self.model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decode the response, skipping the input prompt
            response_ids = output[0][inputs.input_ids.shape[1]:]
            response = self.tokenizer.decode(response_ids, skip_special_tokens=True)

            logger.debug(f"Generated response: {response[:50]}...")
            return response.strip()

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I'm having trouble processing your request. Please try again later. (Error: {str(e)})"