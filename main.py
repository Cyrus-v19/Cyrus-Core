import os, json, requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from plyer import tts

API_KEY = os.environ.get("GROQ_API_KEY", "")

def load_mem():
    if os.path.exists("memory.json"):
        with open("memory.json") as f:
            return json.load(f)
    return {"name": None, "goals": [], "projects": [], "notes": [], "tasks": [], "history": []}

def save_mem(mem):
    with open("memory.json", "w") as f:
        json.dump(mem, f, indent=2)

def ask_cyrus(text, mem):
    system_prompt = f"""You are Cyrus, Samuel's personal AI assistant.
Name: {mem.get('name')}
Goals: {mem.get('goals')}
Projects: {mem.get('projects')}
Notes: {mem.get('notes')}
Tasks: {mem.get('tasks')}
Be concise and direct."""
    history = mem["history"][-10:]
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": text}]
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "max_tokens": 800
        }
    )
    reply = r.json()["choices"][0]["message"]["content"]
    mem["history"].append({"role": "user", "content": text})
    mem["history"].append({"role": "assistant", "content": reply})
    save_mem(mem)
    return reply

def handle_builtin(text, mem):
    t = text.lower().strip()
    if t.startswith("remember my name is"):
        mem["name"] = text[20:].strip(); save_mem(mem)
        return f"Got it, {mem['name']}."
    if t.startswith("add goal "):
        mem["goals"].append(text[9:].strip()); save_mem(mem); return "Goal added."
    if t.startswith("add project "):
        mem["projects"].append(text[12:].strip()); save_mem(mem); return "Project added."
    if t.startswith("add note "):
        mem["notes"].append(text[9:].strip()); save_mem(mem); return "Note saved."
    if t.startswith("add task "):
        mem["tasks"].append(text[9:].strip()); save_mem(mem); return "Task added."
    if t == "show memory":
        return json.dumps(mem, indent=2)
    return None

class CyrusUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.mem = load_mem()

        self.scroll = ScrollView()
        self.chat_log = Label(size_hint_y=None, text="Cyrus is online.\n", halign="left", valign="top")
        self.chat_log.bind(texture_size=self._update_height)
        self.scroll.add_widget(self.chat_log)
        self.add_widget(self.scroll)

        self.input = TextInput(size_hint_y=None, height=50, multiline=False)
        self.input.bind(on_text_validate=self.send_text)
        self.add_widget(self.input)

        btn_row = BoxLayout(size_hint_y=None, height=60)
        send_btn = Button(text="Send")
        send_btn.bind(on_press=self.send_text)
        mic_btn = Button(text="Speak")
        mic_btn.bind(on_press=self.voice_input)
        btn_row.add_widget(send_btn)
        btn_row.add_widget(mic_btn)
        self.add_widget(btn_row)

    def _update_height(self, *a):
        self.chat_log.height = self.chat_log.texture_size[1]
        self.chat_log.text_size = (self.chat_log.width, None)

    def append_log(self, who, text):
        self.chat_log.text += f"\n{who}: {text}\n"

    def process(self, text):
        if not text.strip():
            return
        self.append_log("You", text)
        reply = handle_builtin(text, self.mem) or ask_cyrus(text, self.mem)
        self.append_log("Cyrus", reply)
        try:
            tts.speak(reply)
        except Exception:
            pass

    def send_text(self, *a):
        text = self.input.text
        self.input.text = ""
        self.process(text)

    def voice_input(self, *a):
        self.append_log("Cyrus", "Voice input wiring comes in the next update.")

class CyrusApp(App):
    def build(self):
        return CyrusUI()

if __name__ == "__main__":
    CyrusApp().run()
