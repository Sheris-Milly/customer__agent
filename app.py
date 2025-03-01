from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
model = AutoModelForCausalLM.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")



# Generate response
input_text = "Hello, how can you assist me?"
inputs = tokenizer(input_text, return_tensors="pt")
output = model.generate(**inputs, max_length=50)
response = tokenizer.decode(output[0], skip_special_tokens=True)

print(response)
