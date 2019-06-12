import logging
import sys

sys.dont_write_bytecode = True
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.user')


class c2wUser(object):

    def __init__(self, userName, userChatRoom, userChatInstance=None,
                 userAddress=None, userId=None):
        """
        :param userName: The name of the user.
        :type userName: string
        :param userChatRoom: The name of the chat room where the user is
                            currently located.
        :type userChatRoom: string or one of the values of
                    c2w.main.constants.ROOM_IDS
        :param userId: The numerical user id (optional, can be None if not
                         needed)
        :type userId: integer
        :param userChatInstance: A reference to the corresponding instance of
                     c2wChatServerProtocol (used only in the server)
        :type userChatInstance: instance of c2wChatServerProtocol
        :param userAddress: The address of the corresponding client (optional)

        This class contains all the information about a user, consisting
        in the following attributes:

        .. attribute:: userName

            The name of the user (must be unique).

        .. attribute:: userChatRoom

            The name of the chat room where the user is currently located.
            It can also take one of the values of
            :py:class:`c2w.main.constants.ROOM_IDS`.

        .. attribute:: userId

            The numerical id of the user (can be None if not used)

        .. attribute:: userChatInstance

            A reference to the corresponding instance of the
            c2wChatServerProtocol.  (Used only in the server in order
            to send messages to multiple users.)

        .. attribute:: userAddress

            The address of the corresponding client.  (Optional)
        """
        #: The user Id (can be none).
        self.userId = userId
        #: The user name (must be unique).
        self.userName = userName
        #: The chatroom where the user is located.
        self.userChatRoom = userChatRoom
        #: This field can be used to store a reference to the
        #: corresponding protocol instance (only for the server).
        self.userChatInstance = userChatInstance
        #: This field can be used to store the address of the corresponding
        #: user (only for the server).
        self.userAddress = userAddress

    def __repr__(self):
        s = '<Instance of c2wUser; userName={0}, userChatRoom={1}, '.format(
             self.userName, self.userChatRoom)
        s += 'userChatInstance={0}, userAddress={1}>'.format(
              self.userChatInstance, self.userAddress)
        return s


class c2wUserStore(object):
    def __init__(self):
        """
        Class that can store multiple users (as if they were in a list).

        .. py:attribute::
               _allUserDic:

           a dictionary mapping user names to users
           (instances of the class :py:class:`User`)

        .. warning::
            The :py:attr:`_allUserDic` is a 'private' member and *must not*
            be accessed directly.

        .. warning::
            Each element (user) must have a unique name.  If this is not the
            case an exception is thrown.

        """

        self._allUserDic = {}

    def addUser(self, user):
        """
        :param user: The user to be added to the list.
        :type user: instance of :py:class:`~c2w.main.user.c2wUser`

        Add a user to the list.
        """
        if not isinstance(user, c2wUser):
            moduleLogger.error("USER_STORE_ERROR (addUser): the user" +
                " parameter does not have the name and/or chatRoom " +
                " attribute(s), make sure it is instance of the User class")
            raise TypeError('user must be an instance of the User class')
        if user.userName in list(self._allUserDic.keys()):
            moduleLogger.error("USER_STORE_ERROR (addUser): the user" +
                "  %s is already in the dictionary", user.userName)
            raise ValueError("user already in the dictionary")
        else:
            moduleLogger.debug("USER_STORE (addUSer): adding user" +
                " with name %s to the dictionary", user.userName)
            self._allUserDic[user.userName] = user

    def createAndAddUser(self, userName, userChatRoom, userChatInstance=None,
                         userAddress=None, userId=None):
        """
        :param userName: The name of the user.
        :type userName: string
        :param userChatRoom: The name of the chat room where the user is
                            currently located.
        :type userChatRoom: string or one of the values of
                    c2w.main.c2w_constants.ROOM_IDS
        :param userId: The numerical user id (optional, can be None if not
                         needed)
        :type userId: integer
        :param userChatInstance: A reference to the corresponding instance of
                     c2wChatServerProtocol (used only in the server)
        :type userChatInstance: instance of c2wChatServerProtocol
        :param userAddress: The address of the corresponding client (optional)
        :raises: ValueError if there is already a user with the same name
                in the user list.

        Create a new user and add it to the list.
        """

        if userName in list(self._allUserDic.keys()):
            moduleLogger.error("USER_STORE_ERROR (addUser): the user" +
                "  %s is already in the dictionary", userName)
            raise ValueError("user already in the list")
        else:
            user = c2wUser(userName, userChatRoom, userChatInstance,
                           userAddress, userId)
            moduleLogger.debug("USER_STORE (addUSer): adding user" +
                " with name %s to the dictionary", user.userName)
            self._allUserDic[user.userName] = user

    def getUserByName(self, userName):
        """
        :param userName: The name of the user
        :type userName: string
        :returns: The corresponding user (instance of
                  :py:class:`~c2w.main.user.c2wUser`), ``None`` if
                  there is no user with the given name in the list.
        """
        try:
            u = self._allUserDic[userName]
        except KeyError:
            u = None
        return u

    def userExist(self, userName):
        """
        :param userName: The name of the user.
        :type userName: string
        :rtype:  boolean

        Check if a given userId is already present in the user list.
        """

        return userName in list(self._allUserDic.keys())

    def updateUserChatRoom(self, userName, newUserChatRoom):
        """
        :param userName: The name of the user.
        :type userName: string
        :param userChatRoom: The name of the chat room where the user is
                            currently located.
        :type userChatRoom: string or one of the values of
                    c2w.main.constants.ROOM_IDS

        Update the location of the user whose name is :py:obj:`userName`.
        """
        self._allUserDic[userName].userChatRoom = newUserChatRoom

    def removeUser(self, userName):
        """
        :param userName: The name of the user.
        :type userName: string
        :raises: ValueError if there is no user with this name in the list.

        Delete the user from the dictionary.
        """
        if userName in list(self._allUserDic.keys()):
            del self._allUserDic[userName]
        else:
            raise ValueError("trying to delete a user not in the list")

    def removeAllUsers(self):
        """
        Remove all the users from the list.
        """
        self._allUserDic = {}

    def getUserList(self):
        """
        :returns: A list with all the users in the server.
        """
        usersList = []
        for u in list(self._allUserDic.values()):
            usersList.append(u)
        return usersList

    def getChatRoomUsersList(self, chatRoomName):
        """
        :param chatRoomName: The name of a chatRoomName.
        :type chatRoomName: string or one of the values of
                    c2w.main.constants.ROOM_IDS
        :returns: A list of all the users in the corresponding chat room
                    (each element of the list is an instance of
                    :py:class:`~c2w.main.user.c2wUser`.

        Return a list with all the users in a specific chat room.

        .. note::
            The list can be empty (if no user is in the given room or if there
            is no room with that name).
        """

        usersChatRoomList = []
        for u in list(self._allUserDic.values()):
            if u.userChatRoom == chatRoomName:
                usersChatRoomList.append(u)
        return usersChatRoomList

    def __iter__(self):
        """
        Needed to make the class iterable.

        You can do something like the following:
        .. code-block:: python
            userStore = c2wUserStore()
            # add some users
            userStore.createAndAddUser( ...)
            for u in userStore():
                print(u.userName)
        """
        return iter(list(self._allUserDic.values()))

    def getUserById(self, uid):
        """
        :param uid: The numerical identifier of the user.
        :type uid: int
        :returns: The corresponding user (instance of
                  :py:class:`~c2w.main.user.c2wUser`), ``None`` if
                  there is no user with the given name in the list.

        .. note::
            This function works correctly only if there is at most one
            user with the given id.  If multiple users have the same id
            this function will return only one of them.
        """
        r = [u for k, u in self._allUserDic.items() if u.userId == uid]
        if r:
            return r[0]
        else:
            return None

    def getUserByAddress(self, addr):
        """
        :param addr: The address of the user.  Must be of the same type
            used when creating the user, e.g., a pair (address, port).

        :returns: The corresponding user (instance of
                  :py:class:`~c2w.main.user.c2wUser`), ``None`` if
                  there is no user with the given name in the list.

        .. note::
            This function works correctly only if there is at most one
            user with the given address.  If multiple users have the same
            address this function will return only one of them.
        """
        r = [u for k, u in self._allUserDic.items() 
             if u.userAddress == addr]
        if r:
            return r[0]
        else:
            return None
