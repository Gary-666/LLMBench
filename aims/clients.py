"""
API client implementations for different AI services.
"""
import os
import time
import traceback
import requests
import httpx
from io import BytesIO
import PIL.Image
from openai import OpenAI
import google.generativeai as genai

from .models import Message, conversation_manager


class BaseAPIClient:
    """Base class for all API clients."""
    def __init__(self, api_key, proxies=None):
        self.api_key = api_key
        self.proxies = proxies or {}
        
    def setup_proxies(self):
        """Set up proxy configuration if available."""
        if self.proxies:
            print(f"Using proxies: {self.proxies}")
            # Set environment variables for requests
            os.environ["HTTP_PROXY"] = self.proxies.get("http", "")
            os.environ["HTTPS_PROXY"] = self.proxies.get("https", "")
            
    def get_client(self):
        """Get the API client. To be implemented by subclasses."""
        raise NotImplementedError
        
    def send_message(self, prompt, image_url=None, conversation_id=None):
        """Send a message to the API. To be implemented by subclasses."""
        raise NotImplementedError


class MonicaClient(BaseAPIClient):
    """Client for the Monica AI API."""
    def __init__(self, api_key, proxies=None):
        super().__init__(api_key, proxies)
        self.base_url = "https://openapi.monica.im/v1"
        self.default_model = "gpt-4o"  # Monica的最新模型
        
    def get_client(self):
        """Get the Monica API client."""
        self.setup_proxies()
        http_client = None
        if self.proxies:
            proxy_url = self.proxies.get("https") or self.proxies.get("http")
            if proxy_url:
                http_client = httpx.Client(proxies={"http://": proxy_url, "https://": proxy_url})
        
        return OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            http_client=http_client,
            timeout=30.0
        )
        
    def send_message(self, prompt, image_url=None, conversation_id=None):
        """Send a message to the Monica API."""
        print("\n=== Testing Monica API ===")
        try:
            client = self.get_client()
            
            # Get or create conversation
            model = self.default_model
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
            print(f"Error details: {traceback.format_exc()}")
            # Return a tuple with None values to maintain the expected return format
            return None, None


class OpenAIClient(BaseAPIClient):
    """Client for the OpenAI API."""
    def __init__(self, api_key, proxies=None):
        super().__init__(api_key, proxies)
        self.text_model = "gpt-4.1"  # OpenAI最先进的文本模型
        self.vision_model = "gpt-4.1"  # OpenAI最先进的视觉模型
        
    def get_client(self):
        """Get the OpenAI API client."""
        self.setup_proxies()
        http_client = None
        if self.proxies:
            proxy_url = self.proxies.get("https") or self.proxies.get("http")
            if proxy_url:
                http_client = httpx.Client(proxies={"http://": proxy_url, "https://": proxy_url})
        
        return OpenAI(
            api_key=self.api_key,
            http_client=http_client,
            timeout=30.0
        )
        
    def send_message(self, prompt, image_url=None, conversation_id=None):
        """Send a message to the OpenAI API."""
        print("\n=== Testing OpenAI API ===")
        try:
            client = self.get_client()
            
            # Determine model based on image presence
            model = self.vision_model if image_url else self.text_model
                
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
            print(f"Error details: {traceback.format_exc()}")
            # Return a tuple with None values to maintain the expected return format
            return None, None


class GeminiClient(BaseAPIClient):
    """Client for the Google Gemini API."""
    def __init__(self, api_key, proxies=None):
        super().__init__(api_key, proxies)
        self.text_model = 'gemini-2.5-pro'  # Gemini最先进的文本模型
        self.vision_model = 'gemini-2.5-pro'  # Gemini最先进的视觉模型
        
    def setup(self):
        """Set up the Gemini API."""
        self.setup_proxies()
        genai.configure(api_key=self.api_key)
        
    def get_generation_config(self):
        """Get the generation configuration for Gemini."""
        return {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
    def get_safety_settings(self):
        """Get the safety settings for Gemini."""
        return [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
    def send_message(self, prompt, image_url=None, conversation_id=None):
        """Send a message to the Gemini API."""
        print("\n=== Testing Google Gemini API ===")
        try:
            # Configure the Gemini API
            self.setup()
            
            # Set generation config and safety settings
            generation_config = self.get_generation_config()
            safety_settings = self.get_safety_settings()
            
            # Determine model based on image presence
            model_name = self.vision_model if image_url else self.text_model
            
            # Get or create conversation
            if conversation_id:
                conversation = conversation_manager.get_conversation(conversation_id)
            else:
                conversation_id = conversation_manager.start_conversation('gemini', model_name)
                conversation = conversation_manager.get_conversation(conversation_id)
            
            # Add user message to conversation
            user_message = Message(role="user", content=prompt if not image_url else f"{prompt} [Image attached]")
            conversation.add_message(user_message)
            
            # Process image if provided
            if image_url:
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
                            proxies=self.proxies if self.proxies else None
                        )
                        response.raise_for_status()
                        img = PIL.Image.open(BytesIO(response.content))
                        
                        print("Generating content with image...")
                        # Create model with image support
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            generation_config=generation_config,
                            safety_settings=safety_settings
                        )
                        
                        # Generate content with the image
                        contents = [prompt, img]
                        break
                    except Exception as e:
                        print(f"Error downloading or processing image (attempt {attempt+1}/{max_retries}): {str(e)}")
                        if attempt < max_retries - 1:
                            print(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            print("Max retries reached. Falling back to text-only mode.")
                            # Fall back to text-only mode
                            model_name = self.text_model
                            model = genai.GenerativeModel(
                                model_name=model_name,
                                generation_config=generation_config,
                                safety_settings=safety_settings
                            )
                            contents = prompt
            else:
                # Text-only mode
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                contents = prompt
            
            # For Gemini, we need to build the conversation history
            if len(conversation.messages) > 1:
                # Create a chat session
                chat = model.start_chat(history=[
                    {"role": "user" if msg.role == "user" else "model", 
                     "parts": [msg.content]} 
                    for msg in conversation.messages[:-1]  # Exclude the last message which we'll send now
                ])
                response = chat.send_message(contents)
            else:
                # First message in conversation
                response = model.generate_content(contents)
            
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
