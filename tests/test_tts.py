#
#
#

import sys
sys.path.append ("../lib")

from profeta.clepta.google import *

svc = GoogleTextToSpeech('it')

while True:
    s = raw_input("Enter string> ")
    svc.say(s)

