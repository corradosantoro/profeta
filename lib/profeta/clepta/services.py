#
# services.py
#

import urllib2

class Service:

    def __init__(self):
        pass

    def invoke(self):
        raise "To be overridden"



class HttpService(Service):

    def __init__(self, uURL, uMethod = 'GET'):
        Service.__init__(self)
        self.__url = uURL
        self.__method = uMethod

    def get_url(self):
        return self.__url

    def set_url(self, uURL):
        self.__url = uURL

    def get_method(self):
        return self.__method

    def set_method(self, uMethod):
        self.__method = uMethod

    def invoke(self, hdr, d = None):
        if (d is None)and(self.__method == 'POST'):
            raise 'Cannot handle POST without data'
        if (d is not None)and(self.__method == 'GET'):
            raise 'Data must be handled by POST instead of GET'

        req = urllib2.Request(self.__url, data=d, headers=hdr)
        p = urllib2.urlopen(req)

        return p

