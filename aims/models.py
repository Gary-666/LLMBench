"""
Data models for the AIMS conversation framework.
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Union
import time
import os
import json
import datetime
import csv
import uuid


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # 'system', 'user', or 'assistant'
    content: Union[str, List[Dict[str, Any]]]  # Text or structured content with images
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class Conversation:
    """Represents a full conversation with an API."""
    id: str
    api_name: str
    messages: List[Message]
    model: str
    start_time: float
    end_time: Optional[float] = None
    metrics: Dict[str, Any] = None
    
    def add_message(self, message: Message):
        """Add a message to the conversation."""
        self.messages.append(message)
        
    def end_conversation(self):
        """Mark the conversation as ended."""
        self.end_time = time.time()
        
    def calculate_metrics(self):
        """Calculate conversation metrics."""
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
        """Calculate the average time between user messages and assistant responses."""
        response_times = []
        for i in range(1, len(self.messages)):
            if self.messages[i].role == 'assistant' and self.messages[i-1].role == 'user':
                response_times.append(self.messages[i].timestamp - self.messages[i-1].timestamp)
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _calculate_avg_response_length(self):
        """Calculate the average length of assistant responses."""
        responses = [m.content for m in self.messages if m.role == 'assistant']
        if not responses:
            return 0
        lengths = [len(r) if isinstance(r, str) else sum(len(item.get('text', '')) for item in r if isinstance(item, dict) and 'text' in item) 
                  for r in responses]
        return sum(lengths) / len(lengths)
    
    def to_dict(self):
        """Convert the conversation to a dictionary."""
        return asdict(self)
    
    def save_to_file(self, directory='conversations'):
        """Save the conversation to a JSON file."""
        os.makedirs(directory, exist_ok=True)
        filename = f"{directory}/{self.api_name}_{self.id}_{int(self.start_time)}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, default=str, ensure_ascii=False)
        print(f"Conversation saved to {filename}")
        return filename


class ConversationManager:
    """Manages multiple conversations across different APIs."""
    def __init__(self):
        self.conversations = {}
        self.current_conversation_ids = {'monica': None, 'openai': None, 'gemini': None}
        
    def start_conversation(self, api_name, model):
        """Start a new conversation with the specified API."""
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
        """Add a message to an existing conversation."""
        if conv_id in self.conversations:
            self.conversations[conv_id].add_message(message)
            return True
        return False
    
    def get_conversation(self, conv_id):
        """Get a conversation by its ID."""
        return self.conversations.get(conv_id)
    
    def get_current_conversation(self, api_name):
        """Get the current conversation for a specific API."""
        conv_id = self.current_conversation_ids.get(api_name)
        if conv_id:
            return self.conversations.get(conv_id)
        return None
    
    def end_conversation(self, conv_id):
        """End a conversation."""
        if conv_id in self.conversations:
            self.conversations[conv_id].end_conversation()
            return True
        return False
    
    def save_all_conversations(self, directory='conversations'):
        """Save all conversations to files and generate a summary CSV."""
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
        """Create a CSV summary of all conversations."""
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


# Create a global instance of the ConversationManager
conversation_manager = ConversationManager()
