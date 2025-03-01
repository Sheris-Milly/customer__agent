# models/deepseek_model.py
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.llms import HuggingFacePipeline
import torch
import logging
from config import MODEL_NAME, MAX_LENGTH, TEMPERATURE

logger = logging.getLogger(__name__)


def load_deepseek_model(model_name=MODEL_NAME):
    """
    Load the DeepSeek R1 model and return a LangChain LLM.
    """
    try:
        logger.info(f"Loading model: {model_name}")

        # Set device to CPU if no GPU is available
        device_map = "auto" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=dtype,
            device_map=device_map,
            low_cpu_mem_usage=True
        )

        # Create text generation pipeline
        hf_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=MAX_LENGTH,
            temperature=TEMPERATURE
        )

        # Wrap in LangChain
        return HuggingFacePipeline(pipeline=hf_pipeline)

    except Exception as e:
        logger.error(f"Error loading DeepSeek model: {str(e)}")
        raise


# Initialize the model
try:
    llm = load_deepseek_model()
    logger.info("DeepSeek model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    # Provide a fallback for testing
    import os

    if os.environ.get("TESTING") == "1":
        from langchain.llms import FakeListLLM

        llm = FakeListLLM(responses=["This is a test response from the fallback model."])
        logger.warning("Using fallback test model")
    else:
        raise