"""
Testing and evaluation utilities for AI API conversations.
"""
import os
import json
import time
from typing import List, Dict, Any, Optional

from .models import Message, conversation_manager
from .clients import MonicaClient, OpenAIClient, GeminiClient
from .evaluation import ConversationEvaluator, evaluate_api_responses


def interactive_conversation(api_name, initial_prompt=None, image_url=None, api_clients=None):
    """
    Start an interactive conversation with the specified API.
    
    Args:
        api_name: Name of the API to use ('monica', 'openai', or 'gemini')
        initial_prompt: Optional initial prompt to start the conversation
        image_url: Optional URL of an image to include in the conversation
        api_clients: Dictionary of API clients
        
    Returns:
        conversation_id: ID of the conversation
    """
    if api_clients is None:
        raise ValueError("API clients dictionary must be provided")
        
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
            _, conversation_id = api_clients['monica'].send_message(prompt, image_url, conversation_id)
        elif api_name == 'openai':
            _, conversation_id = api_clients['openai'].send_message(prompt, image_url, conversation_id)
        elif api_name == 'gemini':
            _, conversation_id = api_clients['gemini'].send_message(prompt, image_url, conversation_id)
        
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


def compare_apis(prompt, image_url=None, apis=None, api_clients=None):
    """
    Compare responses from multiple APIs for the same prompt.
    
    Args:
        prompt: Text prompt to send to the APIs
        image_url: Optional URL of an image to include in the prompt
        apis: List of API names to test
        api_clients: Dictionary of API clients
        
    Returns:
        results: Dictionary of results from each API
    """
    if api_clients is None:
        raise ValueError("API clients dictionary must be provided")
        
    if apis is None:
        apis = ["monica", "openai", "gemini"]
    
    results = {}
    
    for api in apis:
        print(f"\n=== Testing {api.upper()} API ===")
        if api == "monica":
            result, conv_id = api_clients['monica'].send_message(prompt, image_url)
        elif api == "openai":
            result, conv_id = api_clients['openai'].send_message(prompt, image_url)
        elif api == "gemini":
            result, conv_id = api_clients['gemini'].send_message(prompt, image_url)
        
        # Skip if there was an error with the API
        if result is None:
            print(f"Skipping {api} due to error")
            continue
            
        results[api] = {
            'response': result.choices[0].message.content if hasattr(result, 'choices') else result.text,
            'conversation_id': conv_id
        }
    
    return results


def batch_test(test_cases, apis=None, api_clients=None):
    """
    Run a batch of test cases across multiple APIs.
    
    Args:
        test_cases: List of test case dictionaries
        apis: List of API names to test
        api_clients: Dictionary of API clients
        
    Returns:
        results: Dictionary of results from each test case
    """
    if api_clients is None:
        raise ValueError("API clients dictionary must be provided")
        
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
        
        test_results = compare_apis(prompt, image_url, apis, api_clients)
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


def multi_turn_test(conversation_flows, apis=None, api_clients=None, evaluate=True):
    """
    Run multi-turn conversation tests across multiple APIs.
    
    Args:
        conversation_flows: List of conversation flow dictionaries
        apis: List of API names to test
        api_clients: Dictionary of API clients
        evaluate: Whether to evaluate the conversations
        
    Returns:
        results: Dictionary of results from each conversation flow
    """
    if api_clients is None:
        raise ValueError("API clients dictionary must be provided")
        
    if apis is None:
        apis = ["monica", "openai", "gemini"]
    
    results = {}
    
    for i, flow in enumerate(conversation_flows):
        print(f"\n=== Running conversation flow {i+1}/{len(conversation_flows)} ===")
        name = flow.get('name', f'Conversation Flow {i+1}')
        description = flow.get('description', '')
        turns = flow.get('turns', [])
        
        if description:
            print(f"Description: {description}")
        print(f"Name: {name}")
        print(f"Number of turns: {len(turns)}")
        
        # Run the conversation flow for each API
        api_results = {}
        for api in apis:
            print(f"\n--- Testing {api.upper()} API ---")
            conversation_id = None
            turn_results = []
            
            for j, turn in enumerate(turns):
                prompt = turn.get('prompt', '')
                image_url = turn.get('image_url')
                
                print(f"\nTurn {j+1}: {prompt}")
                
                if api == "monica":
                    result, conversation_id = api_clients['monica'].send_message(prompt, image_url, conversation_id)
                elif api == "openai":
                    result, conversation_id = api_clients['openai'].send_message(prompt, image_url, conversation_id)
                elif api == "gemini":
                    result, conversation_id = api_clients['gemini'].send_message(prompt, image_url, conversation_id)
                
                # Skip if there was an error with the API
                if result is None:
                    print(f"Error with {api} API on turn {j+1}")
                    break
                
                response = result.choices[0].message.content if hasattr(result, 'choices') else result.text
                turn_results.append({
                    'prompt': prompt,
                    'response': response
                })
            
            # Get conversation metrics
            conversation = conversation_manager.get_conversation(conversation_id)
            if conversation:
                conversation.end_conversation()
                conversation.calculate_metrics()
                metrics = conversation.metrics
            else:
                metrics = {}
                
            api_results[api] = {
                'conversation_id': conversation_id,
                'turns': turn_results,
                'metrics': metrics
            }
        
        results[f"flow_{i+1}"] = {
            'name': name,
            'description': description,
            'api_results': api_results
        }
    
    # Save all conversations
    conversation_manager.save_all_conversations()
    
    # Save multi-turn test results to a JSON file
    os.makedirs('results', exist_ok=True)
    results_file = f"results/multi_turn_test_results_{int(time.time())}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nMulti-turn test results saved to {results_file}")
    
    # 评估对话质量
    if evaluate:
        print("\n=== Evaluating conversation quality ===")
        evaluation_results = evaluate_api_responses(results_file)
        
        # 打印总体评分
        if "overall_scores" in evaluation_results:
            print("\n=== Overall API Scores ===")
            for api_name, score in evaluation_results["overall_scores"].items():
                print(f"{api_name.upper()}: {score:.2f}/1.00")
            
            # 找出得分最高的API
            best_api = max(evaluation_results["overall_scores"].items(), key=lambda x: x[1])
            print(f"\nBest performing API: {best_api[0].upper()} with score {best_api[1]:.2f}/1.00")
    
    return results
