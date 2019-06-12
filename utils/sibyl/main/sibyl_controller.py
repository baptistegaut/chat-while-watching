# -*- coding: utf-8 -*-
""""
Module for the controller of the Sibyl GUI
"""

from .sibyl_model import SibylModel
from .sibyl_view import SibylView
from .sibyl_view import TextInterface
from .sibyl_client_proxy import SibylClientProxy
import logging
from twisted.internet import reactor
from twisted.internet import stdio
from .sibyl_tcp_client_factory import SibylTcpClientProtocolFactory


moduleLogger = logging.getLogger('sibyl_client.sibyl_controller')


def gotProtocol(p, **kwargs):
    """
    This function is called when the client has established a TCP
    connection with the server.
    """
    moduleLogger.debug("gotProtocol started => connection established!")


class SibylGuiController(object):
    """
    The controller for the chat client.
    """
    def __init__(self, protocolName, usingUdp, serverAddr, serverPort,
                 appInstance):
        """
        :param protocol: The *name* of the protocol class.
        :type protocol: string

        :param appInstance: The instance of the gtk application for the
           Sibyl client.
        :type appInstance: instance of gtk.Application
        """
        self.protocolName = protocolName
        self.appInstance = appInstance

        self.sibylClientProxy = SibylClientProxy(self)
        self.view = SibylView(appInstance, self)
        self.model = SibylModel()
        d = reactor.resolve(serverAddr)
        d.addCallback(self.completeInit, protocolName, usingUdp, serverPort,
                      appInstance)
#         if usingUdp:
#             moduleLogger.debug('using UDP, protocol name: %s',
#                                self.protocolName)
#             self.protocolInstance = self.protocolName(
#                                             self.sibylClientProxy,
#                                             self.serverPort,
#                                             self.serverAddr)
#             self.sibylClientProxy.registerProtcolInstance(
#                                                     self.protocolInstance)
#             reactor.listenUDP(0, self.protocolInstance)
#             self.view.showRequestWindow()
#             return
#         else:
#             moduleLogger.debug('using TCP, protocol name: %s',
#                                self.protocolName)
#             self.serverAddr = serverAddr
#             self.serverPort = serverPort
#             self.protocolFactory = SibylTcpClientProtocolFactory(
#                                                     self.protocolName,
#                                                     self.sibylClientProxy,
#                                                     self)
#             reactor.connectTCP(serverAddr, serverPort, self.protocolFactory)
#             self.view.showSpinningWindow('Connecting ...',
#                     'Trying to connect with the server, please wait')

    def completeInit(self, serverAddr, protocolName, usingUdp, serverPort,
                     appInstance):
        self.serverAddr = serverAddr
        self.serverPort = serverPort
        if usingUdp:
            moduleLogger.debug('using UDP, protocol name: %s',
                               self.protocolName)
            self.protocolInstance = self.protocolName(
                                            self.sibylClientProxy,
                                            self.serverPort,
                                            self.serverAddr)
            self.sibylClientProxy.registerProtcolInstance(
                                                    self.protocolInstance)
            reactor.listenUDP(0, self.protocolInstance)
            self.view.showRequestWindow()
            return
        else:
            moduleLogger.debug('using TCP, protocol name: %s',
                               self.protocolName)
            self.serverAddr = serverAddr
            self.serverPort = serverPort
            self.protocolFactory = SibylTcpClientProtocolFactory(
                                                    self.protocolName,
                                                    self.sibylClientProxy,
                                                    self)
            reactor.connectTCP(serverAddr, serverPort, self.protocolFactory)
            self.view.showSpinningWindow('Connecting ...',
                            'Trying to connect with the server, please wait')

    def connectionFailure(self):
        moduleLogger.critical('Connection with the server failed')
        self.view.showErrorWindow('Connection Failed',
            'Connection with the server failed, make sure the server ' +
            'address and port number are correct and that the server is ' +
            'running.')

    def connectionSuccess(self):
        moduleLogger.debug('connectionSuccess called in the controller')
        self.view.showRequestWindow()

    def sendRequest(self, requestText):
        self.view.showSpinningWindow('Please Wait',
                  'Waiting for the response, please wait.')
        moduleLogger.debug("calling sibylClientProxy.sendRequest")
        self.sibylClientProxy.sendRequest(requestText)

    def responseReceived(self, responseText):
        self.view.showResponseWindow(responseText)

    def sibylErrorUserDone(self):
        reactor.stop()

    def connectionProblem(self, reason):
        moduleLogger.critical('Connection problem. \n ' + reason)
        self.view.showErrorWindow('Connection Problem', str(reason))
        reactor.stop()


class SibylTextInterfaceController(object):
    """
    The controller for the chat client.
    """
    def __init__(self, protocolName, usingUdp, serverAddr, serverPort):
        """
        :param protocol: The *name* of the protocol class.
        :type protocol: string
        """

        self.protocolName = protocolName
        self.serverAddr = serverAddr
        self.serverPort = serverPort
        self.sibylClientProxy = SibylClientProxy(self)
        if usingUdp:
            moduleLogger.debug('using UDP, protocol name: %s',
                               self.protocolName)
            self.protocolInstance = self.protocolName(
                                            self.sibylClientProxy,
                                            self.serverPort,
                                            self.serverAddr)
            self.sibylClientProxy.registerProtcolInstance(
                                                    self.protocolInstance)
            reactor.listenUDP(0, self.protocolInstance)
        else:
            moduleLogger.debug('using TCP, protocol name: %s',
                               self.protocolName)
            self.protocolFactory = SibylTcpClientProtocolFactory(
                                                    self.protocolName,
                                                    self.sibylClientProxy,
                                                    self)
            reactor.connectTCP(serverAddr, serverPort, self.protocolFactory)

        moduleLogger.debug('about to start the text-based user interface')
        self.view = TextInterface(self)
        stdio.StandardIO(self.view)
        #self.view = TextInterface(self)

    def connectionFailure(self):
        moduleLogger.critical('Connection with the server failed, aborting')
        reactor.stop()

    def connectionSuccess(self):
        moduleLogger.debug('connectionSuccess called in the controller')
        pass  # This function is only used by the GUI

    def sendRequest(self, requestText):
        moduleLogger.debug("calling sibylClientProxy.sendRequest")
        self.sibylClientProxy.sendRequest(requestText)

    def responseReceived(self, responseText):
        self.view.responseReceived(responseText)
        self.view.transport.loseConnection()
        moduleLogger.debug('loseConnection called')
        self.sibylClientProxy.protocolInstance.transport.loseConnection()
        #sys.exit()
        #reactor.stop()

    def connectionProblem(self, reason):
        moduleLogger.critical('Connection problem. \n ' + reason)
        self.view.displayErrorMessage('Connection problem.\n' + reason)
        reactor.stop()
