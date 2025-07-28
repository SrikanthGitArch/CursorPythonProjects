import tkinter as tk
from tkinter import ttk, messagebox, filedialog, PhotoImage
import json
import os
import datetime
from typing import Dict, List, Optional
import emoji
from PIL import Image, ImageTk
import threading
import time

class Message:
    def __init__(self, sender: str, content: str, timestamp: datetime.datetime = None, message_type: str = "text"):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp or datetime.datetime.now()
        self.message_type = message_type  # text, image, file
        self.read = False

    def to_dict(self):
        return {
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

class WhatsAppClone:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WhatsApp Clone")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.current_user = "You"
        self.chats: Dict[str, Chat] = {}
        self.current_chat_id = None
        self.data_file = "whatsapp_data.json"
        
        # Load existing data
        self.load_data()
        
        # Create sample chats if none exist
        if not self.chats:
            self.create_sample_chats()
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.load_chat_list()
        
        # Auto-save data periodically
        self.auto_save()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Sidebar.TFrame', background='#2a2f32')
        style.configure('Chat.TFrame', background='#ffffff')
        style.configure('Header.TFrame', background='#00a884')
        style.configure('MessageInput.TFrame', background='#f0f0f0')
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left sidebar (chat list)
        self.create_sidebar(main_frame)
        
        # Right side (chat area)
        self.create_chat_area(main_frame)
        
    def create_sidebar(self, parent):
        sidebar_frame = ttk.Frame(parent, style='Sidebar.TFrame', width=350)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        sidebar_frame.pack_propagate(False)
        
        # Header
        header_frame = tk.Frame(sidebar_frame, bg='#00a884', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="WhatsApp Clone", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#00a884')
        title_label.pack(pady=15)
        
        # Search bar
        search_frame = tk.Frame(sidebar_frame, bg='#2a2f32')
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=('Arial', 11), bg='#3c4043', fg='white',
                               insertbackground='white', relief=tk.FLAT)
        search_entry.pack(fill=tk.X, ipady=8, ipadx=10)
        search_entry.bind('<KeyRelease>', self.filter_chats)
        
        # New chat button
        new_chat_btn = tk.Button(sidebar_frame, text="+ New Chat", 
                                font=('Arial', 11), bg='#00a884', fg='white',
                                relief=tk.FLAT, command=self.new_chat_dialog)
        new_chat_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Chat list
        self.chat_list_frame = tk.Frame(sidebar_frame, bg='#2a2f32')
        self.chat_list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
    def create_chat_area(self, parent):
        chat_container = ttk.Frame(parent)
        chat_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chat header
        self.chat_header = tk.Frame(chat_container, bg='#00a884', height=60)
        self.chat_header.pack(fill=tk.X)
        self.chat_header.pack_propagate(False)
        
        self.chat_title_label = tk.Label(self.chat_header, text="Select a chat", 
                                        font=('Arial', 14, 'bold'), fg='white', bg='#00a884')
        self.chat_title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Online status
        self.status_label = tk.Label(self.chat_header, text="", 
                                    font=('Arial', 10), fg='#e8f5e8', bg='#00a884')
        self.status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Messages area
        messages_frame = tk.Frame(chat_container, bg='#e5ddd5')
        messages_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable text widget for messages
        self.messages_text = tk.Text(messages_frame, wrap=tk.WORD, state=tk.DISABLED,
                                    bg='#e5ddd5', fg='#000', font=('Arial', 11),
                                    relief=tk.FLAT, padx=15, pady=10)
        
        scrollbar = ttk.Scrollbar(messages_frame, orient=tk.VERTICAL, command=self.messages_text.yview)
        self.messages_text.configure(yscrollcommand=scrollbar.set)
        
        self.messages_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Message input area
        input_frame = tk.Frame(chat_container, bg='#f0f0f0', height=70)
        input_frame.pack(fill=tk.X)
        input_frame.pack_propagate(False)
        
        # Emoji button
        emoji_btn = tk.Button(input_frame, text="😊", font=('Arial', 16),
                             bg='#f0f0f0', relief=tk.FLAT, command=self.show_emoji_picker)
        emoji_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        # Attachment button
        attach_btn = tk.Button(input_frame, text="📎", font=('Arial', 16),
                              bg='#f0f0f0', relief=tk.FLAT, command=self.attach_file)
        attach_btn.pack(side=tk.LEFT, padx=5, pady=15)
        
        # Message entry
        self.message_var = tk.StringVar()
        self.message_entry = tk.Entry(input_frame, textvariable=self.message_var,
                                     font=('Arial', 12), relief=tk.FLAT)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=15, ipady=8)
        self.message_entry.bind('<Return>', self.send_message)
        self.message_entry.bind('<KeyPress>', self.on_typing)
        
        # Send button
        self.send_btn = tk.Button(input_frame, text="Send", font=('Arial', 11, 'bold'),
                                 bg='#00a884', fg='white', relief=tk.FLAT, 
                                 command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, padx=10, pady=15)
        
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
                chat.add_message(Message(self.current_user, "I'm good! How about you?"))
                chat.add_message(Message("John Doe", "Great! Want to catch up later?"))
            elif name == "Alice Smith":
                chat.add_message(Message("Alice Smith", "Did you see the latest news?"))
                chat.add_message(Message(self.current_user, "No, what happened?"))
            elif name == "Family Group":
                chat.add_message(Message("Mom", "Don't forget dinner on Sunday!"))
                chat.add_message(Message("Dad", "I'll bring dessert 🍰"))
                chat.add_message(Message(self.current_user, "Can't wait!"))
                
            self.chats[chat_id] = chat
            
    def load_chat_list(self):
        # Clear existing chat list
        for widget in self.chat_list_frame.winfo_children():
            widget.destroy()
            
        # Add chats to list
        for chat_id, chat in self.chats.items():
            self.create_chat_item(chat)
            
    def create_chat_item(self, chat: Chat):
        item_frame = tk.Frame(self.chat_list_frame, bg='#2a2f32', cursor='hand2')
        item_frame.pack(fill=tk.X, pady=2)
        item_frame.bind('<Button-1>', lambda e, cid=chat.chat_id: self.select_chat(cid))
        
        # Chat info frame
        info_frame = tk.Frame(item_frame, bg='#2a2f32')
        info_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Chat name
        name_label = tk.Label(info_frame, text=chat.name, font=('Arial', 12, 'bold'),
                             fg='white', bg='#2a2f32', anchor='w')
        name_label.pack(fill=tk.X)
        name_label.bind('<Button-1>', lambda e, cid=chat.chat_id: self.select_chat(cid))
        
        # Last message preview
        last_msg = chat.get_last_message()
        if last_msg:
            preview_text = last_msg.content[:50] + "..." if len(last_msg.content) > 50 else last_msg.content
            preview_label = tk.Label(info_frame, text=preview_text, font=('Arial', 10),
                                   fg='#8696a0', bg='#2a2f32', anchor='w')
            preview_label.pack(fill=tk.X)
            preview_label.bind('<Button-1>', lambda e, cid=chat.chat_id: self.select_chat(cid))
        
        # Hover effects
        def on_enter(e):
            item_frame.configure(bg='#3c4043')
            info_frame.configure(bg='#3c4043')
            name_label.configure(bg='#3c4043')
            if last_msg:
                preview_label.configure(bg='#3c4043')
                
        def on_leave(e):
            item_frame.configure(bg='#2a2f32')
            info_frame.configure(bg='#2a2f32')
            name_label.configure(bg='#2a2f32')
            if last_msg:
                preview_label.configure(bg='#2a2f32')
                
        item_frame.bind('<Enter>', on_enter)
        item_frame.bind('<Leave>', on_leave)
        info_frame.bind('<Enter>', on_enter)
        info_frame.bind('<Leave>', on_leave)
        
    def select_chat(self, chat_id: str):
        self.current_chat_id = chat_id
        chat = self.chats[chat_id]
        
        # Update header
        self.chat_title_label.config(text=chat.name)
        status_text = "online" if chat.chat_type == "personal" else f"{len(chat.participants)} participants"
        self.status_label.config(text=status_text)
        
        # Load messages
        self.load_messages()
        
    def load_messages(self):
        if not self.current_chat_id:
            return
            
        chat = self.chats[self.current_chat_id]
        
        # Clear messages
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete(1.0, tk.END)
        
        # Add messages
        for message in chat.messages:
            self.display_message(message)
            
        self.messages_text.config(state=tk.DISABLED)
        self.messages_text.see(tk.END)
        
    def display_message(self, message: Message):
        timestamp = message.timestamp.strftime("%H:%M")
        is_own_message = message.sender == self.current_user
        
        # Create message bubble
        self.messages_text.config(state=tk.NORMAL)
        
        if is_own_message:
            # Right-aligned message (own message)
            self.messages_text.insert(tk.END, f"\n{message.content}\n")
            self.messages_text.insert(tk.END, f"{timestamp} ✓✓\n", "timestamp_right")
        else:
            # Left-aligned message (other person's message)
            self.messages_text.insert(tk.END, f"\n{message.sender}\n", "sender_name")
            self.messages_text.insert(tk.END, f"{message.content}\n")
            self.messages_text.insert(tk.END, f"{timestamp}\n", "timestamp_left")
            
        # Configure text tags for styling
        self.messages_text.tag_configure("sender_name", foreground="#00a884", font=('Arial', 10, 'bold'))
        self.messages_text.tag_configure("timestamp_right", foreground="#8696a0", font=('Arial', 9), justify='right')
        self.messages_text.tag_configure("timestamp_left", foreground="#8696a0", font=('Arial', 9))
        
        self.messages_text.config(state=tk.DISABLED)
        
    def send_message(self, event=None):
        if not self.current_chat_id:
            messagebox.showwarning("No Chat Selected", "Please select a chat first.")
            return
            
        content = self.message_var.get().strip()
        if not content:
            return
            
        # Create and add message
        message = Message(self.current_user, content)
        chat = self.chats[self.current_chat_id]
        chat.add_message(message)
        
        # Display message
        self.display_message(message)
        
        # Clear input
        self.message_var.set("")
        
        # Simulate response (for demo purposes)
        self.simulate_response()
        
        # Refresh chat list to update last message
        self.load_chat_list()
        
        # Auto scroll to bottom
        self.messages_text.see(tk.END)
        
    def simulate_response(self):
        """Simulate a response from the other person (for demo purposes)"""
        if not self.current_chat_id:
            return
            
        chat = self.chats[self.current_chat_id]
        if chat.chat_type == "personal":
            # Simulate typing delay
            self.root.after(2000, self._send_auto_response)
            
    def _send_auto_response(self):
        chat = self.chats[self.current_chat_id]
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
        
        import random
        response = random.choice(responses)
        message = Message(chat.name, response)
        chat.add_message(message)
        
        if self.current_chat_id == chat.chat_id:
            self.display_message(message)
            self.messages_text.see(tk.END)
            
        # Refresh chat list
        self.load_chat_list()
        
    def new_chat_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("New Chat")
        dialog.geometry("400x300")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        tk.Label(dialog, text="Create New Chat", font=('Arial', 16, 'bold'),
                bg='#f0f0f0').pack(pady=20)
        
        # Chat name
        tk.Label(dialog, text="Chat Name:", font=('Arial', 12), bg='#f0f0f0').pack(pady=5)
        name_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=name_var, font=('Arial', 12), width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        # Chat type
        tk.Label(dialog, text="Chat Type:", font=('Arial', 12), bg='#f0f0f0').pack(pady=5)
        type_var = tk.StringVar(value="personal")
        type_frame = tk.Frame(dialog, bg='#f0f0f0')
        type_frame.pack(pady=5)
        
        tk.Radiobutton(type_frame, text="Personal", variable=type_var, value="personal",
                      font=('Arial', 11), bg='#f0f0f0').pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="Group", variable=type_var, value="group",
                      font=('Arial', 11), bg='#f0f0f0').pack(side=tk.LEFT, padx=10)
        
        def create_chat():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a chat name.")
                return
                
            chat_id = name.lower().replace(" ", "_")
            if chat_id in self.chats:
                messagebox.showerror("Error", "A chat with this name already exists.")
                return
                
            # Create new chat
            chat = Chat(chat_id, name, type_var.get())
            self.chats[chat_id] = chat
            
            # Refresh chat list
            self.load_chat_list()
            
            # Select the new chat
            self.select_chat(chat_id)
            
            dialog.destroy()
            
        # Buttons
        btn_frame = tk.Frame(dialog, bg='#f0f0f0')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Create", font=('Arial', 11, 'bold'),
                 bg='#00a884', fg='white', command=create_chat).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", font=('Arial', 11),
                 bg='#f44336', fg='white', command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        
        # Bind Enter key to create chat
        dialog.bind('<Return>', lambda e: create_chat())
        
    def show_emoji_picker(self):
        """Show a simple emoji picker"""
        emojis = ['😀', '😂', '😍', '😊', '😎', '😔', '😭', '😡', '👍', '👎', '❤️', '🔥', '💯', '🎉', '👏', '🙏']
        
        picker = tk.Toplevel(self.root)
        picker.title("Emoji Picker")
        picker.geometry("300x200")
        picker.configure(bg='white')
        picker.transient(self.root)
        picker.grab_set()
        
        # Center the picker
        picker.update_idletasks()
        x = self.root.winfo_x() + 100
        y = self.root.winfo_y() + 100
        picker.geometry(f"300x200+{x}+{y}")
        
        emoji_frame = tk.Frame(picker, bg='white')
        emoji_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for i, emoji_char in enumerate(emojis):
            row = i // 8
            col = i % 8
            
            btn = tk.Button(emoji_frame, text=emoji_char, font=('Arial', 16),
                           width=3, height=2, relief=tk.FLAT,
                           command=lambda e=emoji_char: self.insert_emoji(e, picker))
            btn.grid(row=row, column=col, padx=2, pady=2)
            
    def insert_emoji(self, emoji_char, picker_window):
        """Insert emoji into message entry"""
        current_text = self.message_var.get()
        cursor_pos = self.message_entry.index(tk.INSERT)
        new_text = current_text[:cursor_pos] + emoji_char + current_text[cursor_pos:]
        self.message_var.set(new_text)
        picker_window.destroy()
        self.message_entry.focus()
        
    def attach_file(self):
        """Handle file attachment"""
        file_path = filedialog.askopenfilename(
            title="Select file to attach",
            filetypes=[
                ("All files", "*.*"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Documents", "*.pdf *.doc *.docx *.txt"),
            ]
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            # For demo purposes, just send the filename
            self.message_var.set(f"📎 {filename}")
            
    def filter_chats(self, event=None):
        """Filter chats based on search input"""
        search_term = self.search_var.get().lower()
        
        # Clear current list
        for widget in self.chat_list_frame.winfo_children():
            widget.destroy()
            
        # Add filtered chats
        for chat_id, chat in self.chats.items():
            if search_term in chat.name.lower():
                self.create_chat_item(chat)
                
    def on_typing(self, event=None):
        """Handle typing indicator (placeholder for future implementation)"""
        pass
        
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
            
    def auto_save(self):
        """Auto-save data every 30 seconds"""
        self.save_data()
        self.root.after(30000, self.auto_save)  # 30 seconds
        
    def on_closing(self):
        """Handle app closing"""
        self.save_data()
        self.root.destroy()
        
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = WhatsAppClone()
    app.run()