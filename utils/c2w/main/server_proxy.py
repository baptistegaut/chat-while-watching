"""
ServerProxy Module
==================================

This module contains the ServerProxy, the proxy between the server
and the server model.

"""

import logging
import sys

sys.dont_write_bytecode = True
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.server_proxy')


class c2wServerProxy(object):
    def __init__(self, serverModel):
        self.serverModel = serverModel
        moduleLogger.debug('done building the server proxy')

    def initMovieStore(self, streamVideoFlag, noVideoFlag):
        """
        Initializes the movie list.
        """
        self.serverModel.initMovieStore(streamVideoFlag, noVideoFlag)

    def addUser(self, userName, userChatRoom,  userChatInstance=None,
                 userAddress=None):
        """
        :param userName: The name of the user.
        :type userName: string
        :param userChatRoom: The name of the corresponding chatroom.
        :type userChatRoom: string or an instance of
               :py:class:`c2w.main.constants.ROOM_IDS`
        :param userChatInstance: A reference to the corresponding instance of
                     c2wChatServerProtocol (optional, useful in the case
                     of TCP protocols)
        :type userChatInstance: instance of c2wChatServerProtocol
        :param userAddress: The address of the corresponding client (optional,
                useful in the case of UDP protocols)

        Add a new user to the model.  Returns the numerical user
        identifier of the new user (as an integer).

        .. warning::
            You MUST use the user ID returned by this method for the
            automated tests to work.
        """

        assert(isinstance(userName, str))
        userId = self.serverModel.addUser(userName, userChatRoom,
                                          userChatInstance, userAddress)
        return userId

    def userExists(self, userName):
        """
        :param userName: The name of the user.
        :type userName: string

        Returns `True` if the user exists, `False` otherwise.
        """

        assert(isinstance(userName, str))
        return self.serverModel.userExists(userName)

    def getUserByName(self, userName):
        """
        :param userName: The name of the user.
        :type userName: string

        Returns the user, if it exists, `False` otherwise.  If the user
        exists, the return value is an instance of
        :py:class:`~c2w.main.user.c2wUser`.
        """

        assert(isinstance(userName, str))
        return self.serverModel.getUserByName(userName)

    def getUserById(self, uid):
        """
        :param uid: The numerical identifier of the user.

        .. warning::
            The uid must of the same type as the one used when adding the
            user.  Otherwise this function will return `False` even if
            the user does exist.

        Returns the user, if it exists, `False` otherwise.  If the user
        exists, the return value is an instance of
        :py:class:`~c2w.main.user.c2wUser`.
        """
        return self.serverModel.getUserById(uid)

    def getUserByAddress(self, address):
        """
         :param address: The numerical identifier of the user.

        .. warning::
            The address must of the same type as the one used when adding the
            user.  Otherwise this function will return `False` even if
            the user does exist.

        Returns the user, if it exists, `False` otherwise.  If the user
        exists, the return value is an instance of
        :py:class:`~c2w.main.user.c2wUser`.
        """
        return self.serverModel.getUserByAddress(address)

    def removeUser(self, userName):
        """
        :param userName: The name of the user to be removed.
        :type userName: string

        Remove a single user.
        """

        assert(isinstance(userName, str))
        self.serverModel.removeUser(userName)

    def removeAllUsers(self):
        """
        Remove all the users.
        """
        self.serverModel.removeAllUsers()

    def updateUserChatroom(self, userName, newUserChatRoom):
        """
        :param userName: The name of the user who has changed room
        :type userName: string
        :param newUserChatRoom: The name of the new room.
        :type newUserChatRoom: string or an instance of
               :py:class:`c2w.main.constants.ROOM_IDS`
        """

        assert(isinstance(userName, str))
        self.serverModel.updateUserChatroom(userName, newUserChatRoom)

    def addMovie(self, movieTitle, movieIpAddress, moviePort,
                 movieFilePath, movieId=None):
        """
        :param movieTitle: The title of the movie.
        :type movieTitel: string
        :param movieIpAddress: The dotted decimal notation of the IP address
            where the video flow is received.
        :type movieIpAddress: string
        :param moviePort: The corresponding port number.
        :type moviePort: string or integer

        Add a movie with the corresponding information.
        """

        assert(isinstance(movieTitle, str))
        self.serverModel.addMovie(movieTitle, movieIpAddress, moviePort,
                                  movieFilePath, movieId)

    def getMovieByTitle(self, movieTitle):
        """
        :param movieTitle: The title of the movie.
        :type movieTitel: string

        Returns the corresponding movie, or `None` if it does not exist.
        """

        assert(isinstance(movieTitle, str))
        return self.serverModel.getMovieByTitle(movieTitle)

    def getMovieById(self, movieId):
        """
        :param movieId: The numerical identifier of the movie.
        :type movieId: int
        :returns: The corresponding movie (instance of
                  :py:class:`~c2w.main.movie.c2wMovie`), ``None`` if
                  there is no movie with the given name in the list.

        .. warning::
            This function works correctly only if the `movieId` is
            an integer and *not* a string.

        .. note::
            This function works correctly only if there is at most one
            movie with the given id.  If multiple movies have the same id
            this function will return only one of them.
        """
        return self.serverModel.getMovieById(movieId)

    def getMovieAddrPort(self, movieTitle):
        """
        :param movieTitle: The title of the movie.
        :type movieTitel: string

        Returns the corresponding IP address and port, or `None` if
        the movie does not exist.
        """

        assert(isinstance(movieTitle, str))
        return self.serverModel.getMovieAddrPort(movieTitle)

    def getMovieAddrPortById(self, movieId):
        """
        :param movieId: The numerical identifier of the user.
        :type movieId: int

        Returns the corresponding IP address and port (as a pair), or
        `None` if the movie does not exist.
        """
        return self.serverModel.getMovieAddrPortById(movieId)

    def removeAllMovies(self):
        """
        Remove all the movies.
        """
        self.serverModel.removeAllMovies()

    def getUserList(self):
        """
        Returns the list of all the users.  Each element of the list
        is an instance of :py:class:`~c2w.main.user.c2wUser`.
        """
        return self.serverModel.getUserList()

    def getMovieList(self):
        """
        Returns the list of all the movies.  Each element of the list
        is an instance of :py:class:`~c2w.main.movie.c2wMovie`.
        """
        return self.serverModel.getMovieList()

    def startStreamingMovie(self, movieTitle):
        """
        Start streaming the corresponding movie.
        """

        assert(isinstance(movieTitle, str))
        self.serverModel.startStreamingMovie(movieTitle)

    def stopStreamingMovie(self, movieTitle):
        """
        Stop streaming the corresponding movie.
        """

        assert(isinstance(movieTitle, str))
        self.serverModel.stopStreamingMovie(movieTitle)
