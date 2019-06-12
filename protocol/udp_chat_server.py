# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import logging
from functions import decodeBuffHeader
from functions import prepareBuff
from functions import prepareBuffHeader
from functions import prepareBuffMovieList
from functions import prepareBuffUsersList
from functions import prepareBuffChatMessage
from functions import decodeBuffChatMessage
from twisted.internet import task
from c2w.main.constants import ROOM_IDS

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_server_protocol')


class c2wUdpChatServerProtocol(DatagramProtocol):

    def __init__(self, serverProxy, lossPr):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param lossPr: The packet loss probability for outgoing packets.  Do
            not modify this value!

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """
        self.tasks = {}
        #: The serverProxy, which the protocol must use
        #: to interact with the server (to access the movie list and to 
        #: access and modify the user list).
        self.serverProxy = serverProxy
        self.lossPr = lossPr
        #attribution des numéros de séquences (relatif binaire) pour l'interaction serveur <-> clients
        self.sequenceNumber = 0
        #alidate pour vérifier la réception d'ack (-1 pour éviter le conflit avec le typeofRequest==0) 
        self.validateConnectionNumber = -1 
        self.validateMovieListNumber = -1
        self.sequenceNumberTreatedPerUser  = {}

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


        
        
    #Côté serveur tout dépend de la fonction datagramReceived car le serveur agit 
    #uniquement en fonction des données qu'il reçoit pour chaque client (host_port)
    def datagramReceived(self, datagram, host_port):
        
        separatedDatagram = decodeBuffHeader(datagram)
        print("meesage receive from client :")
        print(separatedDatagram)
        
        senderSequenceNumber = separatedDatagram[1]
        typeOfRequest = separatedDatagram[2]
        

        
        #fonction qui envoie chaque seconde un buffer jusqu'à reception d'un ack, 
        #chaque fois le sequenceNumber est incrémenter 
        def sendUntilAck(buff, sequenceNumber, host_port):
            self.tasks[sequenceNumber] = task.LoopingCall(self.transport.write, buff, (host_port))
            self.tasks[sequenceNumber].start(1.0)
            self.sequenceNumber = self.sequenceNumber + 1
            
            
        
        #fonction qui envoie la liste des utilisateurs (en l'actualisant) à chaque fois que 
        #un d'eux rentre ou quitte une room 
        def updateUserList():
                usersList = self.serverProxy.getUserList()
                print ("userList to send : ", usersList)
                buffUsersList = prepareBuffUsersList(usersList)
                for user in usersList:
                    buffHeader = prepareBuffHeader(6, buffUsersList, self.sequenceNumber)
                    buff = prepareBuff(buffHeader, buffUsersList)
                    sendUntilAck(buff, self.sequenceNumber, user.userAddress)
                    print("sending users list : ", buff, "to ", user.userName)
        
        
        #Si ce qu'on reçoit ce n'est pas un ack on renvoie un ack (juste un header) au client (data='')
        if typeOfRequest != 0:   
            buffHeader = prepareBuffHeader(0, "", senderSequenceNumber)
            self.transport.write(buffHeader, (host_port))
            print("sending ack to the client : ", buffHeader)
            
            #: On regarde ensuite si le numéro de séquence est dans la liste des numéros de séquence
            #: déjà traité (dans le cas d'un ack perdu). Si c'est le cas on sort de la fonction sans traiter le message
            if typeOfRequest != 1:
                senderName = self.serverProxy.getUserByAddress(host_port).userName
                if senderSequenceNumber in  self.sequenceNumberTreatedPerUser[senderName]:
                    return
             #: Sinon on va traiter le message donc on ajoute le numéro de séquence de l'envoyeur dans la liste des numéros de séquences traités.
                else: 
                    senderName = self.serverProxy.getUserByAddress(host_port).userName
                    self.sequenceNumberTreatedPerUser[senderName].append(senderSequenceNumber)
        
        
        #Si on reçoit un ack on stop le looping et on envoie le paquet
        if typeOfRequest == 0: 
            self.tasks[senderSequenceNumber].stop()
            
            if self.validateConnectionNumber == senderSequenceNumber:
                #Si l'ack de connection est bien reçu on envoie la liste des films 
                #que client (requestType=5) et on attend l'ack
                movies = self.serverProxy.getMovieList()
                buffMovieList = prepareBuffMovieList(movies)
                buffHeader = prepareBuffHeader(5, buffMovieList, self.sequenceNumber)
                buff = prepareBuff(buffHeader, buffMovieList)
                print("sending movie list : ", buff, "to the client")
                self.validateMovieListNumber = self.sequenceNumber
                sendUntilAck(buff, self.sequenceNumber, host_port)
                
                
            
            
            #Si l'ack du client pour la liste des films est reçu on envoie alors la liste des utilisateurs est actualisé    
            if self.validateMovieListNumber == senderSequenceNumber:
               updateUserList()
                
            
        
        # Si le serveur reçoit une requête de login, on vérifie d'abord si l'userName est disponible, si c'est le cas 
        # connection est autorisé et l'utilisateur est ajouter à l'userList et on instancie la liste des numéro de séquences traités liée à l'utilisateur
        if typeOfRequest == 1:
            userName = separatedDatagram[3]
            
            if self.serverProxy.userExists(userName): #Si l'userName est déjà utilisé la connection est refusé -> Message connection refused!
                buffHeader = prepareBuffHeader(8, "", senderSequenceNumber)
                sendUntilAck(buffHeader, senderSequenceNumber, host_port) #attente de l'ack de l'utilisateur 
                print("sending conection refused to the client : ", buffHeader )
                
            
            else:  # userName disponible -> connection autorisé 
                buffHeader = prepareBuffHeader(7, "", senderSequenceNumber)
                sendUntilAck(buffHeader, senderSequenceNumber, host_port)
                print("sending conection accepted to the client : ", buffHeader )
                self.validateConnectionNumber = senderSequenceNumber
                self.serverProxy.addUser(userName, ROOM_IDS.MAIN_ROOM, userChatInstance=None, userAddress=host_port)
                self.sequenceNumberTreatedPerUser[userName] = []
                
        
        #Si le serveur reçoit une requête pour quitter la mainRoom, le nom de l'utilisateur est supprimer de l'userlist 
        # la liste des utilisateurs est actualisé
        if typeOfRequest == 2:
            userName = separatedDatagram[3]
            print("the username of the person who wants to leave :", userName)
            print("userList : ", self.serverProxy.getUserList())
            self.serverProxy.removeUser(userName)
            updateUserList()
        
        #Si le serveur reçoit une requête pour rentrer dans une movie room, on démarre automatiquement le film 
        if typeOfRequest == 3:
            movieTitle = separatedDatagram[3]
            self.serverProxy.startStreamingMovie(movieTitle)
            movie = self.serverProxy.getMovieByTitle(movieTitle)
            idMovie = movie.movieId
            # On actualise alors la liste des utilisateurs dans la movie room et on l'envoie à tous les autres
            userName = self.serverProxy.getUserByAddress(host_port).userName
            self.serverProxy.updateUserChatroom(userName, str(idMovie))
            updateUserList()
            print("userList has been updated", self.serverProxy.getUserList())

        #Si le serveur reçoit une requête pour sortir d'une une movie room,On actualise alors la liste des utilisateurs 
        #ns la movie room et on l'envoie à tous les autres
        if typeOfRequest == 4:
            '''#we want to see if the user is the last one in the room
            #userRoom = self.serverProxy.getUserByAddress(host_port).userChatRoom
            #userList = self.serverProxy.getUserList()
            #numberUserInMovieRoom = 0
            #we go through the list of user top see if there is anybody left in the room
            #for user in userList:
            #   if user.userChatRoom == userRoom:
            #       numberUserInMovieRoom += 1
            #if there is just the user who wants to leave the room we stop streaming video
            #if numberUserInMovieRoom == 1:
             #   self.serverProxy.stopStreamingMovie(self.serverProxy.getMovieById(userRoom).movieTitle)'''
            userName = self.serverProxy.getUserByAddress(host_port).userName
            self.serverProxy.updateUserChatroom(userName, ROOM_IDS.MAIN_ROOM)
            updateUserList()
            print("userList has been updated", self.serverProxy.getUserList())

        
        #Si le serveur reçoit une requête d'un client pour envoyer un message, le serveur envoie ce message à tout les autres utilisateurs
        # où il est présent (if dans la videoRomm ou si mainRoom) et attend les ack
        if typeOfRequest == 9:

            userList = self.serverProxy.getUserList()
            userName, message = decodeBuffChatMessage(datagram)
            senderRoom = self.serverProxy.getUserByName(userName).userChatRoom
            buffPacket = prepareBuffChatMessage(userName, message)
            requestType = 9
            for user in userList:
                if senderRoom == user.userChatRoom:
                    buffHeader = prepareBuffHeader(requestType, buffPacket, self.sequenceNumber)
                    buff = prepareBuff(buffHeader, buffPacket)
                    sendUntilAck(buff, self.sequenceNumber, user.userAddress)
                    print("sending chat message to client : " , datagram)
                    
        
        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.
        
        Twisted calls this method when the server has received a UDP
        packet.  You cannot change the signature of this method.
        """
        
        pass
    
