import os
import time
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from selenium.webdriver.common.by import By

class Webdriver_X:

    def __init__(self):

        self.driver = None


    def openBrowser(self, path=""):

        self.downloadPath = ".\\"
        self.driver = self.__genDrive()
        return self.driver


    def awaitDownload(self, pathList, timeAfter=0, max=90):

        counter = 0
        while counter != max:

            for path in pathList:
                if os.path.exists(path):
                    time.sleep(timeAfter)
                    return path

            counter +=1
            time.sleep(1)

        return False


    def executeScript(self, script, timeAfter=0, max=30):

        try:
            self.driver.execute_script(script)
            time.sleep(timeAfter)
        except:
            return False



    def selectOnDropDown(self, selectElement, text="", getSelected=False, timeAfter=0, max=30):

        counter = 0

        while counter != max:

            try:

                select = Select(selectElement)

                if getSelected:
                    return select.first_selected_option.text

                index = 0
                for item in select.options:
                    if item.text == text:
                        select.select_by_index(index)
                        break
                    index +=1

                time.sleep(timeAfter)
                return False
            except:

                counter += 1
                time.sleep(1)

        return False

    def clickOnElementOnList(self, mode, id, textCompare, element=None, timeAfter=0, max=30):

        counter = 0
        if element == None:
            element = self.driver

        while counter != max:

            try:

                searchList = self.getElements(mode, id, element=element, timeAfter=1, max=2)

                for index in range(0, len(searchList)):

                    if searchList[index].text == textCompare:
                        searchList[index].click()
                        return True

                time.sleep(timeAfter)
                return False
            except:

                counter += 1
                time.sleep(1)

        return False


    def clickOnElementOnList_in(self, mode, id, textCompare, element=None, timeAfter=0, max=30):

        counter = 0
        if element == None:
            element = self.driver

        while counter != max:

            try:

                searchList = self.getElements(mode, id, element=element, timeAfter=1, max=5)

                for index in range(0, len(searchList)):

                    if textCompare in searchList[index].text:
                        searchList[index].click()
                        return True

                time.sleep(timeAfter)
                return False
            except:

                counter += 1
                time.sleep(1)

        return False


    def click(self, mode, id, element=None, timeAfter=0, max=30):

        counter  = 0
        if element == None:
            element = self.driver


        while counter != max:

            try:

                element.find_element(mode, id).click()
                time.sleep(timeAfter)
                return True
            except:

                counter +=1
                time.sleep(1)

        return False

    def sendKeys(self, mode, id, value, element=None, timeAfter=0, max=30):

        counter = 0
        if element == None:
            element = self.driver


        while counter != max:

            try:
                try:
                    element.find_element(mode, id).clear()
                except:
                    pass
                element.find_element(mode, id).send_keys(value)
                time.sleep(timeAfter)
                return True
            except:

                counter += 1
                time.sleep(1)

        return False


    def getText(self, mode, id, element=None, timeAfter=0, max=30):

        counter = 0
        if element == None:
            element = self.driver



        while counter != max:

            try:

                value = element.find_element(mode, id).text
                time.sleep(timeAfter)
                return value
            except:
                counter += 1
                time.sleep(1)

        return False


    def getProp(self, mode, id, propName, element=None,timeAfter=0, max=30):

        counter = 0
        if element == None:
            element = self.driver

        while counter != max:

            try:

                value = element.find_element(mode, id).get_property(propName)
                time.sleep(timeAfter)
                return value
            except:
                counter += 1
                time.sleep(1)

        return False

    def getElement(self, mode, id, element=None, timeAfter=0, max=30):

        counter = 0
        if element == None:
            element = self.driver



        while counter != max:

            try:

                childElement = element.find_element(mode, id)
                time.sleep(timeAfter)
                return childElement
            except:

                counter += 1
                time.sleep(1)

        return False

    def switch2Iframe(self, iframeId, element=None, timeAfter=0, max=30):
        counter = 0
        if element == None:
            element = self.driver

        while counter != max:

            try:
                element.switch_to.default_content()

                for item in iframeId:
                    iframe = self.getElement(By.ID, item, timeAfter=1, max=2)
                    element.switch_to.frame(iframe)
                time.sleep(timeAfter)
                return element
            except:
                element.switch_to.default_content()
                counter += 1
                time.sleep(1)

        return False


    def awaitEelentOnIframe(self, iframeId, mode, id, compare, element=None, timeAfter=0, max=30):

        counter = 0
        if element == None:
            element = self.driver

        while counter != max:

            try:
                element.switch_to.default_content()

                element = self.switch2Iframe(iframeId, element=element, timeAfter=1, max=1)
                text = self.getText(mode, id,element=element, timeAfter=1, max=1)

                if text == compare:
                    time.sleep(timeAfter)
                    self.driver.switch_to.default_content()
                    return True
                else:
                    counter +=1
            except:
                counter += 1
                time.sleep(1)

        return False



    def getElements(self, mode, id, element=None, timeAfter=0, max=30):


        counter = 0
        if element == None:
            element = self.driver

        while counter != max:

            try:

                element = element.find_elements(mode, id)
                time.sleep(timeAfter)
                return element
            except:

                counter += 1
                time.sleep(1)

        return False

    def __genDrive(self, path=None):
        try:
            chrome_options = Options()

            # Configurar Chrome para baixar PDF sem abrir
            chrome_options.add_experimental_option("prefs", {
                "download.default_directory": os.path.normpath(self.downloadPath),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "plugins.always_open_pdf_externally": True,  # Evita abertura no visualizador
            })

            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

            chrome_options.add_argument('--kiosk-printing')
            chrome_options.add_argument('--log-level=1')
            chrome_options.add_argument('--safebrowsing-disable-download-protection')

            if path is None:
                self.driver = webdriver.Chrome(options=chrome_options)

            # Habilitar monitoramento de rede
            self.driver.execute_cdp_cmd("Network.enable", {})

            self.pdf_url = None

            def intercept_request(response):
                """ Captura a URL do PDF nas requisições """
                if "pdf" in response.get("response", {}).get("url", "").lower():
                    self.pdf_url = response["response"]["url"]

            # Adiciona listener para capturar a resposta da rede
            self.driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})
            self.driver.execute_script("window.addEventListener('load', () => {console.log('Página carregada')});")

            return self.driver
        except Exception as e:
            print(f"❌ Erro ao inicializar o WebDriver: {e}")
            print(traceback.format_exc())
            return False

    def intercept_request(self, params):
        global pdf_url
        if "pdf" in params["request"]["url"]:  # Filtra requisições que contenham "pdf"
            pdf_url = params["request"]["url"]