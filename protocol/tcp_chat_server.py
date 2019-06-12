# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
import logging
import struct
from twisted.internet import task
from functions import decodeBuffHeader
from functions import prepareBuff
from functions import prepareBuffHeader
from functions import prepareBuffMovieList
from functions import prepareBuffUsersList
from functions import decodeBuffChatMessage
from functions import prepareBuffChatMessage
from c2w.main.constants import ROOM_IDS
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_server_protocol')

class c2wTcpChatServerProtocol(Protocol):
    
    def __init__(self, serverProxy, clientAddress, clientPort):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param clientAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param clientPort: The port number used by the c2w server,
            given by the user.
        Class implementing the TCP version of the client protocol.
        .. note::
            You must write the implementation of this class.
        Each instance must have at least the following attribute:
        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: clientAddress

            The IP address of the client corresponding to this 
            protocol instance.

        .. attribute:: clientPort
            The port number used by the client corresponding to this 
            protocol instance.

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.

        .. note::
            The IP address and port number of the client are provided
            only for the sake of completeness, you do not need to use
            them, as a TCP connection is already associated with only
            one client.
        """

        #: The IP address of the client corresponding to this 
        #: protocol instance.
        self.clientAddress = clientAddress
        #: The port number used by the client corresponding to this 
        #: protocol instance.
        self.clientPort = clientPort
        #: The serverProxy, which the protocol must use
        #: to interact with the user and movie store in the server.
        self.serverProxy = serverProxy
        #: The sequence number to handle lost sent buff.
        self.sequenceNumber = 0
        #: Task would be a dic of all the buff to retransmit everysecond with sequence number as key.
        self.tasks = {}
        #: The total  data received usefull to wait until we received at least one full message from server.
        self.totalBuff = bytes()
        #: Lenght of the last message received.
        self.lenMessage = 0
        #: The next two attributs are important to store the sequence number of
        #: the validation connection and the movieList after connection.
        self.validateConnectionNumber = -1
        self.validateMovieListNumber = -1
        #: The userName of the client connect to the server.
        self.userName = ""
        #: The list of treated client sequence number, use to ignore message already received if an ack is lost.
        self.sequenceNumberTreated = []
    
    
    #: Function that sore the send every seond a message until the ack of client in task, increment sequence number.
    def sendUntilAck(self, buff, sequenceNumber):
        self.tasks[sequenceNumber] = task.LoopingCall(self.transport.write, buff)
        self.tasks[sequenceNumber].start(1.0)
        self.sequenceNumber = self.sequenceNumber + 1
    
    #: Function that send the user list to every client. We camm it everytime there is a change of status.
    def updateUserList(self):
        usersList = self.serverProxy.getUserList()
        print ("userList to send : ", usersList)
        buffUsersList = prepareBuffUsersList(usersList)
        for user in usersList:
            buffHeader = prepareBuffHeader(6, buffUsersList, user.userChatInstance.sequenceNumber)
            buff = prepareBuff(buffHeader, buffUsersList)
            user.userChatInstance.sendUntilAck(buff, user.userChatInstance.sequenceNumber)
            print("sending users list : ", buff, "to ", user.userName)    
        
        
    def dataReceived(self, data):
        """
        :param data: The data received from the client (not necessarily
                     an entire message!)
        Twisted calls this method whenever new data is received on this
        connection.
        """

        print("data received from the client : ", data)
        self.totalBuff += data
        
        #: If the data received is longer than when byte that means we can store the lenght of the message
        if len(self.totalBuff) > 1:
            self.lenMessage = int(struct.unpack("!H", self.totalBuff[0:2])[0])
            
            #: If total buff received longer than one message we can then treat the message
            if len(self.totalBuff) >= self.lenMessage:
                print("totalBuff : ", self.totalBuff)

                separatedDatagram = decodeBuffHeader(self.totalBuff[:self.lenMessage])
                print("message receive from client :")
                print(separatedDatagram)
                senderSequenceNumber = separatedDatagram[1]
                typeOfRequest = separatedDatagram[2]

                #: If message received not an ACK then send ACK
                if typeOfRequest != 0:   
                    buffHeader = prepareBuffHeader(0, "", senderSequenceNumber)
                    self.transport.write(buffHeader)
                    print("sending ", buffHeader, "to the client")
                    
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
                        
                    #: If not we add the sender sequence number to the treated one and we after treat the message
                    else: 
                        self.sequenceNumberTreated.append(senderSequenceNumber)
                        
                #: If data received ACK we stop sending the message according to the sequence number
                if typeOfRequest == 0: 
                    self.tasks[senderSequenceNumber].stop()
                    
                    #: If ACK of connection validation is received then we send movieList to the client
                    if self.validateConnectionNumber == senderSequenceNumber:
                        movies = self.serverProxy.getMovieList()
                        buffMovieList = prepareBuffMovieList(movies)
                        buffHeader = prepareBuffHeader(5, buffMovieList, self.sequenceNumber)
                        buff = prepareBuff(buffHeader, buffMovieList)
                        self.validateMovieListNumber = self.sequenceNumber
                        self.sendUntilAck(buff, self.sequenceNumber)
                        print("sending ", buff, "to the client")

                    #:  if ACK of sent movie list is received then we send new  userList to every client
                    if self.validateMovieListNumber == senderSequenceNumber:
                       self.updateUserList()
                        
                #: If data received is connection request we store the username
                if typeOfRequest == 1: 
                    userName = separatedDatagram[3]
                    self.userName = userName
                    
                    #: if userName already used send a connection refused
                    if self.serverProxy.userExists(userName): 
                        buffHeader = prepareBuffHeader(8, "", senderSequenceNumber)
                        self.sendUntilAck(buffHeader, senderSequenceNumber)
                    
                    #: If not send connection successfull and add user to server proxy
                    else:  
                        buffHeader = prepareBuffHeader(7, "", senderSequenceNumber)
                        self.sendUntilAck(buffHeader, senderSequenceNumber)
                        print("sending ", buffHeader, " to the client")                       
                        self.validateConnectionNumber = senderSequenceNumber                 
                        self.serverProxy.addUser(userName, ROOM_IDS.MAIN_ROOM, userChatInstance=self)
                        
                #If leave Mainroom request we remove user from the proxy and send the new user list to every client.
                if typeOfRequest == 2:
                    userName = separatedDatagram[3]
                    print("the username of the person who wants to leave :", userName)
                    print("userList : ", self.serverProxy.getUserList())
                    self.serverProxy.removeUser(userName)
                    self.updateUserList()
        
                #: If join movie room request we start stream the movie, 
                #: update the user list of server proxy and send it to every client.
                if typeOfRequest == 3:
                    movieTitle = separatedDatagram[3]
                    self.serverProxy.startStreamingMovie(movieTitle)
                    movie = self.serverProxy.getMovieByTitle(movieTitle)
                    idRoom = movie.movieId
                    self.serverProxy.updateUserChatroom(self.userName, str(idRoom))
                    self.updateUserList()
                    print("userList has been updated", self.serverProxy.getUserList())
                    
                #If leave movie room request we update the user list of server proxy and send it to every client.
                if typeOfRequest == 4:
                    """#userRoom = self.serverProxy.getUserByAddress(self.clientAddress).userChatRoom
                    #userList = self.serverProxy.getUserList()
                    #numberUserInMovieRoom = 0
                    #we go through the list of user top see if there is anybody left in the room
                    #for user in userList:
                    #    if user.userChatRoom == userRoom:
                    #        numberUserInMovieRoom += 1
                    #if there is just the user who wants to leave the room we stop streaming video
                    #if numberUserInMovieRoom == 1:
                    #   self.serverProxy.stopStreamingMovie(self.serverProxy.getMovieById(userRoom).movieTitle)"""
                    self.serverProxy.updateUserChatroom(self.userName, ROOM_IDS.MAIN_ROOM)
                    self.updateUserList()
                    print("userList has been updated", self.serverProxy.getUserList())
                
                #: If send message request we get the room of the sender and
                #: send the message to every client in the same room
                if typeOfRequest == 9:

                    userList = self.serverProxy.getUserList()
                    userName, message = decodeBuffChatMessage(self.totalBuff[:self.lenMessage])
                    senderRoom = self.serverProxy.getUserByName(userName).userChatRoom
                    buffPacket = prepareBuffChatMessage(userName, message)
                    requestType = 9
                    for user in userList:
                        if senderRoom == user.userChatRoom:
                            buffHeader = prepareBuffHeader(requestType, buffPacket, user.userChatInstance.sequenceNumber)
                            buff = prepareBuff(buffHeader, buffPacket)
                            user.userChatInstance.sendUntilAck(buff, user.userChatInstance.sequenceNumber)
                            print("sending chat message to : ", user.userName , self.totalBuff[:self.lenMessage])
                
                #: If there is data left to treat (total buff > one message) 
                #: we call recursively datareceivde with the rest of the data
                if len(self.totalBuff[self.lenMessage:]) > 0 :
                    data = self.totalBuff[self.lenMessage:]
                    self.totalBuff = bytes()  
                    self.dataReceived(data)
                    
                self.totalBuff = bytes()
            
        

        pass

