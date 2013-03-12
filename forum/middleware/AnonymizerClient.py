import sys, getopt
import httplib
import socket
import logging

# This class performs the client side of anonymization.
# feel free to copy this into the Django code.
class AnonymizerClient:
    
    def __init__(self, anonymizer_port):
        self.anonymizer_port = anonymizer_port
        try:
            self.conn = httplib.HTTPConnection('127.0.0.1', self.anonymizer_port)
            self.conn.connect()
        except (httplib.HTTPException, socket.error):
            logging.error("Port number %s does not have the Anonymizer Service running on it.\n REMINDER: If you restarted the server, make sure you run AnonymizerService.py using the Anonymizer user." , str(anonymizer_port) ) 
            sys.exit(2)
    
    def anonymize(self, userid):
        
        self.conn.request('GET', '/anonymize?userid='+str(userid))
        rsp = self.conn.getresponse()
        data_received = rsp.read()
        return data_received

    def close(self):        
        self.conn.close()

