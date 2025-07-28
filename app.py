from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import datetime
from typing import Dict, List, Optional
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'whatsapp_clone_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

class Message:
    def __init__(self, sender: str, content: str, timestamp: datetime.datetime = None, message_type: str = "text"):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.content = content
        self.timestamp = timestamp or datetime.datetime.now()
        self.message_type = message_type  # text, image, file
        self.read = False

    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'message_type': self.message_type,
            'read': self.read
        }

    @classmethod
    def from_dict(cls, data):
        msg = cls(
            sender=data['sender'],
            content=data['content'],
            timestamp=datetime.datetime.fromisoformat(data['timestamp']),
            message_type=data.get('message_type', 'text')
        )
        msg.id = data.get('id', str(uuid.uuid4()))
        msg.read = data.get('read', False)
        return msg

class Chat:
    def __init__(self, chat_id: str, name: str, chat_type: str = "personal"):
        self.chat_id = chat_id
        self.name = name
        self.chat_type = chat_type  # personal, group
        self.messages: List[Message] = []
        self.participants: List[str] = []
        self.last_seen = {}
        
    def add_message(self, message: Message):
        self.messages.append(message)
        
    def get_last_message(self) -> Optional[Message]:
        return self.messages[-1] if self.messages else None
    
    def to_dict(self):
        return {
            'chat_id': self.chat_id,
            'name': self.name,
            'chat_type': self.chat_type,
            'participants': self.participants,
            'messages': [msg.to_dict() for msg in self.messages],
            'last_message': self.get_last_message().to_dict() if self.get_last_message() else None
        }

class WhatsAppClone:
    def __init__(self):
        self.chats: Dict[str, Chat] = {}
        self.users = {}  # Store connected users
        self.data_file = "whatsapp_data.json"
        
        # Load existing data
        self.load_data()
        
        # Create sample chats if none exist
        if not self.chats:
            self.create_sample_chats()
            
    def create_sample_chats(self):
        # Create some sample chats
        contacts = [
            ("John Doe", "personal"),
            ("Alice Smith", "personal"), 
            ("Bob Wilson", "personal"),
            ("Family Group", "group"),
            ("Work Team", "group")
        ]
        
        for name, chat_type in contacts:
            chat_id = name.lower().replace(" ", "_")
            chat = Chat(chat_id, name, chat_type)
            
            # Add sample messages
            if name == "John Doe":
                chat.add_message(Message("John Doe", "Hey! How are you doing?"))
                chat.add_message(Message("You", "I'm good! How about you?"))
                chat.add_message(Message("John Doe", "Great! Want to catch up later?"))
            elif name == "Alice Smith":
                chat.add_message(Message("Alice Smith", "Did you see the latest news?"))
                chat.add_message(Message("You", "No, what happened?"))
            elif name == "Family Group":
                chat.add_message(Message("Mom", "Don't forget dinner on Sunday!"))
                chat.add_message(Message("Dad", "I'll bring dessert 🍰"))
                chat.add_message(Message("You", "Can't wait!"))
                
            self.chats[chat_id] = chat
            
    def save_data(self):
        """Save chat data to file"""
        data = {}
        for chat_id, chat in self.chats.items():
            data[chat_id] = {
                'name': chat.name,
                'chat_type': chat.chat_type,
                'participants': chat.participants,
                'messages': [msg.to_dict() for msg in chat.messages]
            }
            
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")
            
    def load_data(self):
        """Load chat data from file"""
        if not os.path.exists(self.data_file):
            return
            
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for chat_id, chat_data in data.items():
                chat = Chat(chat_id, chat_data['name'], chat_data['chat_type'])
                chat.participants = chat_data.get('participants', [])
                
                for msg_data in chat_data['messages']:
                    message = Message.from_dict(msg_data)
                    chat.add_message(message)
                    
                self.chats[chat_id] = chat
                
        except Exception as e:
            print(f"Error loading data: {e}")

# Initialize the WhatsApp clone
whatsapp = WhatsAppClone()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chats')
def get_chats():
    """Get all chats"""
    chats_data = []
    for chat in whatsapp.chats.values():
        chats_data.append(chat.to_dict())
    return jsonify(chats_data)

@app.route('/api/chats/<chat_id>/messages')
def get_messages(chat_id):
    """Get messages for a specific chat"""
    if chat_id in whatsapp.chats:
        chat = whatsapp.chats[chat_id]
        return jsonify([msg.to_dict() for msg in chat.messages])
    return jsonify([])

@app.route('/api/chats', methods=['POST'])
def create_chat():
    """Create a new chat"""
    data = request.json
    chat_name = data.get('name')
    chat_type = data.get('type', 'personal')
    
    if not chat_name:
        return jsonify({'error': 'Chat name is required'}), 400
        
    chat_id = chat_name.lower().replace(" ", "_")
    
    if chat_id in whatsapp.chats:
        return jsonify({'error': 'Chat already exists'}), 400
        
    chat = Chat(chat_id, chat_name, chat_type)
    whatsapp.chats[chat_id] = chat
    whatsapp.save_data()
    
    return jsonify(chat.to_dict())

@socketio.on('connect')
def handle_connect():
    print(f'User connected: {request.sid}')
    emit('connected', {'message': 'Connected to WhatsApp Clone'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'User disconnected: {request.sid}')

@socketio.on('join_chat')
def handle_join_chat(data):
    chat_id = data['chat_id']
    username = data.get('username', 'Anonymous')
    
    join_room(chat_id)
    whatsapp.users[request.sid] = {
        'username': username,
        'current_chat': chat_id
    }
    
    emit('joined_chat', {'chat_id': chat_id}, room=request.sid)
    emit('user_joined', {'username': username}, room=chat_id, include_self=False)

@socketio.on('leave_chat')
def handle_leave_chat(data):
    chat_id = data['chat_id']
    username = whatsapp.users.get(request.sid, {}).get('username', 'Anonymous')
    
    leave_room(chat_id)
    
    if request.sid in whatsapp.users:
        whatsapp.users[request.sid]['current_chat'] = None
    
    emit('left_chat', {'chat_id': chat_id}, room=request.sid)
    emit('user_left', {'username': username}, room=chat_id)

@socketio.on('send_message')
def handle_send_message(data):
    chat_id = data['chat_id']
    content = data['content']
    sender = data.get('sender', 'Anonymous')
    
    if chat_id not in whatsapp.chats:
        emit('error', {'message': 'Chat not found'})
        return
    
    # Create and store message
    message = Message(sender, content)
    whatsapp.chats[chat_id].add_message(message)
    whatsapp.save_data()
    
    # Emit message to all users in the chat
    emit('new_message', {
        'chat_id': chat_id,
        'message': message.to_dict()
    }, room=chat_id)
    
    # Simulate auto-response for demo (only for personal chats)
    if whatsapp.chats[chat_id].chat_type == 'personal' and sender != whatsapp.chats[chat_id].name:
        socketio.start_background_task(send_auto_response, chat_id)

def send_auto_response(chat_id):
    """Send an automated response after a delay"""
    import time
    import random
    
    time.sleep(2)  # Wait 2 seconds
    
    responses = [
        "That's interesting!",
        "I see what you mean.",
        "Thanks for letting me know!",
        "Sure thing!",
        "Sounds good to me.",
        "Let me think about it.",
        "Great idea!",
        "I agree with you."
    ]
    
    if chat_id in whatsapp.chats:
        chat = whatsapp.chats[chat_id]
        response_content = random.choice(responses)
        response_message = Message(chat.name, response_content)
        chat.add_message(response_message)
        whatsapp.save_data()
        
        socketio.emit('new_message', {
            'chat_id': chat_id,
            'message': response_message.to_dict()
        }, room=chat_id)

@socketio.on('typing')
def handle_typing(data):
    chat_id = data['chat_id']
    username = data.get('username', 'Anonymous')
    is_typing = data.get('is_typing', False)
    
    emit('user_typing', {
        'username': username,
        'is_typing': is_typing
    }, room=chat_id, include_self=False)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)