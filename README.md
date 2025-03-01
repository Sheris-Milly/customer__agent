# DeepSeek R1 Customer Service Chatbot

A fully open-source customer service chatbot built with DeepSeek R1, LangChain, FastAPI, and Streamlit.

## Features

- 100% open-source components - no API keys required
- DeepSeek R1 Distill Qwen 1.5B language model
- FAQ vector search with HuggingFace embeddings
- Order tracking tool
- Conversation memory
- FastAPI backend and Streamlit UI

## Requirements

- Python 3.9+
- CUDA-capable GPU recommended (but will fall back to CPU)
- 16GB+ RAM recommended

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/deepseek-customer-service.git
cd deepseek-customer-service
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the API Server

```bash
python app.py
```

### Start the Streamlit UI (in a separate terminal)

```bash
streamlit run chatbot_ui.py
```

## Project Structure

- `app.py`: FastAPI server entry point
- `chatbot_ui.py`: Streamlit user interface
- `config.py`: Configuration settings
- `models/`: Model loading and management
- `services/`: Core services (FAQ, memory, order tracking)
- `chatbot_agents/`: LangChain agent setup

## Customization

### Adding New FAQs

Edit the `data/faqs.json` file to add new questions and answers.

### Using a Different Model

Change the `MODEL_NAME` in `config.py` to use a different HuggingFace model.

## Troubleshooting

- **Memory Issues**: Reduce model size or enable model offloading in `models/deepseek_model.py`
- **Slow Responses**: Ensure you're using a GPU or try a smaller model
- **API Connection Errors**: Verify the API is running and check the URL in the Streamlit app

## License

MIT License