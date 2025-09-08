import datetime
import locale
import re
import time
import traceback

import json5
import ollama
from ollama import chat

from services import storage

from langchain.agents import AgentExecutor, create_react_agent, BaseSingleActionAgent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from script.db_tools import tools as user_tools


class Lmm_services:


    def __init__(self):

        self.agent_executor = False

        self.mester_model = "qwen3:1.7b"
        self.light_model = "qwen3:1.7b"
        self.agent_model = "qwen3:1.7b"


    def classify_chat(self, content: list):

        messages_context = "## INTERACTIONS\n\n"

        for message in content:

            if message["role"] != "assistant":
                messages_context += "from: user: " + message["content"] + "\n"
            else:
                messages_context += f"from: {message["role"]}: " + message["content"] + "\n"

        config = storage.config()

        try:
            response = chat(self.mester_model,
                            [{"role": "system", "content": config['SUPERVISOR']},
                             {"role": "user", "content": "\n\n This messages " + str(
                                           messages_context) + "\nComplete this json: {'on_context': '','message_context': ''}"}
                                       ])

            try:
                response = json5.loads(str(response.message.content).split("</think>")[-1])
                return response
            except:
                return False
        except:
            print(traceback.format_exc())
            return False


    def ask_simple_context(self, messages):


        try:
            config = storage.config()


            input_messages = [{"role": "system", "content": config['SUPERVISOR']}] + messages

            response =  ollama.chat(
                self.light_model,
                input_messages,
                stream=True
            )

            full_response = ""

            for chunk in response:
                content = chunk['message'].content
                full_response += content
                storage.chat(full_response)
                yield content

            try:
                response = json5.loads(str(full_response).split("</think>")[-1])
                return response
            except:
                return False
        except:
            print(traceback.format_exc())
            return False

    def ask_complex_context(self, messages):

        try:

            if self.agent_executor == False:
                self.loadAgent()

            final_output = ""
            response_output = ""

            for chunk in self.agent_executor.stream({"input": messages}):
                # Stream de ações (pensamentos e chamadas de ferramentas)
                if "actions" in chunk:
                    for action in chunk["actions"]:
                        log = action.log.strip() if action.log else "Pensando..."
                        print(f"💭 {log}")
                        print(f"🛠️ Ação: {action.tool}")
                        print(f"📦 Entrada: {action.tool_input}")

                # Stream de observações (resultados das ferramentas)
                elif "steps" in chunk:
                    for step in chunk["steps"]:
                        obs = step.observation.strip()
                        print(f"🔍 Observação: {obs}")

                # Resposta final
                elif "output" in chunk:
                    final_output = chunk["output"].strip()
                    response_output = final_output
                    print(f"\n✅ Resposta Final: {final_output}")

                else:
                    print(chunk)

            chat_text = ""

            palavras = final_output.split(" ")

            for i, palavra in enumerate(palavras):
                if i > 0:
                    chat_text += " "
                    html_chunk = self.markdown_to_html(chat_text)
                    storage.chat(html_chunk)
                    time.sleep(0.03)

                for char in palavra:
                    chat_text += char
                    html_chunk = self.markdown_to_html(chat_text)
                    storage.chat(html_chunk)
                    time.sleep(0.03)

                chat_text += " "
                storage.chat(chat_text)

            return response_output

        except Exception as e:
            error_msg = f"❌ Erro: {str(e)}"
            print(error_msg)
            return False


    def loadAgent(self):

        try:

            if self.agent_executor == False:

                sys_template = open('.\\sources\\agentic_template', "r", encoding="UTF-8").read()
                conf = storage.config()

                user_template = conf['TEMPLATE'].replace('#INFO', self.get_date())

                self.llm = ChatOpenAI(
                    model= self.agent_model,
                    api_key="ollama",
                    base_url="http://localhost:11434/v1",
                )

                full_template = sys_template.replace("#TEMPLATE", user_template)
                self.prompt = PromptTemplate( input_variables=["input", "tools", "tool_names", "agent_scratchpad"], # ← ajustado!
                                              template=full_template )

                self.agent = create_react_agent(self.llm,
                                                user_tools,
                                                self.prompt)

                self.agent_executor = AgentExecutor(
                    user_template=user_template,
                    agent=self.agent,
                    tools=user_tools,
                    #verbose=True,
                    handle_parsing_errors=True)
        except:
            print(traceback.format_exc())


    def markdown_to_html(self, text: str) -> str:
        """
        Converte **texto** em <b>texto</b> e preserva quebras de linha.
        Escapa caracteres HTML perigosos para segurança.
        """
        if not isinstance(text, str):
            return ""

        # 1. Escapa caracteres HTML especiais
        text = text.replace("&", "&amp;").replace("<", "<").replace(">", ">")

        # 2. Converte **texto** → <b>texto</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

        # 3. Converte quebras de linha para <br>
        text = text.replace("\n", "<br>")

        return text

    def get_date(self):

        try:

            locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

            agora = datetime.datetime.now()
            dia = agora.strftime("%d/%m/%Y")
            hora = agora.strftime("%H:%M")
            dia_semana = agora.strftime("%A")  # agora sai em português

            texto = f"Hoje é : {dia_semana}, {dia}\nAgora são: {hora}"
            return texto
        except:
            return ""