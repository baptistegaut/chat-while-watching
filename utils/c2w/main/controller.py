import logging
import os
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import defer
from c2w.main.client_gui_model import c2wClientGuiModel
from c2w.main.view import c2wView
from c2w.main.client_proxy import c2wClientProxy
from c2w.main.constants import ROOM_IDS
from c2w.main.chat_client_protocol_factory import c2wChatClientProtocolFactory
import sys

sys.dont_write_bytecode = True

class CONTR_STATES(object):
    class MAIN_ROOM(object):
        pass

    class CONNECTING(object):
        pass

    class MOVIE_ROOM(object):
        pass

    class DISCONNECTED(object):
        pass

    class TO_MOVIE_ROOM_REQUEST_PENDING(object):
        pass

    class TO_MAIN_ROOM_REQUEST_PENDING(object):
        pass

    class TO_OUT_OF_THE_SYSTEM_ROOM_REQUEST_PENDING(object):
        pass

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.controller')


class c2wController(object):
    """
    The controller for the chat client.
    """
    def __init__(self, protocolName, appInstance, udpFlag, lossPr):
        """
        :param protocolName: The *name* of the protocolName class.
        :type protocolName: string

        :param appInstance: The instance of the gtk application for the
           c2w client.
        :type appInstance: instance of gtk.Application
        :param lossPr: The loss probability for outgoing packets (used only
                with the UDP version of the protocol).
        :type lossPr: float
        """
        self.protocolName = protocolName
        self.appInstance = appInstance
        self.udpFlag = udpFlag
        self.lossPr = lossPr
        self.clientUdpPort = None
        self.setInitialValues()
        self.view.showLoginWindow()

    def setInitialValues(self):
        """
        set (or reset) all the member values to their initial values .
        """
        self.model = c2wClientGuiModel()
        self.view = c2wView(self.appInstance, self)
        self._state = CONTR_STATES.DISCONNECTED
        self.room = ROOM_IDS.OUT_OF_THE_SYSTEM_ROOM

        self.clientProxy = None
        self.thisUserName = ''
        self.thisMovieRoom = ''
        self.serverName = ''
        self.serverPort = ''
        self._initCompleteONECalled = False

    def gotProtocol(self, p, **kwargs):
        """
        This function is called when the client has established a TCP
        connection with the server.
        """
        moduleLogger.debug("gotProtocol called")
        self.clientProxy.sendLoginRequestOIE(self.thisUserName)

    def loginRequest(self, serverName, serverPort, userName):
        """
        Called by the view when the user clicks on the login button.
        This function instantiates the client proxy and then calls the
        :py:meth:`~c2w.main.client_proxy.clientProxy.loginRequest` method.
        """
        self.thisUserName = userName
        self.serverName = serverName
        self.serverPort = serverPort
        self.view.showSpinningWindow('Connecting',
                  'Connecting with the server, please wait.')
        self.clientProxy = c2wClientProxy(self)
        moduleLogger.debug("instantiated the clientProxy")

        self._state = CONTR_STATES.CONNECTING

        if self.udpFlag:
            moduleLogger.debug("self.protocolName= " + str(self.protocolName))
            self.udpProtocolInstance = self.protocolName(self.serverName,
                                                         self.serverPort,
                                                         self.clientProxy,
                                                         self.lossPr)
            self.clientUdpPort = reactor.listenUDP(0, self.udpProtocolInstance)
            moduleLogger.debug("reactor.listenUDP done")
            self.clientProxy.registerChatClientProtocolInstance(
                                                      self.udpProtocolInstance)
            moduleLogger.debug("calling clientProxy.loginRequest")
            self.clientProxy.sendLoginRequestOIE(userName)
        else:
            self.point = TCP4ClientEndpoint(reactor, self.serverName,
                                             int(serverPort))
            moduleLogger.debug("loginRequest about to connect with TCP")
            self.d = self.point.connect(
                    c2wChatClientProtocolFactory(self.protocolName,
                                              self.clientProxy))
            self.d.addCallback(self.gotProtocol)
            self.d.addErrback(self.handleServerConnectionError)

    def handleServerConnectionError(self, err):
        """
        Called by the errback mechanism when it is not possible
        to open a connection with the server
        """
        moduleLogger.error("Error connecting to the server")
        moduleLogger.error('error: %s', err)
        self.view.showConnectionErrorWindow()

    def connectionErrorUserDone(self):
        """
        Called by the view when the users has clicked on the OK
        button of the connection error window.
        """
        self._state = CONTR_STATES.DISCONNECTED
        self.view.showLoginWindow()

    def initCompleteONE(self, userList, movieList):
        """
        Called by the clientProxy when the client has correctly
        received the movie list and user list.
        """
        if self._initCompleteONECalled == True:
            s = 'initCompleteONE called twice, this is not allowed.  It must'
            s += 'be called only once'
            moduleLogger.critical(s)
            raise RuntimeError(s)
        # First add the movies to the movie list in the model.
        for m in movieList:
            self.model.addMovie(*m)
        # The add the users to the user list.
        for u in userList:
            self.model.addUser(u[0], u[1])
        moduleLogger.info('Movie and User list created in the model')
        self.view.showMainRoomWindow()
        self._state = CONTR_STATES.MAIN_ROOM
        self.room = ROOM_IDS.MAIN_ROOM
        self._initCompleteONECalled = True

    def sendChatMessageOIE(self, message):
        """
        Called by the view when the user has a message to send.
        """
        self.clientProxy.sendChatMessageOIE(message)

    def chatMessageReceivedONE(self, remoteUserName, chatMessage):
        """
        Called by :py:meth:`c2w.main.client_proxy.\
c2wClientProxy.chatMessageReceivedONE`
        when this client has received a message.
        """
        if self._state == CONTR_STATES.MAIN_ROOM:
            self.view.chatReceivedMainWindow(remoteUserName, chatMessage)
        elif self._state == CONTR_STATES.MOVIE_ROOM:
            self.view.chatReceivedMovieWindow(remoteUserName, chatMessage)

    def userUpdateReceivedONE(self, remoteUserName, newRoom):
        """
        Called by :py:meth:`c2w.main.client_proxy.\
c2wClientProxy.userUpdateReceivedONE`
        when it has received a user status update message.
        """
        if self.model.userExists(remoteUserName):
#             oldRoom = self.model.getUserByName(
#                                             remoteUserName).chatRoom
            moduleLogger.debug("VIEW_INFO: updateUserStatus,"\
                    " updating user status, user: %s, room: %s",
                    remoteUserName, newRoom)
            if newRoom == ROOM_IDS.OUT_OF_THE_SYSTEM_ROOM:
                self.model.removeUser(remoteUserName)
            else:
                self.model.updateUserChatroom(remoteUserName, newRoom)
        else:
            moduleLogger.debug("VIEW_INFO: updateUserStatus,"\
                    " adding new user: %s, room: %s", remoteUserName, newRoom)
            self.model.addUser(remoteUserName, newRoom)

    def setUserListONE(self, userList):
        """
        Called the c2wClientProxy to re-set the user list.  We have to reset
        the liststore corresponding to the room we're in.
        """
        self.model.removeAllUsers()
        for u in userList:
            self.model.addUser(u[0], u[1])
        moduleLogger.info('setUserListONE, done resetting the user list.')

    def sendLeaveSystemRequestOIE(self):
        """
        Called by the c2wView when the user clicks on the leave button
        in the main room.
        """
        if self._state != CONTR_STATES.MAIN_ROOM:
            s = 'Controller Internal error: sendJoinRoomRequestOIE '
            s += 'called  with roomName=ROOM_IDS.OUT_OF_THE_SYSTEM_ROOM '
            s += 'when the client is not in the main room'
            moduleLogger.critical(s)
            raise RuntimeError(s)
        else:
            self._state = \
                      CONTR_STATES.TO_OUT_OF_THE_SYSTEM_ROOM_REQUEST_PENDING
            self.view.showSpinningWindow(
                     'Waiting for the server to respond',
                     'Request to disconnect sent to the server, ' +
                     'waiting for the response.')
            self.clientProxy.sendLeaveSystemRequestOIE()

    def leaveSystemOKONE(self):
        if self._state == \
                    CONTR_STATES.TO_OUT_OF_THE_SYSTEM_ROOM_REQUEST_PENDING:
            self._state = CONTR_STATES.DISCONNECTED
            if self.udpFlag:
                # For some reason if we're using UDP we cannot restart the
                # application.  If we try doing that, we get an
                # assert self.transport == None error
                # on top of that, if just raise SystemExit we get a
                # weird error message, that's why we use os._exit() ...
                os._exit(1)
            self.view.currentWindow.hide()
            self.setInitialValues()
            self.view.showLoginWindow()
        else:
            s = 'Controller Internal error: leaveSystemOKONE '
            s += 'called  when the state is not '
            s += 'CONTR_STATES.TO_OUT_OF_THE_SYSTEM_ROOM_REQUEST_PENDING.'
            s += 'This is not possible.'
            moduleLogger.critical(s)
            raise RuntimeError(s)

    def sendJoinRoomRequestOIE(self, roomName):
        """
        Called by the c2wView when the user clicks on the watch
        or leave button.
        """
        if roomName == ROOM_IDS.MAIN_ROOM:
            if self._state != CONTR_STATES.MOVIE_ROOM:
                s = 'Controller Internal error: sendJoinRoomRequestOIE called '
                s += 'with roomName= ROOM_IDS.MAIN_ROOM when the client is '
                s += 'not in a movie room'
                moduleLogger.critical(s)
                raise RuntimeError(s)
            else:
                self._state = CONTR_STATES.TO_MAIN_ROOM_REQUEST_PENDING
                self.view.showSpinningWindow(
                     'Waiting for the server to respond',
                     'Request to change the room sent to the server, ' +
                     'waiting for the response.')
                self.thisMovieRoom = ''
                self.room = ROOM_IDS.MAIN_ROOM
                self.view.showSpinningWindow(
                     'Waiting for the server to respond',
                     'Request to change the room sent to the server, ' +
                     'waiting for the response.')
                self.clientProxy.sendJoinRoomRequestOIE(roomName)
        else:
            # i.e., the user is in the main room and is asking to join a
            # movie room
            if self._state != CONTR_STATES.MAIN_ROOM:
                s = 'Controller Internal error: sendJoinRoomRequestOIE called '
                s += 'with roomName="{0}", when the client '.format(roomName)
                s += 'when the client is not in the main room.'
                moduleLogger.critical(s)
                raise RuntimeError(s)
            m = self.model.getMovieByTitle(roomName)
            if (m is None):
                s = 'VIEW_FATAL_ERROR: trying to join a non-existing movie '
                s += ' title={0}'.format(roomName)
                moduleLogger.critical(s)
                raise RuntimeError(s)
            self.thisMovieRoom = roomName
            self.room = roomName
            self._state = CONTR_STATES.TO_MOVIE_ROOM_REQUEST_PENDING
            self.view.showSpinningWindow('Waiting for the server to respond',
                     'Request to change the room sent to the server, ' +
                     'waiting for the response.')
            self.clientProxy.sendJoinRoomRequestOIE(self.thisMovieRoom)
        self.model.updateLocalUserRoom(roomName)
        self.model.updateUserChatroom(self.thisUserName,
                                         roomName)

    def joinRoomOKONE(self):
        """
        Called by :py:meth:`c2w.main.client_proxy.\
c2wClientProxy.joinRoomOKONE`
        when it receives the OK message for a join room request.

        Depending on the value of self._state, the controller shows
        the appropriate window.
        """
        if self._state == CONTR_STATES.TO_MOVIE_ROOM_REQUEST_PENDING:
            self._state = CONTR_STATES.MOVIE_ROOM
            self.view.showMovieRoomWindow()
        elif self._state == CONTR_STATES.TO_MAIN_ROOM_REQUEST_PENDING:
            self._state = CONTR_STATES.MAIN_ROOM
            self.view.showMainRoomWindow()
        else:
            s = 'joinRoomOKONE called when self._state={0}'.format(self._state)
            s += ' This is not supposed to happen.'
            moduleLogger.critical(s)
            raise RuntimeError(s)
        moduleLogger.debug("VIEW: done with joinMovieOK")

    def setThisUserName(self, userName):
        """
        Set the value of thisUserName
        """
        self.thisUserName = userName

    def applicationQuit(self):
        """
        Called by the protocolName when the application should be closed,
        for example because of an unrecoverable error.
        """
        #raise SystemExit
        #sys.exit()
        from twisted.internet import reactor
        reactor.stop()

    def connectionRejectedONE(self, msg):
        """
        Called by the protocolName when the server rejects the login request.
        """
        self.view.showConnectionRejectedWindow(msg)

    def connectionRejectedUserDone(self):
        """
        Called by the view when the users has clicked on the OK
        button of the connection rejected window
        """
        # Apparently we need to make sure we tear down all the sockets
        # otherwise we get an error if we try to connect again
        # The code below has been copied and pasted from a TCP example
        # at: http://blackjml.livejournal.com/23029.html
        # the title of the page is "How to Disconnect in Twisted, Really"
        if self.udpFlag:
            d = defer.maybeDeferred(self.clientUdpPort.stopListening)
            defer.gatherResults([d])
            del self.udpProtocolInstance
            del self.clientUdpPort
            # this is not working, let's just quite the application :(
            raise SystemExit
        self._state = CONTR_STATES.DISCONNECTED
        self.view.showLoginWindow()

    def getMovieAddrPort(self, movieTitle):
        """
        Called by the view when building a movie room window to get
        the IP address and port number of the corresponding video flow.
        """
        return self.model.getMovieAddrPort(movieTitle)

    def updateMovieAddressPort(self, movieTitle, movieIpAddress, moviePort):
        """
        :param movieTitle: The title of the movie.
        :type movieTitel: string
        :param movieIpAddress: The dotted decimal notation of the IP address
            where the video flow is received.
        :type movieIpAddress: string
        :param moviePort: The corresponding port number.
        :type moviePort: string or integer

        Updates the IP address and the port number associated with the
        movie.

        """

        self.model.updateMovieAddressPort(movieTitle, movieIpAddress,
                                               moviePort)

    def getMainRoomUserListStore(self):
        """
        Called by the view to get the main room user list store, which
        is in the model.
        """
        return self.model.getMainRoomUserListStore()

    def getMovieRoomUserListStore(self):
        """
        Called by the view to get the movie room user list store, which
        is in the model.
        """
        return self.model.getMovieRoomUserListStore()

    def getMainRoomMovieListStore(self):
        """
        Called by the view to get the main room movie list store, which
        is in the model.
        """
        return self.model.getMainRoomMovieListStore()
