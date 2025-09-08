import json
import traceback
import os

from filelock import FileLock

DATA_PATH = ".\database"
os.makedirs(DATA_PATH, exist_ok=True)

def chats(data=False):

    return __dataControl(DATA_PATH + "\\chats.json", data)


def config(data=False):

    return __dataControl(DATA_PATH + "\\config.json", data)

def chat(data=False):

    return __dataControl(DATA_PATH + "\\chat.json", data)



def __dataControl(path, data=False):

    lockFile = path + ".lock"
    lock = FileLock(lockFile)
    res = None

    try:

        with lock:
            if data != False:

                with open(path, "w", encoding="utf-8") as file:

                    s_data = json.dumps(data)
                    file.write(s_data)
                    return res

            else:

                with open(path, "r", encoding="utf-8") as file:

                    res = json.loads(file.read())

                    return res
    except:
        return None