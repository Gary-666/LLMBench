# AIMS For Every API

A conversation testing framework for multiple AI APIs using the OpenAI client format.

## Overview

This project provides a comprehensive framework to test and evaluate the conversational capabilities of various AI APIs:
1. Monica AI API
2. OpenAI API
3. Google Gemini API

The framework allows for interactive conversations, side-by-side comparisons, and batch testing across all APIs, with metrics collection and analysis.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with your API keys:

```
MONICA_KEY=your_monica_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_KEY=your_gemini_api_key
```

## Usage

### Interactive Conversation Mode

Start an interactive conversation with a specific API:

```bash
python main.py interactive
```

You'll be prompted to select which API to use (Monica, OpenAI, or Gemini). Then you can have a multi-turn conversation with the selected API.

### Compare APIs

Compare responses from all APIs for the same prompt:

```bash
python main.py compare --prompt "What is the future of AI?"
```

### Batch Testing

Run a series of predefined test cases across all APIs:

```bash
python main.py batch
```

Or provide your own test cases in a JSON file:

```bash
python main.py batch --file test_cases.json
```

Example test_cases.json format:
```json
[
  {
    "prompt": "What is artificial intelligence?"
  },
  {
    "prompt": "Explain quantum computing",
    "image_url": "https://example.com/quantum.jpg"
  }
]
```

### Test a Specific API

```bash
python main.py monica  # Test only Monica API
python main.py openai  # Test only OpenAI API
python main.py gemini  # Test only Gemini API
```

### Custom Prompts

Use a custom text prompt:

```bash
python main.py --prompt "What is machine learning?"
```

### Text-Only Mode

Test with text-only prompts (no images):

```bash
python main.py --text-only
```

### Custom Image

Use a different image URL:

```bash
python main.py --image "https://example.com/your-image.jpg"
```

## Conversation Testing Features

### Multi-turn Conversations
The framework supports multi-turn conversations with each API, allowing for testing of context retention and conversation flow.

### Metrics Collection
For each conversation, the framework automatically collects and calculates metrics such as:
- Total conversation duration
- Number of turns
- Average response time
- Average response length

### Conversation Storage
All conversations are saved to JSON files in the `conversations` directory, allowing for later analysis and comparison.

### Summary Reports
A CSV summary report is generated for each testing session, providing an overview of all conversations and their metrics.

## Command-Line Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `api` | | Mode to run: `interactive`, `compare`, `batch`, `monica`, `openai`, `gemini`, or `all` (default: `interactive`) |
| `--prompt` | `-p` | Text prompt to send to the API |
| `--image` | `-i` | URL of an image to include in the prompt |
| `--text-only` | `-t` | Use text-only prompt (no image) |
| `--file` | `-f` | JSON file with test cases for batch mode |
| `--system` | `-s` | System message to set context for the conversation |