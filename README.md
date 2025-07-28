# WhatsApp Clone in Python

A feature-rich WhatsApp-like messaging application built with Python and tkinter, featuring a modern UI and comprehensive messaging capabilities.

## Features

### 🎨 Modern UI Design
- Clean, WhatsApp-inspired interface
- Dark sidebar with light chat area
- Responsive design with hover effects
- Custom styling and color scheme

### 💬 Messaging Features
- Real-time messaging simulation
- Personal and group chats
- Message timestamps
- Read receipts (✓✓)
- Emoji picker with popular emojis
- File attachment support
- Search functionality for chats

### 🔧 Core Functionality
- Create new chats (personal/group)
- Auto-save chat history
- Persistent data storage in JSON format
- Auto-response simulation for demo
- Typing indicators (placeholder)
- Online status display

### 📱 User Experience
- Intuitive chat selection
- Smooth scrolling message area
- Keyboard shortcuts (Enter to send)
- Modern message bubbles
- Last message preview in chat list

## Installation

1. Clone or download the project files
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python whatsapp_clone.py
```

### Getting Started
1. The app starts with sample chats pre-loaded
2. Click on any chat in the left sidebar to start messaging
3. Type your message and press Enter or click Send
4. Use the emoji button (😊) to add emojis
5. Use the attachment button (📎) to attach files
6. Create new chats using the "+ New Chat" button

### Features in Detail

**Chat Management:**
- Click "+ New Chat" to create new personal or group chats
- Search for chats using the search bar
- Chat list shows last message preview

**Messaging:**
- Type messages in the input field at the bottom
- Press Enter or click Send to send messages
- Messages are automatically saved
- Timestamps are displayed with each message

**Emojis:**
- Click the emoji button (😊) to open emoji picker
- Click any emoji to insert it into your message

**File Attachments:**
- Click the attachment button (📎) to select files
- Supported file types: images, documents, and all file types

## Technical Details

### Architecture
- **Object-Oriented Design**: Clean separation of concerns with `Message`, `Chat`, and `WhatsAppClone` classes
- **Data Persistence**: JSON-based storage for chat history
- **Modern GUI**: Built with tkinter and custom styling
- **Responsive Design**: Adaptive layout that works on different screen sizes

### File Structure
- `whatsapp_clone.py` - Main application file
- `requirements.txt` - Python dependencies
- `whatsapp_data.json` - Auto-generated data storage file
- `README.md` - This documentation

### Dependencies
- `tkinter` - GUI framework (built into Python)
- `Pillow` - Image processing capabilities
- `emoji` - Emoji support
- `requests` - HTTP requests (for future features)
- `python-dateutil` - Date/time handling
- `cryptography` - Security features (for future encryption)

## Sample Features Demonstration

The application comes with pre-loaded sample chats to demonstrate its capabilities:

1. **Personal Chats**: Individual conversations with contacts
2. **Group Chats**: Multi-participant conversations
3. **Message History**: Persistent storage of all conversations
4. **Auto-responses**: Simulated responses for demonstration

## Future Enhancements

Potential features that could be added:
- Real network messaging with socket programming
- End-to-end encryption
- Voice message support
- Image preview and sharing
- Video calling integration
- Dark/light theme toggle
- Message search within chats
- Chat backup and restore
- Status updates
- Profile management

## Development

### Code Structure
- **Message Class**: Handles individual message data
- **Chat Class**: Manages conversation data and participants
- **WhatsAppClone Class**: Main application controller and UI manager

### Key Methods
- `create_widgets()`: Sets up the UI layout
- `send_message()`: Handles message sending logic
- `load_messages()`: Displays chat history
- `save_data()`/`load_data()`: Data persistence
- `simulate_response()`: Demo auto-responses

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to fork this project and submit pull requests for improvements or bug fixes.

---

Built with ❤️ using Python and tkinter
