import logging
import sys

sys.dont_write_bytecode = True

try:
    from twisted.internet.protocol import ClientFactory
except:
    raise ImportError("IMPORT_ERROR: Unable to import twisted module")

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.chat_client_protocol_factory')


class c2wChatClientProtocolFactory(ClientFactory):

    def __init__(self, protocolClass, c2wClientProxy):
        """
        :param protocol: The complete protocol class name (including the module
            name).
        :param chatClientProtocolController: A reference to the corresponding
          chatClientProtocolController

        The constructor for the class.
        """
        moduleLogger.debug("c2wChatClientProtocolFactory constructor called" +
                           ' with protocol class: ' + str(protocolClass))
        #: The name of the protocol implementation.
        self.protocolClass = protocolClass
        #: A reference to the corresponding chatClientProtocolController
        self.c2wClientProxy = c2wClientProxy

    def buildProtocol(self, addr):
        """
        :param addr: The remote address.

        Builds a new instance of the client protocol whenever it is called.
        """
        moduleLogger.debug('Building a new protocol instance')
        p = self.protocolClass(self.c2wClientProxy, addr.host, addr.port)
        moduleLogger.debug('Registering the new protocol instance with the' +
                           ' proxy')
        self.c2wClientProxy.registerChatClientProtocolInstance(p)

        return p
