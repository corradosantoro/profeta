#
#
#

import sys
sys.path.append ("../lib")

from profeta.clepta.google import *

svc = Hearer(threshold=240)
svc.prepare()
svc.set_language('it')

while True:
    a = svc.sense()
    if a is not None:
        print a

