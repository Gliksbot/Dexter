"""
Dexter Simple v2 - Main UI
Simple tkinter interface for chatting with Dexter and Partner.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import asyncio
import threading
import time
from pathlib import Path
from llm_orchestrator import DexterOrchestrator

class DexterUI:
    """Simple tkinter interface for Dexter"""
    
    def __init__(self):
        self.orchestrator = None
        self.is_processing = False
        
        # Setup UI
        self.setup_ui()
        
        # Start orchestrator
        self.start_orchestrator()
    
    def setup_ui(self):
        """Setup the tkinter interface"""
        
        self.root = tk.Tk()
        self.root.title("Dexter Simple v2 - AI Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Title
        title_frame = tk.Frame(self.root, bg='#2b2b2b')
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="🤖 Dexter Simple v2",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='white'
        )
        title_label.pack()
        
        # Status
        self.status_label = tk.Label(
            title_frame,
            text="🔴 Starting up...",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#888888'
        )
        self.status_label.pack()
        
        # Chat display
        chat_frame = tk.Frame(self.root, bg='#2b2b2b')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(
            chat_frame,
            text="Conversation:",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor=tk.W)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            height=20,
            bg='#1e1e1e',
            fg='white',
            font=('Consolas', 10),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Input frame
        input_frame = tk.Frame(self.root, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Input field
        self.input_field = tk.Text(
            input_frame,
            height=3,
            bg='#1e1e1e',
            fg='white',
            font=('Arial', 11),
            wrap=tk.WORD
        )
        self.input_field.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))
        
        # Bind Enter key
        self.input_field.bind('<Control-Return>', self.send_message)
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send\n(Ctrl+Enter)",
            command=self.send_message,
            bg='#404040',
            fg='white',
            font=('Arial', 9),
            width=12
        )
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control frame
        control_frame = tk.Frame(self.root, bg='#2b2b2b')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Clear button
        clear_button = tk.Button(
            control_frame,
            text="Clear Chat",
            command=self.clear_chat,
            bg='#404040',
            fg='white',
            font=('Arial', 9)
        )
        clear_button.pack(side=tk.LEFT)
        
        # Proposals button
        self.proposals_button = tk.Button(
            control_frame,
            text="Show Proposals",
            command=self.show_proposals,
            bg='#404040',
            fg='white',
            font=('Arial', 9)
        )
        self.proposals_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Initialize chat
        self.add_to_chat("System", "Welcome to Dexter Simple v2! Starting up...", "#888888")
    
    def start_orchestrator(self):
        """Start the orchestrator in background thread"""
        
        def run_orchestrator():
            try:
                self.orchestrator = DexterOrchestrator()
                self.root.after(0, self.update_status_online)
                self.root.after(0, lambda: self.add_to_chat("System", "Dexter is now online! Try saying hello.", "#00ff00"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.add_to_chat("System", f"Error starting: {error_msg}", "#ff0000"))
        
        threading.Thread(target=run_orchestrator, daemon=True).start()
    
    def update_status_online(self):
        """Update status to online"""
        self.status_label.config(text="🟢 Dexter & Partner Online", fg="#00ff00")
    
    def add_to_chat(self, speaker: str, message: str, color: str = "white"):
        """Add message to chat display"""
        
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        # Add message
        self.chat_display.insert(tk.END, f"[{timestamp}] {speaker}: {message}\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self, event=None):
        """Send message to Dexter"""
        
        if self.is_processing:
            return
        
        message = self.input_field.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Clear input
        self.input_field.delete("1.0", tk.END)
        
        # Add to chat
        self.add_to_chat("You", message, "#00aaff")
        
        # Process message
        self.process_message_async(message)
    
    def process_message_async(self, message: str):
        """Process message asynchronously"""
        
        def run_async():
            if not self.orchestrator:
                self.root.after(0, lambda: self.add_to_chat("System", "Dexter not ready yet", "#ff0000"))
                return
            
            self.is_processing = True
            self.root.after(0, lambda: self.send_button.config(text="Thinking...", state=tk.DISABLED))
            
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Process message
                response = loop.run_until_complete(self.orchestrator.process_user_input(message))
                
                # Update UI
                self.root.after(0, lambda: self.add_to_chat("Dexter", response, "#88ff88"))
                
            except Exception as e:
                # Fix the closure issue by capturing e properly
                error_msg = str(e)
                self.root.after(0, lambda: self.add_to_chat("System", f"Error: {error_msg}", "#ff0000"))
            
            finally:
                self.is_processing = False
                self.root.after(0, lambda: self.send_button.config(text="Send\n(Ctrl+Enter)", state=tk.NORMAL))
        
        threading.Thread(target=run_async, daemon=True).start()
    
    def clear_chat(self):
        """Clear chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.add_to_chat("System", "Chat cleared", "#888888")
    
    def show_proposals(self):
        """Show Partner proposals"""
        if not self.orchestrator:
            self.add_to_chat("System", "Orchestrator not ready", "#ff0000")
            return
        
        try:
            proposals = self.orchestrator.get_recent_proposals()
            if proposals:
                proposals_text = "\n".join([f"• {p}" for p in proposals])
                self.add_to_chat("Partner Proposals", f"Recent suggestions:\n{proposals_text}", "#ffaa00")
            else:
                self.add_to_chat("Partner Proposals", "No recent suggestions.", "#ffaa00")
        except Exception as e:
            error_msg = str(e)
            self.add_to_chat("System", f"Error getting proposals: {error_msg}", "#ff0000")
    
    def run(self):
        """Start the UI"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

def main():
    """Main entry point"""
    if not Path("dexter_simple_config.json").exists():
        print("Configuration file not found! Please run start_dexter.py first.")
        return
    
    app = DexterUI()
    app.run()

if __name__ == "__main__":
    main()
