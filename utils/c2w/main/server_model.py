"""
The c2wServerModel Module
=========================
"""

import logging
import os
from c2w.main.user import c2wUserStore
from c2w.main.movie import c2wMovieStore
from c2w.main.gst_pipeline import c2wGstServerPipeline
import sys

sys.dont_write_bytecode = True
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.server_model')


class c2wServerModel(object):
    """
    The model for the server, containing the user store and the movie store.

    .. warning::
        Only the :py:class:`~c2w.main.server_proxy.c2wServerProxy` class
        is supposed to use this class and its methods.
        Do not use it in the protocol!
    """
    def __init__(self):
        #: user list with all the information about a user
        #: this is of type c2wUserStore
        self._userStore = c2wUserStore()
        #: movie list with all the information about a user
        #: this is of type c2wMovieStore
        self._movieStore = c2wMovieStore()
        #: whether to enable streaming for the movies or not
        #: the initMovieStore method sets this value properly
        self._noVideoFlag = True
        #: counter used to assign and ID to each new movie
        self._lastMovieId = 2
        #: counter used to assign and ID to each new user
        self._lastUserId = 1

    def initMovieStore(self, streamVideoFlag, noVideoFlag):
        """
        Builds the movie list base on the configuration file (if it
        exists) or using standard movies.
        """

        self._noVideoFlag = noVideoFlag
        if streamVideoFlag == True:
            multicast = True
        else:
            multicast = False
            dstIp = '127.0.0.1'
        if (os.path.isfile(os.path.join(os.path.dirname(
                            os.path.realpath(__file__)), "c2w_movie_config"))):
            # The configuration file exists, read it
            myFile = open(os.path.join(os.path.dirname(
                            os.path.realpath(__file__)), "c2w_movie_config"))
            moduleLogger.info("found movie configuration file, reading it")
            for line in myFile:
                fields = line.split(',')
                if len(fields) != 4:
                    moduleLogger.error("Invalid line in the" +
                              " configuration file: " + line)
                else:
                    movieName = fields[0].strip()
                    movieIpAddress = fields[1].strip()
                    moviePort = fields[2].strip()
                    moviePath = fields[3].rstrip('\n')
                    moduleLogger.info('MAIN_INFO: Adding movie: title=%s,' +
                                  ' address=%s, port=%s, path=%s', movieName,
                                  movieIpAddress, moviePort, moviePath)
                    if multicast == False:
                        movieIpAddress = dstIp
                    self.addMovie(movieName, movieIpAddress, moviePort,
                                         moviePath)
        else:
            if multicast == False:
                movieIpAddress = dstIp
            else:
                movieIpAddress = '224.1.1.1'
            self.addMovie("Big Buck Bunny", movieIpAddress, 1234,
                        "../Movies/Big_Buck_Bunny_small.ogv")
            self.addMovie("Sintel - Trailer", movieIpAddress, 1285,
                       "../Movies/sintel_trailer-480p.ogv")

    def addUser(self, userName, userChatRoom, userChatInstance=None,
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

        Add a new user to the model. Returns the numerical user
        identifier of the new user (as an integer).
        """
        self._userStore.createAndAddUser(userName, userChatRoom,
                                         userChatInstance, userAddress,
                                         self._lastUserId)
        self._lastUserId += 1
        return self._lastUserId - 1

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

        Returns the user, if it exists, `False` otherwise.  If the user
        exists, the return value is an instance of
        :py:class:`~c2w.main.user.c2wUser`.
        """
        return self._userStore.getUserByName(userName)

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
        return self._userStore.getUserById(uid)

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
        :param string movieFilePath: The movieFilePath of the corresponding
                video file (used only in the server).


        Add a movie with the corresponding information.
        """

        currentFileDirectory = os.path.dirname(os.path.realpath(__file__))
        allparts = []
        path = movieFilePath.strip()
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path:  # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        p = currentFileDirectory
        for part in allparts:
            if part == '.':
                pass
            elif part == '..':
                p = os.path.split(p)[0]
            else:
                p = os.path.join(p, part)
        if self._noVideoFlag == False:
            serverPipeline = c2wGstServerPipeline(p, movieIpAddress, moviePort)
        else:
            serverPipeline = None

        if movieId is None:
            movieId = self._lastMovieId
            self._lastMovieId += 1
        self._movieStore.createAndAddMovie(movieTitle, movieIpAddress,
                                           moviePort, p, movieId,
                                           self._noVideoFlag, serverPipeline)

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

        Returns the corresponding IP address and port (as a pair), or
        `None` if the movie does not exist.
        """
        m = self._movieStore.getMovieByTitle(movieTitle)
        if m is None:
            return m
        else:
            return (m.movieIpAddress, m.moviePort)

    def getMovieAddrPortById(self, movieId):
        """
        :param movieId: The numerical identifier of the user.
        :type movieId: int

        Returns the corresponding IP address and port (as a pair), or
        `None` if the movie does not exist.
        """
        m = self._movieStore.getMovieById(movieId)
        if m is None:
            return m
        else:
            return (m.movieIpAddress, m.moviePort)

    def getMovieById(self, movieId):
        """
        :param movieId: The numerical identifier of the user.
        :type movieId: int
        :returns: The corresponding user (instance of
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
        assert isinstance(movieId, int)
        return self._movieStore.getMovieById(movieId)

    def removeAllMovies(self):
        """
        Remove all the movies.
        """
        self._movieStore.removeAllMovies()
        self._lastMovieId = 1

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

    def startStreamingMovie(self, movieTitle):
        """
        Start streaming the corresponding movie.
        """
        if not self._noVideoFlag:
            self._movieStore.startStreamingMovie(movieTitle)

    def stopStreamingMovie(self, movieTitle):
        """
        Stop streaming the corresponding movie.
        """
        if not self._noVideoFlag:
            self._movieStore.stopStreamingMovie(movieTitle)
