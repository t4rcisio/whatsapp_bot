

from ollama import chat
from services import storage

class Supervisor:


    def check_question(self, user_message):

        return ""


    def check_response(self, ai_response):

        return ""


    def ask(self, content):

        config = storage.config()


        try:
            response = chat('qwen3:1.7b', [{"role": "system",
                                                      "content": config['SUPERVISOR']}] + content)

            total_seconds = response.total_duration
            total_tokens = response.prompt_eval_count

            return response.message.content
        except:
            return False