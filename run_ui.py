import customtkinter as ctk
import threading
import logging
import time
import schedule
from datetime import datetime
import pytz
from src.screenshot import grab_tradingview_window
from src.vision_client import analyze_chart
from src.mailer import email_signal
from src.config import TIMEZONE

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("trading_bot.log")
    ]
)
logger = logging.getLogger(__name__)

# Set appearance theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Custom colors
COLORS = {
    "background": "#0A0F19",  # Dark navy blue
    "secondary_bg": "#121B2E",  # Slightly lighter navy
    "accent": "#2563EB",  # Electric blue
    "accent_hover": "#1D4ED8",  # Darker blue
    "success": "#10B981",  # Green
    "success_hover": "#059669",  # Darker green
    "error": "#EF4444",  # Red
    "error_hover": "#DC2626",  # Darker red
    "text": "#F9FAFB",  # Almost white
    "text_secondary": "#9CA3AF",  # Gray
    "border": "#1F2937",  # Dark gray
}


class TradingBotUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("TradingView Mail-Bot")
        self.geometry("900x700")
        
        # Set window icon (optional)
        # self.iconbitmap("icon.ico")
        
        # Configure custom colors
        self.configure(fg_color=COLORS["background"])
        
        # Initialize variables
        self.running = False
        self.provider = "GPT"
        self.thread = None
        
        # Create main container with custom styling
        self.main_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["secondary_bg"],
            corner_radius=20,
            border_width=2,
            border_color=COLORS["border"]
        )
        self.main_container.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Create widgets
        self.create_widgets()
        
        # Set up window protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Header section
        header_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Title with gradient-like effect
        title_label = ctk.CTkLabel(
            header_frame,
            text="TradingView Mail-Bot",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text"]
        )
        title_label.pack(side="left")
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(
            header_frame,
            fg_color=COLORS["error"],
            corner_radius=8,
            width=120,
            height=30
        )
        self.status_frame.pack(side="right")
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Stopped",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.status_label.pack(expand=True)
        
        # Divider
        divider = ctk.CTkFrame(
            self.main_container,
            height=2,
            fg_color=COLORS["border"]
        )
        divider.pack(fill="x", padx=20, pady=10)
        
        # Control section
        control_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["background"],
            corner_radius=15
        )
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # Provider selection
        provider_frame = ctk.CTkFrame(
            control_frame,
            fg_color="transparent"
        )
        provider_frame.pack(pady=15, padx=20)
        
        provider_label = ctk.CTkLabel(
            provider_frame,
            text="AI Provider:",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_secondary"]
        )
        provider_label.pack(side="left", padx=10)
        
        self.provider_dropdown = ctk.CTkOptionMenu(
            provider_frame,
            values=["GPT", "Claude"],
            command=self.change_provider,
            fg_color=COLORS["secondary_bg"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["secondary_bg"],
            dropdown_hover_color=COLORS["accent"],
            dropdown_text_color=COLORS["text"],
            text_color=COLORS["text"],
            width=150,
            height=35,
            corner_radius=8
        )
        self.provider_dropdown.set("GPT")
        self.provider_dropdown.pack(side="left", padx=10)
        
        # Control buttons
        button_frame = ctk.CTkFrame(
            control_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=15)
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start Bot",
            command=self.start_bot,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color="white",
            width=140,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.start_button.pack(side="left", padx=10)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop Bot",
            command=self.stop_bot,
            state="disabled",
            fg_color=COLORS["error"],
            hover_color=COLORS["error_hover"],
            text_color="white",
            width=140,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.stop_button.pack(side="left", padx=10)
        
        self.test_button = ctk.CTkButton(
            button_frame,
            text="Test Now",
            command=self.test_now,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="white",
            width=140,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.test_button.pack(side="left", padx=10)
        
        # Log section
        log_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["background"],
            corner_radius=15
        )
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="Activity Log",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"]
        )
        log_label.pack(pady=(15, 10))
        
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            height=300,
            fg_color=COLORS["secondary_bg"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=13)
        )
        self.log_textbox.pack(pady=(0, 15), padx=15, fill="both", expand=True)
        
        # Footer
        footer_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        footer_frame.pack(fill="x", padx=20, pady=10)
        
        self.last_update_label = ctk.CTkLabel(
            footer_frame,
            text="Last update: Never",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        self.last_update_label.pack(side="left")
        
        # Version info
        version_label = ctk.CTkLabel(
            footer_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        version_label.pack(side="right")
    
    def log_message(self, message):
        """Append message to log textbox with timestamp"""
        timestamp = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_textbox.insert("end", formatted_message)
        self.log_textbox.see("end")
    
    def change_provider(self, choice):
        """Update the provider selection"""
        self.provider = choice
        self.log_message(f"AI Provider changed to: {choice}")
    
    def start_bot(self):
        """Start the trading bot"""
        if not self.running:
            self.running = True
            self.status_frame.configure(fg_color=COLORS["success"])
            self.status_label.configure(text="Running")
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.log_message("Bot started")
            
            # Start the bot thread
            self.thread = threading.Thread(target=self.bot_thread)
            self.thread.daemon = True
            self.thread.start()
    
    def stop_bot(self):
        """Stop the trading bot"""
        if self.running:
            self.running = False
            self.status_frame.configure(fg_color=COLORS["error"])
            self.status_label.configure(text="Stopped")
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.log_message("Bot stopped")
    
    def test_now(self):
        """Run a single cycle immediately"""
        self.log_message("Running test cycle...")
        # Run in a separate thread to prevent UI blocking
        threading.Thread(target=self.run_single_cycle).start()
    
    def run_single_cycle(self):
        """Execute a single cycle of screenshot analysis"""
        try:
            self.log_message("Looking for TradingView window...")
            screenshot_path = grab_tradingview_window()
            
            if screenshot_path:
                self.log_message(f"Screenshot taken: {screenshot_path}")
                self.log_message(f"Analyzing with {self.provider}...")
                
                report = analyze_chart(screenshot_path, provider=self.provider)
                self.log_message(f"Analysis complete:\n{report}")
                
                self.log_message("Sending email...")
                email_signal(report)
                self.log_message("Email sent successfully")
                
                # Update last action timestamp
                timestamp = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
                self.last_update_label.configure(text=f"Last update: {timestamp}")
            else:
                self.log_message("ERROR: Screenshot capture failed!")
                
        except Exception as e:
            error_message = str(e)
            if "TradingView window not found" in error_message:
                self.log_message("ERROR: TradingView window not found! Please ensure:")
                self.log_message("  1. TradingView is open in your browser or app")
                self.log_message("  2. The browser tab/window has 'TradingView' in its title")
                self.log_message("  3. The window is not fully minimized")
            else:
                self.log_message(f"ERROR: {error_message}")
            logger.error(error_message, exc_info=True)
    
    def bot_thread(self):
        """Main bot thread that runs the scheduled tasks"""
        # Schedule every 30 minutes
        schedule.every(30).minutes.do(self.run_single_cycle)
        
        # Run one cycle immediately
        self.run_single_cycle()
        
        while self.running:
            schedule.run_pending()
            time.sleep(5)
    
    def on_closing(self):
        """Handle window close event"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        self.destroy()


def main():
    app = TradingBotUI()
    app.mainloop()


if __name__ == "__main__":
    main()