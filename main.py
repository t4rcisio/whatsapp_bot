import sys
import traceback
import os

import pymsgbox
from PyQt6 import QtWidgets, QtGui  # Corrigido: Import de QtCore
from PyQt6.QtCore import QTimer, QUrl, QStandardPaths # Adicionado QStandardPaths
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEnginePage  # Adicionado QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView

from pages import home
from script import agent
from services import threads_man

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

        self.homePage.start_agent.clicked.connect(lambda state: self.exec_slm())


    def exec_slm(self):

        self.sApp = agent.Agent()

        payload = {
            "FX": self.sApp.run(),
            "DATA": False
        }

        self.rn = threads_man.ThreadService()
        self.rn.startThread(payload, self.__begin, self.__end, self.__update)

    def __begin(self, id=""):

        pass

    def __end(self, id=""):

        pass

    def __update(self, id=""):

        pass


    def open_browser(self):
        try:
            b_layout = self.homePage.widget_5.layout()
            if b_layout is None:
                b_layout = QtWidgets.QVBoxLayout(self.homePage.widget_5)
            else:
                while b_layout.count():
                    child = b_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            # Caminho persistente
            data_path = os.path.join(
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation),
                "WppWebEngineProfile"
            )
            os.makedirs(data_path, exist_ok=True)

            self.profile = QWebEngineProfile("WppProfile", self.Form)
            self.profile.setPersistentStoragePath(data_path)
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)

            # User Agent atualizado
            self.profile.setHttpUserAgent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )

            # Cria browser com perfil
            self.browser = QWebEngineView(self.Form)
            custom_page = QWebEnginePage(self.profile, self.browser)
            self.browser.setPage(custom_page)

            # ⚡ Ajustes importantes ⚡
            settings = self.browser.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)

            # Ativa WebRTC (microfone/câmera - necessário pro QRCode do WhatsApp Web)
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
            self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)

            self.browser.setUrl(QUrl("https://web.whatsapp.com/"))

            b_layout.addWidget(self.browser)
            b_layout.setContentsMargins(0, 0, 0, 0)



        except Exception as e:
            pymsgbox.alert(f"Erro ao abrir o navegador:\n{traceback.format_exc()}\n{str(e)}", "ERROR")



if __name__ == "__main__":
    # set_start_method('spawn') # Pode ser necessário em alguns casos, mas geralmente não para isso
    app = App()
    app.initialize()
