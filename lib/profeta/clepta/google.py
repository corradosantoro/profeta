#
# google.py
#

import pyaudio
import wave
import audioop
from collections import deque
import os
import urllib2
import urllib
import time

from profeta.clepta.services import *
from profeta.clepta.action import *
from profeta.clepta.sensor import *
from profeta.attitude import *
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



class GoogleSpeechToText(HttpService):

    def __init__(self, uLanguage):
        HttpService.__init__(
            self,
            'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=6'%(uLanguage),
            'POST')
        self.__lang = uLanguage

    def set_language(self, lang):
        self.__lang = lang
        self.set_url('https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=6'%(lang))

    def get(self, uFlacData):
        res = self.invoke({"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63",
                           'Content-type': 'audio/x-flac; rate=16000'},
                          uFlacData)
        if res.getcode() == 200:
            e = eval(res.read())
            #print e
            return e['hypotheses']
        else:
            return None


class hear(Belief):
    pass

class Hearer(Sensor):

    FILENAME = 'temp_in'
    FLAC_CONV = 'flac --totally-silent -f ' # We need a WAV to FLAC converter.

    def __init__(self, threshold = 100, lang = 'en-US'):
        Sensor.__init__(self)
        self.__threshold = threshold
        self.__lang = lang

    def start(self):
        self.__stt = GoogleSpeechToText('en-US')
        self.__stt.set_language(self.__lang)
        self.__audio = pyaudio.PyAudio()

        self.__stream = self.__audio.open(format = pyaudio.paInt16,
                                          channels = 1,
                                          rate = 16000,
                                          input = True,
                                          frames_per_buffer = 1024)

        SILENCE_LIMIT = 1 # in seconds

        # limit buffer to the total amount of data for 1 second of audio
        self.__queue = deque(maxlen=SILENCE_LIMIT * 16000 / 1024)
        self.__capture_on = False
        self.__audio_buffer = []

    def sense(self):
        ret_val = None
        data = self.__stream.read(1024) # read one chunk
        a=abs(audioop.max(data, 2))
        #print a
        self.__queue.append (a)

        #check for silence
        silence = filter(lambda x: x > self.__threshold, self.__queue) == []

        if self.__capture_on:
            if silence:
                self.__capture_on = False
                # perform translation
                #print "Stop capturing"
                ret_val = self.__do_stt()
                self.__audio_buffer = []
                self.__queue.clear()
            else:
                self.__audio_buffer.append(data)
        else:
            if not(silence):
                #print "Start capturing..."
                self.__capture_on = True
                self.__audio_buffer.append(data)

        return ret_val

    def __do_stt(self):
        #create WAV
        data = ''.join(self.__audio_buffer)
        wf = wave.open(Hearer.FILENAME + '.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.__audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(data)
        wf.close()

        #Convert to flac
        os.system(Hearer.FLAC_CONV + Hearer.FILENAME + '.wav')
        f = open(Hearer.FILENAME + '.flac','rb')
        flac_cont = f.read()
        f.close()

        os.remove(Hearer.FILENAME + '.wav')
        os.remove(Hearer.FILENAME + '.flac')

        e = self.__stt.get(flac_cont)
        if e == []:
            return None
        else:
            phrase = e[0]['utterance']
            return hear(phrase)


class say(AsyncAction):

    def create_service(self, lang = 'en'):
        return GoogleTextToSpeech(lang)

    def set_language(self, lang):
        self.get_service().set_language(lang)

    def execute(self):
        utterance = ""
        for i in range(0,self.items()):
            utterance = utterance + self[i]
        self.async_invoke(self.get_service().say, [utterance])
