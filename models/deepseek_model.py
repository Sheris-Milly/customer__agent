from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.llms import HuggingFacePipeline
import torch

def load_deepseek_model(model_name: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"):
    """
    Load the DeepSeek R1 model and return a LangChain LLM.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, device_map="auto"
    )
    hf_pipeline = pipeline(
        "text-generation", model=model, tokenizer=tokenizer, max_length=512, temperature=0.7
    )
    return HuggingFacePipeline(pipeline=hf_pipeline)

llm = load_deepseek_model()
