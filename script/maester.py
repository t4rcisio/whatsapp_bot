import locale
import re
import time
import traceback

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime


from services import webEngine
from services import storage

from script import  llm_services




class Maester:


    def __init__(self):

        self.chats = {}
        self.agent_executor = False

        self.llm_services = llm_services.Lmm_services()


    def run(self):


        self.start_selenium()

        self.wait = WebDriverWait(self.web.driver, 3)

        while True:

            #chats = self.web.getElements(By.CLASS_NAME, 'xuxw1ft')
            chat_title = self.web.getText(By.XPATH, '//*[@id="pane-side"]/div[1]/div/div/div[1]', max=1)


            if not isinstance(chat_title, str):
                continue

            if chat_title == "":
                continue

            for index in range(1, 6):

                chat_title = self.web.getText(By.XPATH, '//*[@id="pane-side"]/div[1]/div/div/div['+str(index)+']', max=1)

                if not isinstance(chat_title, str):
                    continue

                user_name = chat_title.split("\n")[0]

                #user_name = self.getText(name)

                if user_name == False or user_name == "": #or user_name not in ["Mãe", "Pai", 'Enzola']:
                    continue

                if not user_name in self.chats:
                    self.chats[user_name]  = {"USER_MESSAGE": [], "AI_MESSAGE": [], "FULL_CONVERSATION": [], "HISTORY": [], "SLEEP": True}

                if self.openChat(user_name):


                    u_message = self.get_chat_messages(user_name, 'message-in')

                    if u_message == []:
                        continue

                    if u_message == self.chats[user_name]['USER_MESSAGE']:
                        continue

                    self.chats[user_name]['USER_MESSAGE'] = u_message
                    self.chats[user_name]['AI_MESSAGE'] = self.get_chat_messages('assistant', 'message-out')

                    if len(self.chats[user_name]['USER_MESSAGE']) == 0:
                        continue

                    self.chats[user_name]["FULL_CONVERSATION"] = []

                    self.chats[user_name]["SLEEP"] = False
                    self.build_conversation(user_name)

                    self.fix_ui_message(user_name)

                    if self.chats[user_name]["SLEEP"] == True:
                        continue

                    if self.chats[user_name]["FULL_CONVERSATION"] == []:
                        continue

                    self.build_template(user_name)

                    if len(self.chats[user_name]["HISTORY"]) == 0:
                        continue
                    self.chats[user_name]["FULL_CONVERSATION"] = self.chats[user_name]["FULL_CONVERSATION"][-10:]
                    messages_input = []

                    for message_a in self.chats[user_name]["FULL_CONVERSATION"]:


                        if message_a[2] != "assistant":
                            message_a[2] = "user"

                        messages_input.append({"role": message_a[2], "content": message_a[1]})

                    message =  self.live_chat(messages_input)

                    if message == False:
                        continue

                    message = message.split("</think>")[-1].strip()

                    if self.sendMessage(message):
                        self.chats[user_name]['AI_MESSAGE'].append([datetime.datetime.now(), message, 'assistant'])
                        print("Mensagem enviada")
                    else:
                        print("Mensagem não enviada")
                else:
                    print("Mensagem não enviada")

            self.web.driver.get("https://web.whatsapp.com/")

    def fix_ui_message(self, user_name):

        data = []
        for item in self.chats[user_name]["FULL_CONVERSATION"]:

            m_data = item
            m_data[0] = str(item[0])
            data.append(m_data)


        u_messages = storage.chats()

        if not isinstance(u_messages, dict):
            u_messages = {}

        u_messages[user_name] = data
        storage.chats(u_messages)


    def build_conversation(self, name):

        data = storage.config()

        try:
            delay = int(str(data["RESPONSE_DELAY"]).strip())
        except:
            delay = 30

        try:
            response_at = int(str(data["RESPONSE_AT"]).strip())
        except:
            response_at = 30

        try:
            user_msgs = self.chats[name]["USER_MESSAGE"]
            ai_msgs = self.chats[name]["AI_MESSAGE"]

            # junta as duas listas
            all_msgs = user_msgs + ai_msgs

            # ordena pela data (dt é o índice 0 de cada item)
            all_msgs.sort(key=lambda x: x[0])

            # salva no dicionário

            if not isinstance(all_msgs[-1][0], datetime.datetime):
                time_last_message =  datetime.datetime.strptime(all_msgs[-1][0], "%Y-%m-%d %H:%M:%S")
            else:
                time_last_message = all_msgs[-1][0]


            if all_msgs[-1][2] == 'assistant':
                self.chats[name]["SLEEP"] = True

            if ( time_last_message + datetime.timedelta(seconds=delay)) >= datetime.datetime.now():
                self.chats[name]["SLEEP"] = True

            if (time_last_message + datetime.timedelta(seconds=response_at)) < datetime.datetime.now():
                self.chats[name]["SLEEP"] = True

            self.chats[name]["FULL_CONVERSATION"] = all_msgs

        except:
            self.chats[name]["SLEEP"] = True
            print(traceback.format_exc())



    def build_template(self, name):

        history = []

        try:

            for message in self.chats[name]["FULL_CONVERSATION"]:

                if message[-1] == name:
                    history.append({"role": "user", "content": message[1]})
                else:
                    history.append({"role": "assistant", "content": message[1]})

            self.chats[name]["HISTORY"] =  history
        except:
            return []


    def openChat(self, name):

        try:

            target = f'"{name}"'
            self.wait = WebDriverWait(self.web.driver, 3)

            contact_path = '//span[contains(@title,' + target + ')]'
            contact = self.wait.until(EC.presence_of_element_located((By.XPATH, contact_path)))
            contact.click()
            return True
        except:
            print(traceback.format_exc())
            return False


    def build_chunks(self, message):

        final_chunks = []
        g_chunks = message.split("\n")
        final_chunks =  g_chunks
        return final_chunks


    def sendMessage(self, message):

        message = message.replace("**","*")

        try:
            self.web.click(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div/p', max=2, timeAfter=1)

            chunks = self.build_chunks(message)
            for token in chunks:
                s_tokens = self.split_token(token, 30)
                for s_token in s_tokens:
                    s_token = self.remove_emojis(s_token)
                    self.web.sendKeys(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div/p',s_token, max=2, timeAfter=0.5)
                self.web.sendKeys(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div/p'," ", max=2, timeAfter=0.5)
                self.shift_enter(self.web.driver)


            send = self.web.getElement(By.XPATH,'//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/button', max=2)
            try:
                valor = send.get_attribute("aria-label")
                if valor == 'Enviar':
                    self.web.click(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/button',max=2)
            except:
                pass

            return True
        except:
            print(traceback.format_exc())
            return False

    def remove_emojis(self, text):
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # símbolos e pictogramas
            "\U0001F680-\U0001F6FF"  # transporte e símbolos
            "\U0001F1E0-\U0001F1FF"  # bandeiras (letras de países)
            "\U00002700-\U000027BF"  # símbolos diversos
            "\U0001F900-\U0001F9FF"  # suplementos de símbolos e pictogramas
            "\U00002600-\U000026FF"  # símbolos diversos
            "\U00002B00-\U00002BFF"  # setas adicionais
            "\U0001FA70-\U0001FAFF"  # objetos adicionais
            "\U000025A0-\U000025FF"  # formas geométricas
            "]+", flags=re.UNICODE)

        return emoji_pattern.sub(r'', text)

    def split_token(self, texto, n):
        return [texto[i:i + n] for i in range(0, len(texto), n)]

    def shift_enter(self, driver):
        ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()

    def get_chat_messages(self, name, type):

        k_list = []

        chat_box = self.web.getElement(By.CLASS_NAME, 'x3psx0u', max=2, timeAfter=1)
        messages = self.web.getElements(By.CLASS_NAME, type, chat_box, max=2, timeAfter=1)

        for i in range(len(messages) - 1, -1, -1):
            try:
                details = self.web.getElement(By.CLASS_NAME, 'copyable-text', messages[i],  max=2)
                o_msg = details.get_attribute('data-pre-plain-text')
                text = self.web.getText(By.CLASS_NAME, '_ao3e', messages[i],  max=2)

                parte_data = o_msg.split("]")[0].strip("[")
                dt = datetime.datetime.strptime(parte_data, "%H:%M, %m/%d/%Y")

                k_list.append([dt, text, name])
            except:
                pass
        return k_list


    def getText(self, element):

        try:
            return element.text
        except:
            return False

    def start_selenium(self):

        self.web = webEngine.Webdriver_X()
        self.web.openBrowser()
        self.web.driver.get("https://web.whatsapp.com/")

    def live_chat(self, payload):

        print(payload)

        response_maester = self.llm_services.classify_chat(payload)

        if not isinstance(response_maester, dict):
            msg_nao_entendi = "Desculpe, não consegui entender sua mensagem 😅.\nPode reformular ou me dar mais detalhes? Posso te ajudar com nossos produtos, promoções e serviços da Gota Mágica Cosméticos.\nPara informações precisas, você também pode nos chamar no WhatsApp (33) 98895-5154!"
            self.send_message_to_ui(msg_nao_entendi)
            return msg_nao_entendi

        elif response_maester['message_context'] == 'greeting_context':
            msg_boas_vindas = "Olá! 👋 Bem-vindo(a) à Gota Mágica Cosméticos!\nSou Gotinha, seu assistente virtual.\nPosso te ajudar a conhecer nossos produtos, consultar estoque ou promoções.\nSe quiser, também posso te orientar sobre pedidos e contas.\nComo posso te atender hoje?"
            self.send_message_to_ui(msg_boas_vindas)
            return msg_boas_vindas

        elif response_maester['on_context'] == False:
            msg_nao_entendi = "Desculpe, não consegui entender sua mensagem 😅.\nPode reformular ou me dar mais detalhes?\nPosso te ajudar com nossos produtos, promoções e serviços da Gota Mágica Cosméticos.\nPara informações precisas, você também pode nos chamar no WhatsApp (33) 98895-5154!"
            self.send_message_to_ui(msg_nao_entendi)
            return msg_nao_entendi

        elif response_maester['message_context'] == 'simple_context':
            resp = self.llm_services.ask_simple_context(payload)
            return resp

        if self.agent_executor == False:
            self.llm_services.loadAgent()

        return self.llm_services.ask_complex_context(payload)

    def send_message_to_ui(self, final_output):

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
            storage.chat(self.markdown_to_html(chat_text))

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









