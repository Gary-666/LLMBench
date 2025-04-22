from openai import OpenAI
import os
from dotenv import load_dotenv
import sys
import argparse
import json
import requests
import google.generativeai as genai
import PIL.Image
from io import BytesIO
import time
import httpx
import datetime
import csv
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import uuid

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
MONICA_KEY = os.getenv("MONICA_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Optional proxy settings
HTTP_PROXY = os.getenv("HTTP_PROXY", "")
HTTPS_PROXY = os.getenv("HTTPS_PROXY", "")

@dataclass
class Message:
    role: str  # 'system', 'user', or 'assistant'
    content: Union[str, List[Dict[str, Any]]]  # Text or structured content with images
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class Conversation:
    id: str
    api_name: str
    messages: List[Message]
    model: str
    start_time: float
    end_time: Optional[float] = None
    metrics: Dict[str, Any] = None
    
    def add_message(self, message: Message):
        self.messages.append(message)
        
    def end_conversation(self):
        self.end_time = time.time()
        
    def calculate_metrics(self):
        if not self.end_time:
            self.end_conversation()
            
        # Calculate basic metrics
        self.metrics = {
            'total_duration': self.end_time - self.start_time,
            'num_turns': len([m for m in self.messages if m.role == 'user']),
            'avg_assistant_response_time': self._calculate_avg_response_time(),
            'avg_assistant_response_length': self._calculate_avg_response_length()
        }
        return self.metrics
    
    def _calculate_avg_response_time(self):
        response_times = []
        for i in range(1, len(self.messages)):
            if self.messages[i].role == 'assistant' and self.messages[i-1].role == 'user':
                response_times.append(self.messages[i].timestamp - self.messages[i-1].timestamp)
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _calculate_avg_response_length(self):
        responses = [m.content for m in self.messages if m.role == 'assistant']
        if not responses:
            return 0
        lengths = [len(r) if isinstance(r, str) else sum(len(item.get('text', '')) for item in r if isinstance(item, dict) and 'text' in item) 
                  for r in responses]
        return sum(lengths) / len(lengths)
    
    def to_dict(self):
        return asdict(self)
    
    def save_to_file(self, directory='conversations'):
        os.makedirs(directory, exist_ok=True)
        filename = f"{directory}/{self.api_name}_{self.id}_{int(self.start_time)}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, default=str, ensure_ascii=False)
        print(f"Conversation saved to {filename}")
        return filename

class ConversationManager:
    def __init__(self):
        self.conversations = {}
        self.current_conversation_ids = {'monica': None, 'openai': None, 'gemini': None}
        
    def start_conversation(self, api_name, model):
        conv_id = str(uuid.uuid4())
        conversation = Conversation(
            id=conv_id,
            api_name=api_name,
            messages=[],
            model=model,
            start_time=time.time()
        )
        self.conversations[conv_id] = conversation
        self.current_conversation_ids[api_name] = conv_id
        return conv_id
    
    def add_message(self, conv_id, message):
        if conv_id in self.conversations:
            self.conversations[conv_id].add_message(message)
            return True
        return False
    
    def get_conversation(self, conv_id):
        return self.conversations.get(conv_id)
    
    def get_current_conversation(self, api_name):
        conv_id = self.current_conversation_ids.get(api_name)
        if conv_id:
            return self.conversations.get(conv_id)
        return None
    
    def end_conversation(self, conv_id):
        if conv_id in self.conversations:
            self.conversations[conv_id].end_conversation()
            return True
        return False
    
    def save_all_conversations(self, directory='conversations'):
        os.makedirs(directory, exist_ok=True)
        saved_files = []
        for conv_id, conversation in self.conversations.items():
            if not conversation.end_time:
                conversation.end_conversation()
            conversation.calculate_metrics()
            saved_files.append(conversation.save_to_file(directory))
        
        # Create a summary CSV
        self._create_summary_csv(directory)
        return saved_files
    
    def _create_summary_csv(self, directory):
        csv_file = f"{directory}/summary_{int(time.time())}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'api_name', 'model', 'start_time', 'end_time', 
                         'total_duration', 'num_turns', 'avg_assistant_response_time', 
                         'avg_assistant_response_length']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for conv in self.conversations.values():
                if not conv.metrics:
                    conv.calculate_metrics()
                
                row = {
                    'id': conv.id,
                    'api_name': conv.api_name,
                    'model': conv.model,
                    'start_time': datetime.datetime.fromtimestamp(conv.start_time).strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': datetime.datetime.fromtimestamp(conv.end_time).strftime('%Y-%m-%d %H:%M:%S') if conv.end_time else '',
                    'total_duration': round(conv.metrics.get('total_duration', 0), 2),
                    'num_turns': conv.metrics.get('num_turns', 0),
                    'avg_assistant_response_time': round(conv.metrics.get('avg_assistant_response_time', 0), 2),
                    'avg_assistant_response_length': conv.metrics.get('avg_assistant_response_length', 0)
                }
                writer.writerow(row)
        print(f"Summary saved to {csv_file}")
        return csv_file

# Initialize the conversation manager
conversation_manager = ConversationManager()

def test_monica_api(prompt="Explain this image", image_url=None, conversation_id=None):
    """Test Monica API with text or image prompt"""
    print("\n=== Testing Monica API ===")
    # Set up proxies if available
    proxies = {}
    if HTTP_PROXY:
        proxies["http"] = HTTP_PROXY
    if HTTPS_PROXY:
        proxies["https"] = HTTPS_PROXY

    if proxies:
        print(f"Using proxies: {proxies}")
        # Set environment variables for requests
        os.environ["HTTP_PROXY"] = proxies.get("http", "")
        os.environ["HTTPS_PROXY"] = proxies.get("https", "")

    # Prepare client with proxy support
    try:
        # Create a custom httpx client with proxy support
        http_client = None
        if proxies:
            proxy_url = proxies.get("https") or proxies.get("http")
            if proxy_url:
                http_client = httpx.Client(proxies={"http://": proxy_url, "https://": proxy_url})
        
        client = OpenAI(
            base_url="https://openapi.monica.im/v1",
            api_key=MONICA_KEY,
            http_client=http_client,
            timeout=30.0  # Add timeout parameter
        )
        
        # Get or create conversation
        model = "gpt-4o"
        if conversation_id:
            conversation = conversation_manager.get_conversation(conversation_id)
        else:
            conversation_id = conversation_manager.start_conversation('monica', model)
            conversation = conversation_manager.get_conversation(conversation_id)
        
        # Prepare content based on whether image is provided
        if image_url:
            content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                }
            ]
        else:
            content = prompt
        
        # Add user message to conversation
        user_message = Message(role="user", content=content)
        conversation.add_message(user_message)
        
        # Prepare messages for API call
        api_messages = [{"role": msg.role, "content": msg.content} for msg in conversation.messages]
        
        # Make API call
        start_time = time.time()
        completion = client.chat.completions.create(
            model=model,
            messages=api_messages
        )
        
        # Add assistant response to conversation
        assistant_message = Message(
            role="assistant", 
            content=completion.choices[0].message.content,
            timestamp=time.time()
        )
        conversation.add_message(assistant_message)
        
        print("\nMonica API Response:")
        print(completion.choices[0].message.content)
        return completion, conversation_id
    except Exception as e:
        print(f"\nError with Monica API: {str(e)}")
        # Print more detailed error information
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        # Return a tuple with None values to maintain the expected return format
        return None, None

def test_openai_api(prompt="What is the capital of France?", image_url=None, conversation_id=None):
    """Test OpenAI API with text or image prompt"""
    print("\n=== Testing OpenAI API ===")
    # Set up proxies if available
    proxies = {}
    if HTTP_PROXY:
        proxies["http"] = HTTP_PROXY
    if HTTPS_PROXY:
        proxies["https"] = HTTPS_PROXY

    if proxies:
        print(f"Using proxies: {proxies}")
        # Set environment variables for requests
        os.environ["HTTP_PROXY"] = proxies.get("http", "")
        os.environ["HTTPS_PROXY"] = proxies.get("https", "")

    # Prepare client with proxy support
    try:
        # Create a custom httpx client with proxy support
        http_client = None
        if proxies:
            proxy_url = proxies.get("https") or proxies.get("http")
            if proxy_url:
                http_client = httpx.Client(proxies={"http://": proxy_url, "https://": proxy_url})
        
        client = OpenAI(
            api_key=OPENAI_API_KEY,
            http_client=http_client,
            timeout=30.0  # Add timeout parameter
        )
        
        # Determine model based on image presence
        if image_url:
            model = "gpt-4o"  # Model that supports vision
        else:
            model = "gpt-3.5-turbo"  # Default text model
            
        # Get or create conversation
        if conversation_id:
            conversation = conversation_manager.get_conversation(conversation_id)
        else:
            conversation_id = conversation_manager.start_conversation('openai', model)
            conversation = conversation_manager.get_conversation(conversation_id)
        
        # Prepare content based on whether image is provided
        if image_url:
            content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                }
            ]
        else:
            content = prompt
        
        # Add user message to conversation
        user_message = Message(role="user", content=content)
        conversation.add_message(user_message)
        
        # Prepare messages for API call
        api_messages = [{"role": msg.role, "content": msg.content} for msg in conversation.messages]
        
        # Make API call
        start_time = time.time()
        completion = client.chat.completions.create(
            model=model,
            messages=api_messages
        )
        
        # Add assistant response to conversation
        assistant_message = Message(
            role="assistant", 
            content=completion.choices[0].message.content,
            timestamp=time.time()
        )
        conversation.add_message(assistant_message)
        
        print("\nOpenAI API Response:")
        print(completion.choices[0].message.content)
        return completion, conversation_id
    except Exception as e:
        print(f"\nError with OpenAI API: {str(e)}")
        # Print more detailed error information
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        # Return a tuple with None values to maintain the expected return format
        return None, None

def test_gemini_api(prompt="What is the capital of Germany?", image_url=None, conversation_id=None):
    """Test Google Gemini API with text or image prompt using the official SDK"""
    print("\n=== Testing Google Gemini API ===")
    
    # Set up proxies if available
    proxies = {}
    if HTTP_PROXY:
        proxies["http"] = HTTP_PROXY
    if HTTPS_PROXY:
        proxies["https"] = HTTPS_PROXY
    
    if proxies:
        print(f"Using proxies: {proxies}")
        # Set environment variables for requests
        os.environ["HTTP_PROXY"] = proxies.get("http", "")
        os.environ["HTTPS_PROXY"] = proxies.get("https", "")
    
    try:
        # Configure the Gemini API with timeout
        genai.configure(api_key=GEMINI_KEY)
        
        # Set generation config with safety settings
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        if image_url:
            # For image prompts, use Gemini Pro Vision
            model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Download the image with timeout and retries
            max_retries = 3
            retry_delay = 2
            timeout_seconds = 30
            
            for attempt in range(max_retries):
                try:
                    print(f"Downloading image (attempt {attempt+1}/{max_retries})...")
                    response = requests.get(
                        image_url, 
                        timeout=timeout_seconds,
                        proxies=proxies if proxies else None
                    )
                    response.raise_for_status()
                    img = PIL.Image.open(BytesIO(response.content))
                    
                    print("Generating content with image...")
                    # Generate content with the image
                    result = model.generate_content([prompt, img])
                    print("\nGemini API Response:")
                    print(result.text)
                    return result
                
                except requests.exceptions.Timeout:
                    print(f"Timeout downloading image (attempt {attempt+1}/{max_retries})")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        print("Max retries reached. Falling back to text-only mode.")
                        # Fall back to text-only mode
                        fallback_prompt = f"{prompt} (Note: Image could not be processed due to timeout)"
                        model = genai.GenerativeModel(
                            model_name='gemini-pro',
                            generation_config=generation_config,
                            safety_settings=safety_settings
                        )
                        result = model.generate_content(fallback_prompt)
                        print("\nGemini API Response (text-only fallback):")
                        print(result.text)
                        return result
                
                except Exception as e:
                    print(f"Error downloading or processing image (attempt {attempt+1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        print("Max retries reached. Falling back to text-only mode.")
                        # Fall back to text-only mode
                        fallback_prompt = f"{prompt} (Note: Image could not be processed due to error: {str(e)})"
                        model = genai.GenerativeModel(
                            model_name='gemini-pro',
                            generation_config=generation_config,
                            safety_settings=safety_settings
                        )
                        result = model.generate_content(fallback_prompt)
                        print("\nGemini API Response (text-only fallback):")
                        print(result.text)
                        return result
        else:
            # For text-only prompts, use Gemini Pro
            model_name = 'gemini-1.5-flash'
            
            # Get or create conversation
            if conversation_id:
                conversation = conversation_manager.get_conversation(conversation_id)
            else:
                conversation_id = conversation_manager.start_conversation('gemini', model_name)
                conversation = conversation_manager.get_conversation(conversation_id)
            
        # Add user message to conversation
        user_message = Message(role="user", content=prompt if not image_url else f"{prompt} [Image attached]")
        conversation.add_message(user_message)
        
        # For Gemini, we need to build the conversation history
        if len(conversation.messages) > 1:
            # Create a chat session
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            chat = model.start_chat(history=[
                {"role": "user" if msg.role == "user" else "model", 
                 "parts": [msg.content]} 
                for msg in conversation.messages[:-1]  # Exclude the last message which we'll send now
            ])
            response = chat.send_message(prompt if not image_url else f"{prompt} [Image attached]")
        else:
            # First message in conversation
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            response = model.generate_content(prompt if not image_url else f"{prompt} [Image attached]")
        
        # Add assistant response to conversation
        assistant_message = Message(
            role="assistant", 
            content=response.text,
            timestamp=time.time()
        )
        conversation.add_message(assistant_message)
        
        print("\nGemini API Response:")
        print(response.text)
        return response, conversation_id
    except Exception as e:
        print(f"\nError with Gemini API: {str(e)}")
        # Return a tuple with None values to maintain the expected return format
        return None, None

def check_api_keys():
    """Check if API keys are available and print status"""
    print("\n=== API Key Status ===")
    
    if MONICA_KEY:
        print("✓ MONICA_KEY is available")
    else:
        print("✗ MONICA_KEY not found in .env file")
    
    if OPENAI_API_KEY:
        print("✓ OPENAI_API_KEY is available")
    else:
        print("✗ OPENAI_API_KEY not found in .env file")
    
    if GEMINI_KEY:
        print("✓ GEMINI_KEY is available")
    else:
        print("✗ GEMINI_KEY not found in .env file")
    
    # Check proxy settings
    if HTTP_PROXY or HTTPS_PROXY:
        print("\n=== Proxy Settings ===")
        if HTTP_PROXY:
            print(f"HTTP_PROXY: {HTTP_PROXY}")
        if HTTPS_PROXY:
            print(f"HTTPS_PROXY: {HTTPS_PROXY}")
    
    print()  # Empty line for better readability

def interactive_conversation(api_name, initial_prompt=None, image_url=None):
    """Start an interactive conversation with the specified API"""
    conversation_id = None
    print(f"\n=== Starting interactive conversation with {api_name.upper()} API ===")
    print("Type 'exit' to end the conversation.\n")
    
    # Initial prompt
    if initial_prompt:
        prompt = initial_prompt
    else:
        prompt = input("You: ")
        
    while prompt.lower() != 'exit':
        # Call the appropriate API function
        if api_name == 'monica':
            _, conversation_id = test_monica_api(prompt, image_url, conversation_id)
        elif api_name == 'openai':
            _, conversation_id = test_openai_api(prompt, image_url, conversation_id)
        elif api_name == 'gemini':
            _, conversation_id = test_gemini_api(prompt, image_url, conversation_id)
        
        # Get next prompt
        prompt = input("\nYou: ")
    
    # End conversation and save
    conversation = conversation_manager.get_conversation(conversation_id)
    if conversation:
        conversation.end_conversation()
        conversation.calculate_metrics()
        print(f"\nConversation with {api_name.upper()} API ended.")
        print(f"Duration: {conversation.metrics['total_duration']:.2f} seconds")
        print(f"Number of turns: {conversation.metrics['num_turns']}")
        print(f"Average response time: {conversation.metrics['avg_assistant_response_time']:.2f} seconds")
        conversation.save_to_file()
    return conversation_id

def compare_apis(prompt, image_url=None, apis=None):
    """Compare responses from multiple APIs for the same prompt"""
    if apis is None:
        apis = ["monica", "openai", "gemini"]
    
    results = {}
    
    for api in apis:
        print(f"\n=== Testing {api.upper()} API ===")
        if api == "monica":
            result, conv_id = test_monica_api(prompt, image_url)
        elif api == "openai":
            result, conv_id = test_openai_api(prompt, image_url)
        elif api == "gemini":
            result, conv_id = test_gemini_api(prompt, image_url)
        
        # Skip if there was an error with the API
        if result is None:
            print(f"Skipping {api} due to error")
            continue
            
        results[api] = {
            'response': result.choices[0].message.content if hasattr(result, 'choices') else result.text,
            'conversation_id': conv_id
        }
    
    return results

def batch_test(test_cases, apis=None):
    """Run a batch of test cases across multiple APIs"""
    if apis is None:
        apis = ["monica", "openai", "gemini"]
    
    results = {}
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== Running test case {i+1}/{len(test_cases)} ===")
        prompt = test_case.get('prompt', 'Tell me about yourself')
        image_url = test_case.get('image_url')
        description = test_case.get('description', '')
        
        if description:
            print(f"Description: {description}")
        print(f"Prompt: {prompt}")
        
        test_results = compare_apis(prompt, image_url, apis)
        results[f"test_case_{i+1}"] = {
            'prompt': prompt,
            'description': description,
            'image_url': image_url,
            'results': test_results
        }
    
    # Save all conversations
    conversation_manager.save_all_conversations()
    
    # Save batch test results to a JSON file
    os.makedirs('results', exist_ok=True)
    results_file = f"results/batch_test_results_{int(time.time())}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nBatch test results saved to {results_file}")
    
    return results

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Test AI APIs with conversational capabilities")
    parser.add_argument("api", nargs="?", choices=["monica", "openai", "gemini", "all", "compare", "batch", "interactive"], 
                        default="interactive", help="API to test or mode to run (default: interactive)")
    parser.add_argument("-p", "--prompt", help="Text prompt to send")
    parser.add_argument("-i", "--image", help="URL of image to include in prompt")
    parser.add_argument("-t", "--text-only", action="store_true", help="Use text-only prompt (no image)")
    parser.add_argument("-f", "--file", help="JSON file with test cases for batch mode")
    parser.add_argument("-s", "--system", help="System message to set context for the conversation")
    
    args = parser.parse_args()
    
    # Set default prompt if not provided
    if not args.prompt:
        if args.text_only:
            args.prompt = "What are the benefits of artificial intelligence?"
        else:
            args.prompt = "Explain what you see in this image"
    
    # Set default image if not provided and not in text-only mode
    if not args.image and not args.text_only and args.api != "compare" and args.api != "batch":
        args.image = "https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Maps_blogheader.max-1000x1000.png"
    elif args.text_only or args.api == "compare" or args.api == "batch":
        args.image = None
    
    # Run in the specified mode
    if args.api == "interactive":
        print("Select API for interactive conversation:")
        print("1. Monica API")
        print("2. OpenAI API")
        print("3. Gemini API")
        choice = input("Enter choice (1-3): ")
        
        api_map = {"1": "monica", "2": "openai", "3": "gemini"}
        if choice in api_map:
            interactive_conversation(api_map[choice], args.prompt, args.image)
        else:
            print("Invalid choice. Exiting.")
    
    elif args.api == "compare":
        compare_apis(args.prompt, args.image)
        conversation_manager.save_all_conversations()
    
    elif args.api == "batch":
        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    test_cases = json.load(f)
                batch_test(test_cases)
            except Exception as e:
                print(f"Error loading test cases file: {str(e)}")
        else:
            # Default test cases if no file provided
            test_cases = [
                {"prompt": "What is artificial intelligence?"},
                {"prompt": "Explain quantum computing in simple terms"},
                {"prompt": "What are the ethical considerations of AI?"}
            ]
            batch_test(test_cases)
    
    elif args.api == "all":
        # Test all APIs with the same prompt
        compare_apis(args.prompt, args.image)
        conversation_manager.save_all_conversations()
    
    else:
        # Test a single API
        if args.api == "monica":
            test_monica_api(args.prompt, args.image)
        elif args.api == "openai":
            test_openai_api(args.prompt, args.image)
        elif args.api == "gemini":
            test_gemini_api(args.prompt, args.image)

if __name__ == "__main__":
    main()