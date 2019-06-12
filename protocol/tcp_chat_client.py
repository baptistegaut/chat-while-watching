# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
from functions import prepareBuffHeader
from functions import prepareBuff
from functions import decodeBuffHeader
from functions import decodeBuffMovieList
from functions import decodeBuffUsersList
from functions import prepareBuffChatMessage
from functions import decodeBuffChatMessage
from c2w.main.constants import ROOM_IDS
import struct
from twisted.internet import task
import logging
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_client_protocol')

class c2wTcpChatClientProtocol(Protocol):

    def __init__(self, clientProxy, serverAddress, serverPort):

        """
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param serverPort: The port number used by the c2w server,
            given by the user.

        Class implementing the UDP version of the client protocol.
        .. note::
            You must write the implementation of this class.
        Each instance must have at least the following attribute:
        .. attribute:: clientProxy
            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.
        .. attribute:: serverAddress
prepareBuff
            The IP address of the c2w server.
        .. attribute:: serverPort
            The port number used by the c2w server.
        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        #: The IP address of the c2w server.
        self.serverAddress = serverAddress
        #: The port number used by the c2w server.
        self.serverPort = serverPort
        #: The clientProxy, which the protocol must use
        #: to interact with the Graphical User Interface
        self.clientProxy = clientProxy
        #: Task would be a dic of all the buff to retransmit everysecond with sequence number as key.
        self.tasks = {}
        #: The dictionnary of idMovie: title of movie or MAINROOM, useful to update status of user
        self.movieIdNameDic = {0: ROOM_IDS.MAIN_ROOM}
        #: The sequence number to handle lost sent buff.
        self.sequenceNumber = 0
        #: The list of movie available
        self.movieList = []
        #: the list of users using the app
        self.userList = []
        #: username of the client connected to the server
        self.userName = ""
        #: The total  data received usefull to wait until we received at least one full message from server.
        self.totalBuff = bytes()
        #: Lenght of the last message received.
        self.lenMessage = 0
        #: The next three attributs are important to store the sequence number of
        #: the quit request the joinroom request and the leave movie room request.
        self.quitRequestNumber = -1
        self.validateJoinRoom = -1
        self.validateJoinMainRoom = -1
        #: The list of treated client sequence number, use to ignore message already received if an ack is lost.
        self.sequenceNumberTreated = []

    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.
        The client proxy calls this function when the user clicks on
        the login button.
        """
        lenUsername = len(userName)
        buffData = struct.pack("!" + str(lenUsername) + "s", userName.encode('utf-8'))
        requestType = 1
        data = userName
        self.userName = userName

        buffHeader = prepareBuffHeader(requestType, data, self.sequenceNumber)
        buffPacket = prepareBuff(buffHeader, buffData)

        self.tasks[self.sequenceNumber] = task.LoopingCall(self.transport.write, buffPacket)
        self.tasks[self.sequenceNumber].start(1.0)
        moduleLogger.debug('loginRequest called with username=%s', userName)
        print("login data sent to the server : ", buffPacket)

        moduleLogger.debug('loginRequest called with username=%s', userName)
        

    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string
        Called by the client proxy when the user has decided to send
        a chat message
        .. note::
           This is the only function handling chat messages, irrespective
           of the room where the user is.  Therefore it is up to the
           c2wChatClientProctocol or to the server to make sure that this
           message is handled properly, i.e., it is shown only by the
           client(s) who are in the same room.
        """
        buffPacket = prepareBuffChatMessage(self.userName, message)
        requestType = 9
        buffHeader = prepareBuffHeader(requestType, buffPacket, self.sequenceNumber)
        buff = prepareBuff(buffHeader, buffPacket)
        self.tasks[self.sequenceNumber] = task.LoopingCall(self.transport.write, buff)
        self.tasks[self.sequenceNumber].start(1.0)
        print("chat message data sent to the server : ", buffPacket)
        pass

    def sendJoinRoomRequestOIE(self, roomName):
        """
        :param roomName: The room name (or movie title.)

        Called by the client proxy  when the user
        has clicked on the watch button or the leave button,
        indicating that she/he wants to change room.
        .. warning:
            The controller sets roomName to
            c2w.main.constants.ROOM_IDS.MAIN_ROOM when the user
            wants to go back to the main room.
        """
        
        print(" the name of the room : ", roomName)
        requestType = 3
        if roomName == ROOM_IDS.MAIN_ROOM:
            roomName = "0"
            requestType = 4
        lenRoomName = len(roomName)
        buffData = struct.pack("!" + str(lenRoomName) + "s", roomName.encode('utf-8'))

        data = roomName
        
        buffHeader = prepareBuffHeader(requestType, data, self.sequenceNumber)
        buffPacket = prepareBuff(buffHeader, buffData)
        
        self.tasks[self.sequenceNumber] = task.LoopingCall(self.transport.write, buffPacket)
        self.tasks[self.sequenceNumber].start(1.0)
        print("sending request of movie room : ", buffPacket)
        if roomName == "0":
            self.validateJoinMainRoom = self.sequenceNumber
        else:
            self.validateJoinRoom = self.sequenceNumber
        
        
        pass

    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        buffHeader = prepareBuffHeader(2,  self.userName, self.sequenceNumber)
        buffUserName = struct.pack("!" + str(len(self.userName)) + "s", self.userName.encode('utf-8'))
        buff = prepareBuff(buffHeader, buffUserName)
        self.tasks[self.sequenceNumber] = task.LoopingCall(self.transport.write, buff)
        self.tasks[self.sequenceNumber].start(1.0)
        print("sending leave request to the server : ", buff )
        self.quitRequestNumber = self.sequenceNumber

        pass

    def dataReceived(self, data):

    
        print("data received from the server : ", data)
        self.totalBuff += data
        
        #: If the data received is longer than when byte that means we can store the lenght of the message
        if len(self.totalBuff) > 1:
            self.lenMessage = int(struct.unpack("!H", self.totalBuff[0:2])[0])
            
            #: If total buff received longer than one message we can then treat the message
            if len(self.totalBuff) >= self.lenMessage:
                print("totalBuff : ", self.totalBuff)
                separatedDatagram = decodeBuffHeader(self.totalBuff[:self.lenMessage])
                print("message receive from server :")
                print(separatedDatagram)
                senderSequenceNumber = separatedDatagram[1]
                typeOfRequest = separatedDatagram[2]
                
                #: If message received not an ACK then send ACK
                if typeOfRequest != 0:   
                    buffHeader = prepareBuffHeader(0, "", senderSequenceNumber)
                    self.transport.write(buffHeader) 
                    print("sending ", buffHeader, "to the server")
                    
                    #: Then we check if the message has been already treated (received once and ack sent lost).
                    #: if it is we ignore it
                    if senderSequenceNumber in self.sequenceNumberTreated and typeOfRequest != 1:
                        
                        #: If there is data left to treat (total buff > one message) 
                        #: we call recursively datareceivde with the rest of the data
                        if len(self.totalBuff[self.lenMessage:]) > 0 :
                            data = self.totalBuff[self.lenMessage:]
                            self.totalBuff = bytes()  
                            self.dataReceived(data)
                        else:
                            return
                        
                    #: If not we add the sender sequence number to the treated one and we then treat the message
                    else: 
                        self.sequenceNumberTreated.append(senderSequenceNumber)
                        
                #: If message received ACK increment sequence number, stop task    
                if typeOfRequest == 0: 
                    if senderSequenceNumber == self.sequenceNumber:
                        self.tasks[senderSequenceNumber].stop()
                        self.sequenceNumber = self.sequenceNumber + 1
                        
                        # If ack of quit request is received we empty the userList to  and leave the system
                        if self.quitRequestNumber == senderSequenceNumber:
                            self.userList = []
                            self.clientProxy.leaveSystemOKONE()
                        
                        #: If ack of validateJoinRoom received we call the client proxy to join the room    
                        if senderSequenceNumber == self.validateJoinRoom:
                            self.clientProxy.joinRoomOKONE()

                        #: If ack of validateJoinMainRoom received we call the client proxy to join the main room
                        if senderSequenceNumber == self.validateJoinMainRoom:
                            self.clientProxy.joinRoomOKONE()

                #: if message received  list of movies available we store the movie list and create the dictionnary of movie id: title            
                if typeOfRequest == 5:   
                    self.movieList = decodeBuffMovieList(self.totalBuff[:self.lenMessage])
                    print("la liste des films est la suivante", self.movieList)
                    #on créer le dictionnaire id-> nom film
                    for movie in self.movieList:
                        self.movieIdNameDic[movie[3]] = movie[0]
                    print("voici le dictionnaire des films : ", self.movieIdNameDic)
                
                #if message received list of users: we create the userList with movie title or MAIN_ROOM thanks to the dictionnary
                if typeOfRequest == 6:
                        newUserList = decodeBuffUsersList(self.totalBuff[:self.lenMessage])
                        userListwithMovieTitle = []
                        for user in newUserList:
                            userListwithMovieTitle.append((user[0], self.movieIdNameDic[user[1]]))
                        
                        #: If it's the first time the client receive userList we display main room
                        if self.userList ==[]:
                            self.userList = userListwithMovieTitle
                            self.clientProxy.initCompleteONE(userListwithMovieTitle, self.movieList)
                        
                        #: If not we set the new userList with position of user to update satus
                        else:
                            self.userList = userListwithMovieTitle
                            self.clientProxy.setUserListONE(userListwithMovieTitle)
                            print("userList has been updated : ", self.userList)
                
                #: If message received connection refused request we display it calling the proxy
                if typeOfRequest == 8:
                    self.clientProxy.connectionRejectedONE("userName already used")
                    
                #if message received is send message request we call the proxy to display the message
                if typeOfRequest == 9:
                    userName, message = decodeBuffChatMessage(self.totalBuff[:self.lenMessage])
                    if userName != self.userName:
                        self.clientProxy.chatMessageReceivedONE(userName, message)
                
                #if datagram longer than one message : call dataReceived with the rest of the data
                if len(self.totalBuff[self.lenMessage:]) > 0 :

                    data = self.totalBuff[self.lenMessage:]
                    self.totalBuff = bytes()  
                    self.dataReceived(data)

                self.totalBuff = bytes() 


        """
        :param data: The data received from the client (not necessarily
                     an entire message!)
        Twisted calls this method whenever new data is received on this
        connection.
        """
        pass
