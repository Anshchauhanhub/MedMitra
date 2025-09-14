# Gemini API Setup Guide

This guide will help you set up the Google Gemini API for use with MedMitra.

## Getting a Google AI Studio API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click on "Get API Key" button
4. Create a new API key or use an existing one
5. Copy the API key for use in MedMitra

## Alternative Free LLM APIs

If you prefer alternatives to Google's Gemini API, here are some options with free tiers:

### Together.ai
- Visit [Together.ai](https://www.together.ai/)
- Sign up for an account
- Navigate to API section to get a free API key
- Free credits for using Llama 3 and other models

### Hugging Face
- Visit [Hugging Face](https://huggingface.co/)
- Create an account and get an API token
- Use Inference API with free usage limits

### Groq
- Visit [Groq](https://console.groq.com/)
- Sign up for an account
- Get a free API key with usage limits
- Known for fast inference times

### Cohere
- Visit [Cohere](https://cohere.com/)
- Sign up for an account
- Get a free API key with limited usage
- Good for text generation and embeddings

## Setting Up Environment Variables

1. Create a `.env` file in the root directory of your project
2. Add your API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

3. If using an alternative LLM, add the appropriate API key:
```
OPENAI_API_KEY=your_openai_api_key_here
# OR
TOGETHER_API_KEY=your_together_api_key_here
# OR
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

## Modifying the Code for Alternative LLMs

If you decide to use an alternative LLM, you'll need to modify the `actions/actions.py` file. Examples for different LLMs are provided in the `examples` directory.