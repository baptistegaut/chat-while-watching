"""

c2wChatServerProtoclFactory Module
==================================

This module contains the c2wChatServerProtoclFactory, which, as its name
indicates, is the factory for the server protocol.

"""
import logging
from twisted.internet.protocol import Factory
import sys

sys.dont_write_bytecode = True
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.c2w_main.chat_server_protocol_factory')


class c2wChatServerProtocolFactory(Factory):

    def __init__(self, protocolName, serverProxy):
        """
        :param protocolName: The complete protocol class name (including
                the module name).
        :type protocolName: string
        :param serverProxy:  The server proxy instance.
        :type serverProxy: instance of
:py:class:`~c2w.main.server_proxy.c2wServerProxy`
        :param lossPr: The packet loss probability for outgoing packets.
        :type protocolName: float

        The factory for the server protocol.  It contains the user list
        and the movie list.  Each chat server protocolName instance has
        a reference to these two lists.

        It has the following attributes:

        .. attribute:: protocolName

            The complete protocol class name. (This *must* be given
            as one of arguments of the constructor.)

        .. attribute:: server_proxy

            The user list, of type
:py:class:`~c2w.main.server_proxy.c2wServerProxy`.

        .. warning::
            The chat server protocol *must* use the server proxy to get the
            movie list otherwise video streaming will not work.
        """
        #: The name of the protocolName implementation.
        self.protocolName = protocolName
        #: The server proxy.
        self.serverProxy = serverProxy
        #: The loss probability for outgoing packets
        moduleLogger.debug('ChatServerProtocolFactory, protocolName= %s',
                           str(self.protocolName))
        self.lastMovieId = 0

    def buildProtocol(self, addr):
        """
        :param addr: the address of the newly connected client.

        Build the ChatServerProtocolInstance.  Called by the Twisted
        framework when a new connection is established.

        """
        moduleLogger.info("FACTORY_INFO: building a new protocol instance, " +
                          "for user with address %s", addr)
        p = self.protocolName(self.serverProxy, addr.host, addr.port)
        return p
