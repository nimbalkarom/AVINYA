import os
import sys
import time
import datetime
import subprocess
import platform
import webbrowser
import threading

# Third-party libraries
try:
    import speech_recognition as sr
    import pyttsx3
    import google.generativeai as genai
    import psutil
    import pyautogui
except ImportError as e:
    print(f"[FAIL] Error: Missing dependencies. Please run 'pip install -r requirements.txt'")
    print(f"Specific missing module: {e}")
    sys.exit(1)

# ============================================
# ⚙️ CONFIGURATION - EDIT THIS SECTION
# ============================================

# 🔑 PASTE YOUR GEMINI API KEY HERE
# Get it from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = "AIzaSyBm8PLJFkXlKTr4icAEdeSfShgVlnHUwgo" 

# Voice Settings
VOICE_RATE = 180  # Speed of speech
VOICE_VOLUME = 1.0 # Volume (0.0 to 1.0)

# Language Settings
LANGUAGE_CODES = {
    'english': 'en-US',
    'hindi': 'hi-IN',
    'chinese': 'zh-CN',
    'russian': 'ru-RU',
    'japanese': 'ja-JP',
    'spanish': 'es-ES'
}

# ============================================
# 🧠 AVINYA BRAIN & BODY
# ============================================

def print_banner():
    banner = r"""
    _    _   _ ___ _   1YA
   / \  | | | |_ _| \ | \ \ / /   / \
  / _ \ | | | || ||  \| |\ V /   / _ \
 / ___ \| |_| || || |\  | | |   / ___ \
/_/   \_\___/|___|_| \_| |_|  /_/   \_\
    
    [ SYSTEM ONLINE ]
    """
    print(banner)

class Avinya:
    def __init__(self):
        print_banner()
        print("[INIT] Initializing Avinya...")
        
        # 1. Initialize Speech Engine (The Mouth)
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', VOICE_RATE)
            self.engine.setProperty('volume', VOICE_VOLUME)
            
            # Try to select a good voice
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id) # Default to first voice
        except Exception as e:
            print(f"[WARN] Text-to-Speech initialization failed: {e}")
            self.engine = None

        # 2. Initialize Speech Recognition (The Ears)
        self.recognizer = sr.Recognizer()
        self.current_language = 'en-US'
        self.listening = True

        # 3. Initialize Gemini AI (The Brain)
        if "PASTE_YOUR_KEY_HERE" in GEMINI_API_KEY:
             print("[FAIL] ERROR: You must paste your Gemini API Key in the code!")
             self.speak("Please paste your Google Gemini API key in the script to continue.")
             sys.exit(1)
        
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.chat = self.model.start_chat(history=[])
        except Exception as e:
            print(f"[FAIL] Error connecting to Gemini: {e}")
            self.speak("I could not connect to my brain. Please check your internet or API key.")
            sys.exit(1)

        print("[ OK ] Avinya is Online and Ready!")

    def speak(self, text):
        """Convers text to speech"""
        print(f"[AI]   Avinya: {text}")
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()

    def listen(self):
        """Listens for audio input"""
        with sr.Microphone() as source:
            print(f"\n[MIC]  Listening ({self.current_language})...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("[....] Processing...")
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio, language=self.current_language)
                print(f"[USER] You: {text}")
                return text.lower()
            
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                print("msg: I didn't catch that.")
                return ""
            except sr.RequestError as e:
                print(f"[FAIL] Network error: {e}")
                self.speak("I'm having trouble connecting to Google speech services.")
                return ""
            except Exception as e:
                print(f"[FAIL] Audio error: {e}")
                return ""

    def get_system_status(self):
        """Returns PC stats"""
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        power = f", Battery: {battery.percent}%" if battery else ""
        return f"CPU Usage is at {cpu} percent. Memory usage is {mem} percent{power}."

    def execute_command(self, command):
        """Parses and executes commands"""
        
        # 🛑 Exit
        if any(w in command for w in ['exit', 'quit', 'shutdown avinya', 'bye']):
            self.speak("Goodbye, Sir. Have a nice day.")
            self.listening = False
            return

        # 🖥️ System Info
        elif 'system' in command and ('info' in command or 'status' in command or 'stats' in command):
            info = self.get_system_status()
            self.speak(info)

        # ⌚ Time & Date
        elif 'time' in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"It is currently {now}")
        elif 'date' in command:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {today}")

        # 📂 Applications
        elif 'open' in command:
            app_name = command.replace('open', '').strip()
            self.speak(f"Opening {app_name}")
            
            # Common Apps Map
            apps = {
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'chrome': 'chrome.exe',
                'browser': 'msedge.exe',
                'edge': 'msedge.exe',
                'settings': 'start ms-settings:',
                'cmd': 'start cmd',
                'powershell': 'start powershell'
            }
            
            try:
                if app_name in apps:
                    os.system(apps[app_name]) # Use os.system for simple commands
                else:
                    # Try generic start
                    if platform.system() == "Windows":
                        os.system(f"start {app_name}")
                    else:
                        self.speak("I can only open apps reliably on Windows for now.")
            except Exception:
                self.speak(f"I couldn't find an app named {app_name}")

        # 🌐 Web Search
        elif 'search' in command or 'google' in command:
            query = command.replace('search', '').replace('google', '').replace('for', '').strip()
            if query:
                self.speak(f"Searching Google for {query}")
                webbrowser.open(f"https://www.google.com/search?q={query}")

        # 🔊 Volume Control
        elif 'volume' in command:
            if 'up' in command or 'increase' in command:
                pyautogui.press('volumeup', presses=5)
                self.speak("Increasing volume")
            elif 'down' in command or 'decrease' in command:
                pyautogui.press('volumedown', presses=5)
                self.speak("Decreasing volume")
            elif 'mute' in command:
                pyautogui.press('volumemute')
                self.speak("Muted")
        
        # 📸 Screenshot
        elif 'screenshot' in command:
            try:
                file_name = f"screenshot_{int(time.time())}.png"
                pyautogui.screenshot(file_name)
                self.speak(f"Screenshot saved as {file_name}")
            except Exception:
                self.speak("I failed to take a screenshot.")

        # 🗣️ Language Switching
        elif 'switch language to' in command or 'change language to' in command:
            found = False
            for lang, code in LANGUAGE_CODES.items():
                if lang in command:
                    self.current_language = code
                    self.speak(f"Switched language to {lang}")
                    found = True
                    break
            if not found:
                self.speak("I don't support that language yet.")

        # ======================================================================================
        # ➕ ADD YOUR CUSTOM COMMANDS HERE
        # ======================================================================================
        # Example:
        # elif 'joke' in command:
        #     self.speak("Why did the chicken cross the road? To get to the other side!")
        # ======================================================================================

        # 🧠 Ask Gemini (Default)
        else:
            self.ask_gemini(command)

    def ask_gemini(self, prompt):
        """Send query to Gemini"""
        try:
            # Context injection
            system_instruction = f"""
            You are Avinya, a helpful AI assistant on a user's computer.
            Current Time: {datetime.datetime.now().strftime("%I:%M %p")}
            User input: {prompt}
            
            Instructions:
            1. Keep answers concise and helpful (1-3 sentences for simple questions).
            2. If the user asks for code, provide it.
            3. Be polite and professional.
            """
            
            response = self.chat.send_message(system_instruction)
            text = response.text
            
            # Clean up text for speech (remove * or markdown if needed, though most TTS handles it ok)
            clean_text = text.replace('*', '').replace('#', '')
            
            self.speak(clean_text)
            
        except Exception as e:
            error_str = str(e)
            print(f"[FAIL] Gemini Error: {e}")
            
            if "429" in error_str:
                self.speak("I have reached my daily thinking limit. Please try again later.")
            elif "404" in error_str:
                self.speak("I am having trouble accessing my improved brain model.")
            else:
                self.speak("I'm having trouble reaching my brain right now.")

    def run(self):
        """Main Loop"""
        self.speak("Avinya online. Waiting for instructions.")
        
        while self.listening:
            try:
                # Prompt for input
                print("\nOptions:")
                print("1. Type your command and press Enter")
                print("2. Press Enter (without typing) to use Voice")
                
                # Use input() to capture text. 
                # If user just presses Enter, text is empty -> activate voice.
                text = input("User Input: ").strip()
                
                if text:
                    # Text command provided
                    self.execute_command(text.lower())
                else:
                    # Empty input -> Voice command
                    command = self.listen()
                    if command:
                        self.execute_command(command)
                        
                time.sleep(0.5)
            except KeyboardInterrupt:
                self.listening = False
                print("\n[STOP] Stopping...")

if __name__ == "__main__":
    try:
        app = Avinya()
        app.run()
    except Exception as e:
        print(f"[CRIT] Critical Error: {e}")
        input("Press Enter to exit...")
