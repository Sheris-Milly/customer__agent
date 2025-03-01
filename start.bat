@echo off
echo Starting DeepSeek R1 Customer Service Chatbot...

REM Set environment variables
set PYTHONPATH=%CD%
set CUDA_VISIBLE_DEVICES=0

REM Start API server in the background
start cmd /k "echo Starting API Server... && python app.py"

REM Wait a moment for the API to start
echo Waiting for API server to start...
timeout /t 5

REM Start Streamlit UI
echo Starting Streamlit UI...
streamlit run chatbot_ui.py

echo Application started.