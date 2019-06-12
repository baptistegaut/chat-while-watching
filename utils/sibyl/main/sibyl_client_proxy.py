# -*- coding: utf-8 -*-
import sys
import logging

try:
    from twisted.internet.endpoints import TCP4ClientEndpoint
    from twisted.internet import reactor
except ImportError:
    print("IMPORT_ERROR: Unable to import twisted module")
    sys.exit(1)

moduleLogger = logging.getLogger('sibyl_client.sibyl_client_proxy')


class SibylClientProxy(object):
    """
    This class is the interface between the SibylClientProtocol and
    the SibylController (which is the controller of the client).

    .. warning::
        Your protocol implementation can interact with the user interface
        only by calling the methods of this class.

    The interface offered to the protocol implementation is extremely
    simple, there is only one method that the protocol can call
    (:py:meth:`~sibyl.main.sybil_client_proxy.SibylClientProxy.responseReceived`).

    The class has other methods that you must not call.  They are called
    by the proxy.

    .. note::
       As mentioned above, all the instances of a protocol class have an
       attribute (`.clientProxy`).  You must use this attribute to access
       the proxy.

    .. warning::
       Do not instantiate this class in your protocol.
    """
    def __init__(self, sibylController):
        """
        :param sibylController: The corresponding SibylController instance.
        """
        moduleLogger.debug("SibylClientProxy constructor started")
        self.sibylController = sibylController
        self.protocolInstance = None

    def registerProtcolInstance(self, protocolInstance):
        self.protocolInstance = protocolInstance

    def sendRequest(self, requestText):
        """
        :param requestText: The text of the request (question for the Sibyl).

        Called **by the sibylController** when the user clicks on
        the "send reqeust" button. This function instantiates the connection
        end-point, with the corresponding ChatClientProtocolFactory.
        """
        moduleLogger.debug("sendRequest started")
        self.protocolInstance.sendRequest(requestText)

    def responseReceived(self, responseText):
        """Display the Response in the User Interface

        Tells the controller to display the response in the Graphical User
        Interface

        
        
        """
        self.sibylController.responseReceived(responseText)

    def connectionSuccess(self):
        """
        Called by the TCP version of the protocol when the connection
        with the server is established.  (Needed by the GUI.)
        """
        self.sibylController.connectionSuccess()
