"""
The Client Model Module
=========================
"""

import logging
from c2w.main.user import c2wUserStore
from c2w.main.movie import c2wMovieStore
import sys

sys.dont_write_bytecode = True
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.client_model')


class c2wClientModel(object):
    """
    .. warning:: 
       You cannot use this module to interact with User Interface.
       You can do that only by using the
       :py:class:`~c2w.main.client_proxy.c2wClientProxy`.

    .. note:: 
       This is an *optional* module.  If you want, you can use
       it to store users and/or movies in your *protocol
       implementation*.  If you decide to use this class, you need to
       instantiate it yourself.  For instance, by adding an attribute
       to the Client Protocol class.
    

    This model can be used in the client protocol, it contains a user and
    a movie store.

    """
    def __init__(self):
        #: user list with all the information about a user
        #: this is of type c2wUserStore
        self._userStore = c2wUserStore()
        #: movie list with all the information about a user
        #: this is of type c2wMovieStore
        self._movieStore = c2wMovieStore()

    def addUser(self, userName, userId=None, userChatRoom=''):
        """
        :param userName: The name of the user.
        :type userName: string
        :param userId: The numerical user id (optional, can be None if not
                         needed)
        :type userId: integer
        :param userChatRoom: The name of the corresponding chatroom.
        :type userChatRoom: string or an instance of
               :py:class:`c2w.main.constants.ROOM_IDS`

        Add a new user to the model.
        """
        self._userStore.createAndAddUser(userName, userChatRoom,
                                         None, None, userId)

    def userExists(self, userName):
        """
        :param userName: The name of the user.
        :type userName: string

        Returns `True` if the user exists, `False` otherwise.
        """
        return self._userStore.userExist(userName)

    def getUserByName(self, userName):
        """
        :param userName: The name of the user.
        :type userName: string

        Returns the user, if it exists, `None` otherwise.
        """
        return self._userStore.getUserByName(userName)

    def getUserById(self, uid):
        """
        :param uid: The numerical identifier of the user.

        .. warning::
            The uid must of the same type as the one used when adding the
            user.  Otherwise this function will return `None` even if
            the user does exist.

        Returns the user, if it exists, `None` otherwise.  If the user
        exists, the return value is an instance of
        :py:class:`~c2w.main.user.c2wUser`.
        """
        return self._userStore.getUserById(uid)

    def getUserByAddr(self, address):
        """
         :param address: The numerical identifier of the user.

        .. warning::
            The address must of the same type as the one used when adding the
            user.  Otherwise this function will return `None` even if
            the user does exist.

        Returns the user, if it exists, `None` otherwise.  If the user
        exists, the return value is an instance of
        :py:class:`~c2w.main.user.c2wUser`.
        """
        return self._userStore.getUserByAddress(address)



    def removeUser(self, userName):
        """
        :param userName: The name of the user to be removed.
        :type userName: string

        Remove a single user.
        """
        self._userStore.removeUser(userName)

    def removeAllUsers(self):
        """
        Remove all the users.
        """
        self._userStore.removeAllUsers()

    def updateUserChatroom(self, userName, newUserChatRoom):
        """
        :param userName: The name of the user who has changed room
        :type userName: string
        :param newUserChatRoom: The name of the new room.
        :type newUserChatRoom: string or an instance of
               :py:class:`c2w.main.constants.ROOM_IDS`
        """

        self._userStore.updateUserChatRoom(userName, newUserChatRoom)

    def addMovie(self, movieTitle, movieIpAddress, moviePort, movieId=None, *args):
        """
        :param movieTitle: The title of the movie.
        :type movieTitel: string
        :param movieIpAddress: The dotted decimal notation of the IP address
            where the video flow is received.
        :type movieIpAddress: string
        :param moviePort: The corresponding port number.
        :type moviePort: string or integer
        :param movieId: The numerical identifier of the movie (optional).
        :type movieId: integer or string.

        Add a movie with the corresponding information.
        """

        self._movieStore.createAndAddMovie(movieTitle, movieIpAddress,
                                           moviePort, movieId=movieId)

    def getMovieById(self, movieId):
        """
        :param movieId: The numerical identifier of the user.
        :type movieId: int
        :returns: The corresponding user (instance of
                  :py:class:`~c2w.main.movie.c2wMovie`), ``None`` if
                  there is no user with the given name in the list.

        .. note::
            This function works correctly only if there is at most one
            movie with the given id.  If multiple movies have the same id
            this function will return only one of them.
        """
        return self._movieStore.getMovieById(movieId)

    def getMovieByTitle(self, movieTitle):
        """
        :param movieTitle: The title of the movie.
        :type movieTitel: string

        Returns the corresponding movie, or `None` if it does not exist.
        """
        return self._movieStore.getMovieByTitle(movieTitle)

    def getMovieAddrPort(self, movieTitle):
        """
        :param movieTitle: The title of the movie.
        :type movieTitel: string

        Returns the corresponding IP address and port, or `None` if
        the movie does not exist.
        """
        m = self._movieStore.getMovieByTitle(movieTitle)
        if m is None:
            return m
        else:
            return (m.movieIpAddress, m.moviePort)

    def removeAllMovies(self):
        """
        Remove all the movies.
        """
        self._movieStore.removeAllMovies()

    def getUserList(self):
        """
        Returns the list of all the users.  Each element of the list
        is an instance of :py:class:`~c2w.main.user.c2wUser`.
        """
        return self._userStore.getUserList()

    def getMovieList(self):
        """
        Returns the list of all the movies.  Each element of the list
        is an instance of :py:class:`~c2w.main.movie.c2wMovie`.
        """
        return self._movieStore.getMovieList()
