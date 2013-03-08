import sys, getopt
import httplib
import socket

# This class performs the client side of anonymization.
# feel free to copy this into the Django code.
class AnonymizerClient:
    
    def __init__(self, anonymizer_port):
        self.anonymizer_port = anonymizer_port
        try:
            self.conn = httplib.HTTPConnection('127.0.0.1', self.anonymizer_port)
            self.conn.connect()
        except (httplib.HTTPException, socket.error):
            print 'Port number ' + str(anonymizer_port) + ' does not have the Anonymizer Service running on it'
            sys.exit(2)
    
    def anonymize(self, userid):
        
        self.conn.request('GET', '/anonymize?userid='+str(userid))
        rsp = self.conn.getresponse()
        data_received = rsp.read()
        return data_received

    def close(self):        
        self.conn.close()

