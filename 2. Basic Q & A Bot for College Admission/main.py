import json
from difflib import get_close_matches
from bardapi import Bard
from typing import Dict
import os

KB_FILE_PATH = "kb.json"
BARD_API_KEY = os.environ.get("_BARD_API_KEY")

class KnowledgeBase:
    def __init__(self, file_path: str):
        self.questions: Dict[str, str] = {}
        self.load_from_file(file_path)

    def load_from_file(self, file_path: str):
        try:
            with open(file_path, 'r') as f:
                self.questions = json.load(f)
        except FileNotFoundError:
            print(f"Knowledge base file not found: {file_path}")

    def save_to_file(self, file_path: str):
        with open(file_path, 'w') as f:
            json.dump(self.questions, f, indent=2)

    def find_answer(self, question: str) -> str | None:
        return self.questions.get(question)


class ChatBot:
    def __init__(self):
        self.kb = KnowledgeBase(KB_FILE_PATH)

    def handle_user_input(self, user_input: str) -> str:
        best_match = get_close_matches(user_input, self.kb.questions.keys(), n=1, cutoff=0.6)
        if best_match:
            answer = self.kb.find_answer(best_match[0])
        else:
            try:
                answer = Bard(api_key=BARD_API_KEY).get_answer(user_input)['content']
                self.kb.questions[user_input] = answer
                self.kb.save_to_file(KB_FILE_PATH)
            except Exception as e:
                print(f"Error fetching answer from Bard: {e}")
                answer = "Sorry, I'm unable to answer that question at the moment."
        return answer

    def run(self):
        print("Welcome to XYZ College. How may i help you?")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                print("Thank you for chatting!")
                break
            answer = self.handle_user_input(user_input)
            print(f"Bot: {answer}")

if __name__ == '__main__':
    if not BARD_API_KEY:
        print("Please set the _BARD_API_KEY environment variable.")
    else:
        chatbot = ChatBot()
        chatbot.run()
