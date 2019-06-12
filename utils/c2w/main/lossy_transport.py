from zope.interface import implementer
from twisted.internet import interfaces
import random
import logging
import sys

sys.dont_write_bytecode = True
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.lossy_transport')


@implementer(interfaces.IUDPTransport)
class LossyTransport:
    # FIXME***** remove this comment, if it works with Python 3
    # implements(interfaces.IUDPTransport)

    def __init__(self, transport, lossPr=0.2):
        moduleLogger.debug('Initializing lossy transport with loss' +
                           ' probability=%s', lossPr)
        self.transport = transport
        self.lossPr = lossPr

    def getHandle(self):
        return self.transport.getHandle()

    def startListening(self):
        self.transport.startListening()

    def createSocket(self):
        return self.transport.startListening()

    def _bindSocket(self):
        self.transport._bindSocket()

    def _connectToProtocol(self):
        self.transport.connectToProtocol()

    def cbRead(self):
        self.transport.cbRead()

    def handleRead(self, rc, b, evt):
        self.transport.handleRead(rc, b, evt)

    def doRead(self):
        self.transport.doRead()

    def write(self, datagram, addr=None):
        i = random.random()
        if i >= self.lossPr:
            return self.transport.write(datagram, addr)
        else:
            moduleLogger.debug('++++ lost a packet ++++++')

    def writeSequence(self, seq, addr):
        self.transport.writeSequence(seq, addr)

    def connect(self, host, port):
        self.transport.connect(host, port)

    def _loseConnection(self):
        self.transport._loseConnection()

    def stopListening(self):
        return self.transport.stopListening()

    def loseConnection(self):
        self.transport.loseConnection()

    def connectionLost(self, reason=None):
        self.transport.connectionLost(reason)

    def setLogStr(self):
        self.transport.setLogStr()

    def logPrefix(self):
        return self.transport.logPrefix()

    def getHost(self):
        return self.transport.getHost()
