import sys
import traceback
import os

import pymsgbox
from PyQt6 import QtWidgets, QtGui, QtCore  # Corrigido: Import de QtCore
from PyQt6.QtCore import  QUrl, QStandardPaths # Adicionado QStandardPaths
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEnginePage  # Adicionado QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView

from pages import home
from script import agent
from services import threads_man

from services import storage

VERSION = "0.0.1"

class App:

    def initialize(self):
        try:
            self.app = QtWidgets.QApplication(sys.argv)
            self.homePage = home.Ui_Form()

            self.Form = QtWidgets.QWidget()
            self.homePage.setupUi(self.Form)

            self.connections()

            icon2 = QtGui.QIcon()
            # Use um caminho mais robusto ou um recurso embutido
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "wpp.png")
            if os.path.exists(icon_path):
                icon2.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            self.Form.setWindowIcon(icon2)
            self.Form.setWindowTitle("AGENT STUDIO - WWP " + str(VERSION))
            self.Form.showMaximized()

            sys.exit(self.app.exec())

        except Exception as e: # Captura mais específica
            pymsgbox.alert(f"{traceback.format_exc()}\n{str(e)}", "ERROR") # Inclui a mensagem de erro


    def connections(self):

        self.homePage.start_agent_btn.clicked.connect(lambda state: self.exec_slm())
        self.homePage.save_btn.clicked.connect(lambda state: self.save())

        self.elements()
        self.load()


    def elements(self):

        # CONFIGURA O SCROLL PARA AS CONVERSAS
        self.homePage.scroll_chats.setWidgetResizable(True)
        self.homePage.scroll_chats.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.homePage.scroll_chats.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        chatsWindow = QtWidgets.QWidget()
        self.chatsVBox = QtWidgets.QVBoxLayout(chatsWindow)
        self.chatsVBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.chatsVBox.setSpacing(6)
        self.homePage.scroll_chats.setWidget(chatsWindow)

        # CONFIGURA O SCROLL PARA AS MENSAGENS
        self.homePage.scroll_messages.setWidgetResizable(True)
        self.homePage.scroll_messages.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.homePage.scroll_messages.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        messagesWindow = QtWidgets.QWidget()
        self.messagesVBox = QtWidgets.QVBoxLayout(messagesWindow)
        self.messagesVBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.messagesVBox.setSpacing(12)
        self.homePage.scroll_messages.setWidget(messagesWindow)

        self.homePage.stop_agent_btn.setVisible(False)

        self.chats = {}
        self.__update()

    def exec_slm(self):

        self.sApp = agent.Agent()

        payload = {
            "FX": self.sApp.run,
            "DATA": None
        }

        self.rn = threads_man.ThreadService()
        self.rn.startThread(payload, self.__begin, self.__end, self.__update)

    def __begin(self):

        self.homePage.stop_agent_btn.setVisible(True)
        self.clear_layout(self.chatsVBox)
        self.chats = {}


    def __end(self):

        self.homePage.stop_agent_btn.setVisible(False)

    def __update(self):

        data = storage.chats()

        if not isinstance(data, dict):
            return

        if self.chats == data:
            return

        self.chats = data

        self.clear_layout(self.chatsVBox)

        for user_name in self.chats:

            chat_widget = QtWidgets.QWidget()
            chat_layout = QtWidgets.QHBoxLayout(chat_widget)
            chat_layout.setContentsMargins(0,0,0,0)

            chat_widget.mousePressEvent = lambda state, k=user_name: self.open_chat(k)

            chat_widget.setStyleSheet("background-color: #25D366;")
            chat_widget.setFixedHeight(40)

            user_btn = QtWidgets.QPushButton()
            user_btn.setStyleSheet("border:0px")
            user_btn.setFixedWidth(40)
            user_icon = QtGui.QIcon()
            user_icon.addPixmap(QtGui.QPixmap(".\\sources\\account-profile-essential-svgrepo-com.png"), QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.Off)
            user_btn.setIcon(user_icon)
            user_btn.setIconSize(QtCore.QSize(30, 30))

            user_title = QtWidgets.QLabel()
            user_title.setText(f'<html><head/><body><p><span style=" font-size:10pt; font-weight:600; color:#ffffff;">{user_name}</span></p></body></html>')

            chat_layout.addWidget(user_btn)
            chat_layout.addWidget(user_title)

            self.chatsVBox.addWidget(chat_widget)

    def save(self):

        config = {
            "TEMPLATE": self.homePage.sys_template.toPlainText(),
            "SUPERVISOR": self.homePage.supervisor_template.toPlainText(),
            "RESPONSE_DELAY": self.homePage.response_delay.text(),
        }

        storage.config(config)
        pymsgbox.alert("CONFIGURAÇÕES SALVAS!", "NOTICE")

    def load(self):

        config =  storage.config()

        if not isinstance(config, dict):
            return

        self.homePage.sys_template.setText(config["TEMPLATE"])
        self.homePage.supervisor_template.setText(config["SUPERVISOR"])
        self.homePage.response_delay.setText(config["RESPONSE_DELAY"])



    def open_chat(self, user_name):

            self.clear_layout(self.messagesVBox)

            for message in self.chats[user_name]:
                # widget que contém a mensagem
                text_widget = QtWidgets.QWidget()
                text_layout = QtWidgets.QHBoxLayout(text_widget)
                text_layout.setContentsMargins(10, 0, 10, 0)
                text_layout.setSpacing(0)

                # bolha da mensagem
                user_message = QtWidgets.QLabel()
                user_message.setText(
                    f'<html><head/><body><p><span style=" font-size:10pt; font-weight:600; color:#ffffff;">{message[1]}</span></p></body></html>'
                )
                user_message.setWordWrap(True)
                user_message.setStyleSheet("""
                    background-color: #25D366;
                    border-radius: 10px;
                    padding: 8px;
                    color: white;
                """)
                user_message.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred,
                                           QtWidgets.QSizePolicy.Policy.Preferred)

                # limitar largura máxima da "bolha"
                user_message.setMaximumWidth(400)  # ajuste para sua tela

                # alinhamento (usando spacers para não expandir o widget inteiro)
                if message[2] == "assistant":
                    text_layout.addStretch()  # empurra para a direita
                    text_layout.addWidget(user_message)
                else:
                    text_layout.addWidget(user_message)
                    text_layout.addStretch()  # empurra para a esquerda

                self.messagesVBox.addWidget(text_widget)



    def clear_layout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                if item.layout() is not None:
                    self.clear_layout(item.layout())




if __name__ == "__main__":
    # set_start_method('spawn') # Pode ser necessário em alguns casos, mas geralmente não para isso
    app = App()
    app.initialize()
