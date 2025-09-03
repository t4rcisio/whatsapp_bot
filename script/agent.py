import locale
import traceback

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime

from ollama import chat

from script import supervisor
from services import webEngine

from services import storage


class Agent:


    def __init__(self):

        self.chats = {}
        self.supervisor = supervisor.Supervisor()


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

            for index in range(1, 30):

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

                    validator = self.supervisor.ask(self.chats[user_name]["HISTORY"][-1])

                    if

                    message = self.ask(user_name)


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

        try:
            user_msgs = self.chats[name]["USER_MESSAGE"]
            ai_msgs = self.chats[name]["AI_MESSAGE"]

            # junta as duas listas
            all_msgs = user_msgs + ai_msgs

            # ordena pela data (dt é o índice 0 de cada item)
            all_msgs.sort(key=lambda x: x[0])

            # salva no dicionário


            if all_msgs[-1][2] == 'assistant':
                self.chats[name]["SLEEP"] = True

            if not (all_msgs[-1][0] + datetime.timedelta(minutes=5)) < datetime.datetime.now():
                self.chats[name]["SLEEP"] = True

            self.chats[name]["FULL_CONVERSATION"] = all_msgs

        except:
            self.chats[name]["SLEEP"] = True
            print(traceback.format_exc())



    def build_template(self, name):

        history = []

        try:

            sys_template = open('.\\template', "r", encoding="UTF-8").read()
            sys_template = sys_template.replace('#NAME', name)
            sys_template = sys_template.replace('#INFO', self.get_date())

            history.append({"role": "system","content": sys_template})

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

    def sendMessage(self, message):

        message = message.replace("**","*")

        try:
            self.web.click(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div/p', max=2, timeAfter=1)
            for token in message.split("\n"):
                s_tokens = self.split_token(token, 30)
                for s_token in s_tokens:
                    self.web.sendKeys(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div/p',s_token, max=2)
                self.web.sendKeys(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div/p'," ", max=2)
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

    def split_token(self, texto, n):
        return [texto[i:i + n] for i in range(0, len(texto), n)]

    def shift_enter(self, driver):
        ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()

    def get_chat_messages(self, name, type):

        k_list = []

        chat_box = self.web.getElement(By.CLASS_NAME, 'x3psx0u', max=2)
        messages = self.web.getElements(By.CLASS_NAME, type, chat_box, max=2)

        for i in range(len(messages) - 1, -1, -1):
            try:
                details = self.web.getElement(By.CLASS_NAME, 'copyable-text', messages[i],  max=2)
                o_msg = details.get_attribute('data-pre-plain-text')
                text = self.web.getText(By.CLASS_NAME, '_ao3e', messages[i],  max=2)

                parte_data = o_msg.split("]")[0].strip("[")
                dt = datetime.datetime.strptime(parte_data, "%H:%M, %m/%d/%Y")

                k_list.append([dt, text, name])
            except:
                return k_list
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



    def ask(self, name):

        try:
            response = chat('qwen3:1.7b', self.chats[name]["HISTORY"])

            total_seconds = response.total_duration
            total_tokens = response.prompt_eval_count

            return response.message.content
        except:
            return False
