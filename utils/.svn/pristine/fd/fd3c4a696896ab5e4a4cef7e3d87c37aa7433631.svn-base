# -*- coding: utf-8 -*-
from twisted.internet.protocol import Factory
import logging

moduleLogger = logging.getLogger('sibyl_client.sibyl_tcp_client_factory')


class SibylTcpSeverProtocolFactory(Factory):

    def __init__(self, protocolClass, sibylBrain):
        """
        :param protocol: The complete protocol class name (including the module
            name).

        The constructor for the class.
        """
        moduleLogger.debug("SibylTcpSeverProtocolFactory constructor called" +
                           ' with protocol class: ' + str(protocolClass))
        #: The name of the protocol implementation.
        self.protocolClass = protocolClass
        self.sibylBrain = sibylBrain

    def buildProtocol(self, addr):
        """
        :param addr: The remote address.

        Builds a new instance of the server protocol whenever it is called.
        """
        moduleLogger.debug('Building a new protocol instance (TCP Server)')
        p = self.protocolClass(self.sibylBrain)
        return p
