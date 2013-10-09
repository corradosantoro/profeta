#
# google.py
#

import urllib
import os

from profeta.clepta.services import *
from profeta.clepta.action import *
from profeta.variable import *

class GoogleTextToSpeech(HttpService):

    PLAYER = "mplayer -msglevel all=-1"
    TEMPFILE = "temp.wav"

    def __init__(self, uLanguage):
        HttpService.__init__(self, "http://translate.google.com/translate_tts", 'POST')
        self.__lang = uLanguage

    def set_language(self, lang):
        self.__lang = lang

    def say(self, uUtterance):
        res = self.invoke({"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63"},
                          urllib.urlencode({"q": uUtterance, "textlen": len(uUtterance), "tl": self.__lang}))
        if res.getcode() == 200:
            f = open(GoogleTextToSpeech.TEMPFILE, "wb")
            f.write(res.read())
            f.close()
            os.system(GoogleTextToSpeech.PLAYER + " " + GoogleTextToSpeech.TEMPFILE + " 2>/dev/null")
            os.remove(GoogleTextToSpeech.TEMPFILE)



class say(AsyncAction):

    def create_service(self, lang = 'en'):
        return GoogleTextToSpeech(lang)

    def set_language(self, lang):
        self.get_service().set_language(lang)

    def execute(self):
        utterance = ""
        for i in range(0,self.items()):
            v = self[i]
            if isinstance(v, Variable):
                v = v.get()
            utterance = utterance + v
        self.async_invoke(self.get_service().say, [utterance])