    # -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
from twisted.internet import task
from c2w.main.constants import ROOM_IDS
import logging
import struct
from functions import prepareBuffHeader
from functions import prepareBuff
from functions import decodeBuffHeader
from functions import decodeBuffMovieList
from functions import decodeBuffUsersList
from functions import prepareBuffChatMessage
from functions import decodeBuffChatMessage

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_client_protocol')


class c2wUdpChatClientProtocol(DatagramProtocol):

    def __init__(self, serverAddress, serverPort, clientProxy, lossPr):
        """
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param serverPort: The port number used by the c2w server,
            given by the user.
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attributes:

        .. attribute:: serverAddress

            The IP address of the c2w server.

        .. attribute:: serverPort

            The port number of the c2w server.

        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        #: The IP address of the c2w server.
        self.tasks = {}
        self.serverAddress = serverAddress
        #: The port number of the c2w server.
        self.serverPort = serverPort
        #: The clientProxy, which the protocol must use
        #: to interact with the Graphical User Interface.
        self.clientProxy = clientProxy
        self.lossPr = lossPr
        self.sequenceNumber = 0
        self.movieList = []
        self.movieIdNameDic = {0: ROOM_IDS.MAIN_ROOM}
        self.userList = []
        self.userName = ""
        self.quitRequestNumber = -1
        self.validateJoinRoom = -1
        self.validateJoinMainRoom = -1
        # La liste des numéros de séquence des clients traités, permet 
        # d'ignorer les messages déjà reçus en cas de perte d'un chèque.
        self.sequenceNumberTreated = []
        
    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport
        
        
        pass

    #Le client envoie une demande de connexion au serveur en rentrant son userName
    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The client proxy calls this function when the user clicks on
        the login button.
        """    
        lenUsername = len(userName)
        buffData = struct.pack("!" + str(lenUsername) + "s", userName.encode('utf-8'))#l'username (ici les donées) est encodé en binaire pour l'envoie au serveur 
        requestType = 1
        data = userName
        self.userName = userName
   
        buffHeader = prepareBuffHeader(requestType, data, self.sequenceNumber)
        buffPacket = prepareBuff(buffHeader, buffData)
        
        self.tasks[self.sequenceNumber] = task.LoopingCall(self.transport.write, buffPacket, (self.serverAddress, self.serverPort)) #le client envoie la tache a effectuer au serveur
        self.tasks[self.sequenceNumber].start(1.0) # l'envoie est répéter chaque seconde jusqu'à l'envoie de l'ack
        moduleLogger.debug('loginRequest called with username=%s', userName)
        print("login data sent to the server : ", buffPacket)

        pass
        
        
    #Le client envoie un message dans le Chat  
    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string

        Called by the client proxy  when the user has decided to send
        a chat message

        .. note::
           This is the only function handling chat messages, irrespective
           of the room where the user is.  Therefore it is up to the
           c2wChatClientProctocol or to the server to make sure that this
           message is handled properly, i.e., it is shown only by the
           client(s) who are in the same room.
        """       
        #le message envoyé par un utilisateur et son nom associé est alors transformé au format binaire par prepareBuffChatMessage
        buffPacket = prepareBuffChatMessage(self.userName, message)
        requestType = 9
        buffHeader = prepareBuffHeader(requestType, buffPacket, self.sequenceNumber)
        buff = prepareBuff(buffHeader, buffPacket)
        #voie de la tache au serveur, le serveur va diffusé le message à tous les autres utilisateurs qui sont dans sa room
        self.tasks[self.sequenceNumber] = task.LoopingCall(self.transport.write, buff, (self.serverAddress, self.serverPort)) 
        self.tasks[self.sequenceNumber].start(1.0)
        print("chat message data sent to the server : ", buffPacket)
        
        pass
    #Le client envoie une requête d'accès à une room au serveur
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
        
        self.tasks[self.sequenceNumber] = task.LoopingCall(self.transport.write, buffPacket, (self.serverAddress, self.serverPort))
        self.tasks[self.sequenceNumber].start(1.0)
        print("sending request of movie room : ", buffPacket)
        if roomName == "0":
            self.validateJoinMainRoom = self.sequenceNumber
        else:
            self.validateJoinRoom = self.sequenceNumber

        pass

    #Le client envoie une requête au serveur pour quitter une room
    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        
        buffHeader = prepareBuffHeader(2,  self.userName, self.sequenceNumber)
        buffUserName = struct.pack("!" + str(len(self.userName)) + "s", self.userName.encode('utf-8'))
        buff = prepareBuff(buffHeader, buffUserName)
        self.tasks[self.sequenceNumber] = task.LoopingCall(self.transport.write, buff, (self.serverAddress, self.serverPort))
        self.tasks[self.sequenceNumber].start(1.0)
        print("sending leave request to the server : ", buff )
        self.quitRequestNumber = self.sequenceNumber
        
        pass

    def datagramReceived(self, datagram, host_port):
         
        """:param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.

        Called **by Twisted** when the client has received a UDP
        packet."""
        
        separatedDatagram = decodeBuffHeader(datagram) #on attribut separatedDatagram à l'intégralité des données transmis
        print("message receive from server :")
        print(separatedDatagram)
        
        
        senderSequenceNumber = separatedDatagram[1]
        typeOfRequest = separatedDatagram[2]
        
        if typeOfRequest != 0:   #Si ce qu'on reçoit ce n'est pas un ack on renvoie un ack au serveur (data='')
            buffHeader = prepareBuffHeader(0, "", senderSequenceNumber)
            self.transport.write(buffHeader, (host_port)) 
            print("sending ack to the server: ", buffHeader)
            #: On regarde ensuite si le numéro de séquence est dans la liste des numéros de séquence
            #: déjà traité (dans le cas d'un ack perdu). Si c'est le cas on sort de la fonction sans traiter le message
            if senderSequenceNumber in self.sequenceNumberTreated and typeOfRequest != 1:
                return
             #: Sinon on va traiter le message donc on ajoute le numéro de séquence de l'envoyeur dans la liste des numéros de séquences traités.
            else: 
                self.sequenceNumberTreated.append(senderSequenceNumber)
        
        if typeOfRequest == 0: #Si on reçoit un l'ack on incrémente le sequence number, et on stop la demande
            if senderSequenceNumber == self.sequenceNumber:
                self.tasks[senderSequenceNumber].stop()
                self.sequenceNumber = self.sequenceNumber + 1
                
                if self.quitRequestNumber == senderSequenceNumber:
                    self.userList == []
                    self.clientProxy.leaveSystemOKONE()

                
                if senderSequenceNumber == self.validateJoinRoom:
                    self.clientProxy.joinRoomOKONE()

                if senderSequenceNumber == self.validateJoinMainRoom:
                    self.clientProxy.joinRoomOKONE()
                    
        
        #Si on reçoit la liste des films disponible            
        if typeOfRequest == 5:   
            self.movieList = decodeBuffMovieList(datagram)
            print("la liste des films est la suivante", self.movieList)
            #on créer le dictionnaire id-> nom film
            for movie in self.movieList:
                self.movieIdNameDic[movie[3]] = movie[0]
            print("voici le dictionnaire des films : ", self.movieIdNameDic)


        
        
        #Si on reçoit la liste des utilisateurs 
        if typeOfRequest == 6:
            newUserList = decodeBuffUsersList(datagram)
            userListwithMovieTitle = []
            for user in newUserList:
                userListwithMovieTitle.append((user[0], self.movieIdNameDic[user[1]]))
	    #Si c'est la première fois que le client reçoit l'userList on l'affiche dans la mainroom 
            if self.userList ==[]:
                self.userList = userListwithMovieTitle
                self.clientProxy.initCompleteONE(userListwithMovieTitle, self.movieList)

            else:
                self.userList = userListwithMovieTitle
                self.clientProxy.setUserListONE(userListwithMovieTitle)
                print("userList has been updated : ", self.userList)

                
        
        #Si l'username est déjà utilisé, la connexion est rejeté
        if typeOfRequest == 8:
            self.clientProxy.connectionRejectedONE("userName already used")
            
        #Si l'utilisateur envoie un message, on prend l'username et le message comme données et on envoie au serveur 
        if typeOfRequest == 9:
            userName, message = decodeBuffChatMessage(datagram)
            if userName != self.userName: #Pas de Ré-envoi à sois même parceque c'est gérer directement 
                self.clientProxy.chatMessageReceivedONE(userName, message)
            
            
            
            
        
      
        pass
