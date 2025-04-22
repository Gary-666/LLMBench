"""
Command-line interface for the AIMS conversation framework.
"""
import os
import argparse
import json
from typing import Dict, List, Any

from .models import conversation_manager
from .clients import MonicaClient, OpenAIClient, GeminiClient
from .testing import interactive_conversation, compare_apis, batch_test, multi_turn_test


def setup_api_clients(proxies=None):
    """
    Set up API clients for all supported APIs.
    
    Args:
        proxies: Optional proxy configuration
        
    Returns:
        Dictionary of API clients
    """
    # Get API keys from environment variables
    monica_key = os.getenv("MONICA_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_KEY")
    
    # Create API clients
    clients = {}
    if monica_key:
        clients['monica'] = MonicaClient(monica_key, proxies)
    else:
        print("Warning: Monica API key not found in environment variables")
        
    if openai_key:
        clients['openai'] = OpenAIClient(openai_key, proxies)
    else:
        print("Warning: OpenAI API key not found in environment variables")
        
    if gemini_key:
        clients['gemini'] = GeminiClient(gemini_key, proxies)
    else:
        print("Warning: Gemini API key not found in environment variables")
        
    return clients


def check_api_keys():
    """Check if API keys are available and print status."""
    monica_key = os.getenv("MONICA_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_KEY")
    
    print("\n=== API Key Status ===")
    print(f"Monica API: {'Available' if monica_key else 'Not available'}")
    print(f"OpenAI API: {'Available' if openai_key else 'Not available'}")
    print(f"Gemini API: {'Available' if gemini_key else 'Not available'}")
    
    print()  # Empty line for better readability


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Test AI APIs with conversational capabilities")
    parser.add_argument("mode", nargs="?", 
                        choices=["interactive", "compare", "batch", "multi-turn", "monica", "openai", "gemini", "all"], 
                        default="interactive", 
                        help="Mode to run (default: interactive)")
    parser.add_argument("-p", "--prompt", help="Text prompt to send")
    parser.add_argument("-i", "--image", help="URL of image to include in prompt")
    parser.add_argument("-t", "--text-only", action="store_true", help="Use text-only prompt (no image)")
    parser.add_argument("-f", "--file", help="JSON file with test cases for batch mode or conversation flows for multi-turn mode")
    parser.add_argument("-s", "--system", help="System message to set context for the conversation")
    parser.add_argument("--http-proxy", help="HTTP proxy to use")
    parser.add_argument("--https-proxy", help="HTTPS proxy to use")
    
    return parser.parse_args()


def main():
    """Main entry point for the command-line interface."""
    args = parse_args()
    
    # Set up proxies from environment variables or command line arguments
    proxies = {}
    # 优先使用命令行参数中的代理设置
    if args.http_proxy:
        proxies["http"] = args.http_proxy
    elif os.getenv("HTTP_PROXY"):
        proxies["http"] = os.getenv("HTTP_PROXY")
        
    if args.https_proxy:
        proxies["https"] = args.https_proxy
    elif os.getenv("HTTPS_PROXY"):
        proxies["https"] = os.getenv("HTTPS_PROXY")
        
    if proxies:
        print(f"Using proxies: {proxies}")
    
    # Set up API clients
    api_clients = setup_api_clients(proxies)
    
    # Check API keys
    check_api_keys()
    
    # Set default prompt if not provided
    if not args.prompt:
        if args.text_only:
            args.prompt = "What are the benefits of artificial intelligence?"
        else:
            args.prompt = "Explain what you see in this image"
    
    # Set default image if not provided and not in text-only mode
    if not args.image and not args.text_only and args.mode not in ["compare", "batch", "multi-turn"]:
        args.image = "https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Maps_blogheader.max-1000x1000.png"
    elif args.text_only or args.mode in ["compare", "batch", "multi-turn"]:
        args.image = None
    
    # Run in the specified mode
    if args.mode == "interactive":
        print("Select API for interactive conversation:")
        print("1. Monica API")
        print("2. OpenAI API")
        print("3. Gemini API")
        choice = input("Enter choice (1-3): ")
        
        api_map = {"1": "monica", "2": "openai", "3": "gemini"}
        if choice in api_map:
            api_name = api_map[choice]
            if api_name in api_clients:
                interactive_conversation(api_name, args.prompt, args.image, api_clients)
            else:
                print(f"Error: {api_name.upper()} API client not available. Check your API key.")
        else:
            print("Invalid choice. Exiting.")
    
    elif args.mode == "compare":
        compare_apis(args.prompt, args.image, api_clients=api_clients)
        conversation_manager.save_all_conversations()
    
    elif args.mode == "batch":
        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    test_cases = json.load(f)
                batch_test(test_cases, api_clients=api_clients)
            except Exception as e:
                print(f"Error loading test cases file: {str(e)}")
        else:
            # Default test cases if no file provided
            test_cases = [
                {"prompt": "What is artificial intelligence?"},
                {"prompt": "Explain quantum computing in simple terms"},
                {"prompt": "What are the ethical considerations of AI?"}
            ]
            batch_test(test_cases, api_clients=api_clients)
    
    elif args.mode == "multi-turn":
        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    conversation_flows = json.load(f)
                multi_turn_test(conversation_flows, api_clients=api_clients)
            except Exception as e:
                print(f"Error loading conversation flows file: {str(e)}")
        else:
            # Default conversation flow if no file provided
            conversation_flows = [
                {
                    "name": "General Knowledge Test",
                    "description": "Testing general knowledge capabilities",
                    "turns": [
                        {"prompt": "What is artificial intelligence?"},
                        {"prompt": "What are the main types of machine learning?"},
                        {"prompt": "Can you explain how neural networks work?"}
                    ]
                },
                {
                    "name": "Contextual Understanding Test",
                    "description": "Testing contextual understanding and memory",
                    "turns": [
                        {"prompt": "My name is Alex and I'm learning about AI."},
                        {"prompt": "What was my name again?"},
                        {"prompt": "What am I learning about?"}
                    ]
                }
            ]
            multi_turn_test(conversation_flows, api_clients=api_clients)
    
    elif args.mode == "all":
        # Test all APIs with the same prompt
        compare_apis(args.prompt, args.image, api_clients=api_clients)
        conversation_manager.save_all_conversations()
    
    else:
        # Test a single API
        api_name = args.mode
        if api_name in api_clients:
            result, conv_id = api_clients[api_name].send_message(args.prompt, args.image)
            if conv_id:
                conversation = conversation_manager.get_conversation(conv_id)
                conversation.end_conversation()
                conversation.save_to_file()
        else:
            print(f"Error: {api_name.upper()} API client not available. Check your API key.")
