# -*- coding: utf-8 -*-
import logging
from twisted.internet.protocol import ClientFactory

moduleLogger = logging.getLogger('sibyl_client.sibyl_tcp_client_factory')


class SibylTcpClientProtocolFactory(ClientFactory):

    def __init__(self, protocolClass, sibylClientProxy, sibylController):
        """
        :param protocol: The complete protocol class name (including the module
            name).
        :param sibylClientProxy: A reference to the corresponding
          SibylClientProxy
        :param sibylController: A reference to the corresponding
          sibylController so that the methods clientConnectionLost and
          clientConnectionFailed can signal the corresponding error condition
          to the controller.

        The constructor for the class.
        """
        moduleLogger.debug("SibylTcpClientProtocolFactory constructor called" +
                           ' with protocol class: ' + str(protocolClass))
        #: The name of the protocol implementation.
        self.protocolClass = protocolClass
        #: A reference to the corresponding chatClientProtocolController
        self.sibylClientProxy = sibylClientProxy
        self.sibylController = sibylController

    def buildProtocol(self, addr):
        """
        :param addr: The remote address.

        Builds a new instance of the client protocol whenever it is called.
        """
        moduleLogger.debug('Building a new protocol instance (TCP client)')
        p = self.protocolClass(self.sibylClientProxy)
        moduleLogger.debug('Registering the new protocol instance with the' +
                           ' proxy')
        self.sibylClientProxy.registerProtcolInstance(p)

        return p

    def clientConnectionLost(self, connector, reason):
        moduleLogger.debug('Connection lost, reason: %s', reason)
        #self.sibylController.connectionProblem(reason.getErrorMessage())

    def clientConnectionFailed(self, connector, reason):
        moduleLogger.debug('Connection failed, reason: %s', reason)
        self.sibylController.connectionProblem(reason.getErrorMessage())
