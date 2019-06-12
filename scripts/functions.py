#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:54:13 2019

@author: vblua
"""
import struct
from c2w.main.constants import ROOM_IDS


##
# Numéro 1 : prepareBuffHeader est une fonction qui retourne le header de chaque paquet 
#qui doit être envoyé. Elle prend en argument : le numéro de séquence, le type lié à la requête et l'ensemble des données envoyées.
def prepareBuffHeader(requestType, data, sequenceNumber):
     lenPacket = 4 + len(data) #ajout de 4 bit à la longeur du paquet de données
     buffLenPacket = struct.pack('!H', lenPacket) #struct.pack permet de convertir l'ensemble des données en binaires ! 
     #Mais il faut fournir le format, ici par '!H' (avec une taille de 2) 
     #Ici pour structurer le numéro de séquence et le type sur respectivement 12 et 4 bits, nous devons décaler vers la gauche le numéro de séquence 
     #de 4 bits. Après quoi nous pouvons additionner les deux nombres bit à bit. En prenant en considération que les nombres sont tout deux sur 2 octets.
     decaleSequenceNumber = sequenceNumber<<4
     sequenceAndTypeNumber = decaleSequenceNumber|requestType
     buffSequenceAndTypeNumber = struct.pack('!H', sequenceAndTypeNumber)
     buffHeader = buffLenPacket + buffSequenceAndTypeNumber
     return buffHeader # on récupère le header du paquet

# fonction qui assemble les buffer header et données
def prepareBuff(buffHeader, buffData):
     buffPacket =  buffHeader + buffData
     return buffPacket

#Numéro 2 : decodeBuffHeader est une fonction qui prend en paramètre le paquet reçu et qui retourne une liste contenant :
#la longueur du paquet, le numéro de séquence, le type de message et l'intégralités des données transmises. il sert aussi pour le nom d'utilisateur et le nom d'un film
def decodeBuffHeader(datagram):
    lData = len(datagram) - 4  #on retire les 4 bits ajouter à la longeur du paquet de données
    rawDatagram = struct.unpack('!HH{0}s'.format(lData), datagram) #struct.unpack décompresse la valeur emballée dans sa représentation originale 
    #avec le format spécifié, ici '!HH{0}s'. struct.unpack renvoie toujours un tuple, même s'il n'y a qu'un seul élément.
    lenPacket = int(rawDatagram[0]) # on prend alors comme entier le premier élément de rawDatagram renvoyé par struct.unpack
    sequenceAndTypeNumber = int(rawDatagram[1])
    typeNumber = sequenceAndTypeNumber & 15
    sequenceNumber = sequenceAndTypeNumber >> 4 #décalage vers la droite le numéro de séquence de 4 bits
    if typeNumber == 1 or typeNumber == 2 or typeNumber == 3:
        data = str(rawDatagram[2], 'utf-8')
    else:
        data = rawDatagram[2]
    
    if data == "": # si les données envoyées sont vide ont retourne tout sauf les données 
        decodeBuff = [lenPacket, sequenceNumber, typeNumber]
    else: # sinon on retourne tout, plus les données 
        decodeBuff = [lenPacket, sequenceNumber, typeNumber, data]
    
    return decodeBuff

#Numéro 3 : prepareBuffMovieList est une fonction qui prend en paramètre la liste des films disponibles et qui renvoie 
#une liste de toutes les informations concernant ces films.
def prepareBuffMovieList(MovieList):
    buffMovieList = bytes() # La méthode bytes() retourne un objet octect initialisé par la taille de ces données
    for i in range(len(MovieList)):
        ipMovie = MovieList[i].movieIpAddress # on prend tous les ip de tous les films
        ipMovieList = ipMovie.split(".") # on sépare ces ip dans la liste
        buffIp = struct.pack('!B', int(ipMovieList[0])) + struct.pack('!B', int(ipMovieList[1])) + struct.pack('!B', int(ipMovieList[2])) + struct.pack('!B', int(ipMovieList[3]))
        adrPort = MovieList[i].moviePort # on prend tous les adresses de port de tous les films
        buffAdrPort = struct.pack('!H', adrPort) 
        idMovie = MovieList[i].movieId # on prend tous les id de tous les films
        buffIdMovie = struct.pack('!B', idMovie) #on convertit en binaire mais ici avec une taille de 1 grâce à '!B'
        nameMovie = MovieList[i].movieTitle # on prend tous les nom de tous les films
        buffNameMovie = struct.pack('!{0}s'.format(len(nameMovie)), nameMovie.encode('utf-8')) # convertit sous forme de string
        lenMovie =   len(nameMovie) + 9
        buffLenMovie = struct.pack('!H', lenMovie)
        BuffMovie = buffIp + buffAdrPort + buffLenMovie +buffIdMovie + buffNameMovie
        buffMovieList += BuffMovie # on incrémente pour tous les films disponibles 
    return buffMovieList

# Numéro 4 : decodeBuffMovieListest une fonction qui prend en paramètre tout le paquet reçu et qui retourne la liste des films décoder
#et leurs propres paramètres. Dès qu'il est reçu chaque paramèrtre est décompressé et ajouté dans la liste movieList.
def decodeBuffMovieList(datagram):
    movieListDatagram = datagram[4:]
    movieList = []
    k = 0
    while k < len(movieListDatagram):
        ipMovie = str(movieListDatagram[k]) + "." + str(movieListDatagram[k + 1]) + "." + str(movieListDatagram[k + 2]) + "." + str(movieListDatagram[k + 3])
        k = k + 4
        adrPort = struct.unpack('!H',movieListDatagram[k : k + 2])[0]
        k = k + 2
        lenMovie = int(struct.unpack('!H',movieListDatagram[k : k + 2])[0]) - 9
        k  = k + 2
        idMovie = struct.unpack('!B', movieListDatagram[k : k + 1])[0]
        k = k + 1
        nameMovie = str(struct.unpack('!{0}s'.format(lenMovie), movieListDatagram[k : k + lenMovie])[0], 'utf-8')
        k = k + lenMovie
        movieList.append((nameMovie, ipMovie, adrPort, idMovie))
        
    return movieList
        
        
# Numéro 5 : prepareBuffUsersList est une fonction qui prend en argument la liste des utilisateurs qui la compresse 
#en format binaire et qui renvoie cette même liste
def prepareBuffUsersList(usersList):
    buffUsersList = bytes()
    for user in usersList:
        userName = user.userName
        lenUserName = len(userName)
        buffLenUserName = struct.pack('!B', lenUserName)
        buffUserName = struct.pack('!{0}s'.format(lenUserName), userName.encode('utf-8'))
        status = user.userChatRoom
        if status == ROOM_IDS.MAIN_ROOM:
            buffStatus = struct.pack('!B', 0)
        else:
            buffStatus = struct.pack('!B', int(status))
        buffUsersList += buffLenUserName + buffStatus + buffUserName
    return buffUsersList

# Numéro 6 : decodeBuffUsersList est une fonction qui prend en argument l'ensemble des données reçues et qui parmi celle-ci prend la liste 
#des utilisateurs et les décompresses du format binaire (à leur format original) pour les ajouter à une liste : 'userList' laquel peut-être utilisé
def decodeBuffUsersList(datagram):
    userListDatagram = datagram[4:]
    userList = []
    k = 0
    while k < len(userListDatagram):
        lenUserName = userListDatagram[k]
        k = k + 1
        status = userListDatagram[k]
        k = k + 1
        userName = str(struct.unpack('!{0}s'.format(lenUserName), userListDatagram[k : k + lenUserName])[0], 'utf-8')
        userList.append(tuple((userName, status)))
        k = k + lenUserName
    return userList

# Numéro 7 : prepareBuffChatMessage est une fonction qui prend le message envoyé par un utilisateur et son nom associé, qui le transforme en format binaire
# et qui renvoie un paquet binaire composé du nom, de la longeur du nom et du message de l'utilisateur
def prepareBuffChatMessage(userName, message):
    lenUserName = len(userName)
    buffLenUserName = struct.pack('!B', lenUserName)
    buffUserName = struct.pack('!{0}s'.format(len(userName)), userName.encode('utf-8'))
    buffMessage =  struct.pack('!{0}s'.format(len(message)), message.encode('utf-8'))
    buff = buffLenUserName + buffUserName + buffMessage
    return buff
        
# Numéro 8 : decodeBuffChatMessage est une fonction qui prend en argument l'ensemble des données reçues, ils décompressent ces données (message et nom de l'utilisateur)du binaire-> au string 
#et le retourne au serveur qui après va l'afficher dans l'espace chat des main et video room  
def decodeBuffChatMessage(datagram):
    chatMessageDatagram = datagram[4:]

    lenUserName = chatMessageDatagram[0]
    userName = str(struct.unpack('!{0}s'.format(lenUserName), chatMessageDatagram[1:1 + lenUserName])[0], 'utf-8')
    message = str(struct.unpack('!{0}s'.format(len(chatMessageDatagram[lenUserName + 1:])), chatMessageDatagram[1 + lenUserName:])[0], 'utf-8')
    return (userName, message)
    

        
        
    




    
               
            
