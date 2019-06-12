#!/usr/bin/env python
"""
The Server Module
=================
This module contains the main function of the server.  It supports the
following command line options:

.. program:: c2w_server

.. cmdoption:: -p port_number, --port-number port_number

   The port number on which the server will be listening.  The default
   value is 8888.

.. cmdoption:: -n, --no-video

   The server will disable video streaming if this option is present on the
   command line.

.. cmdoption:: -e, --debug

   The server will print extra debugging messages if this option is present
   on the command line.

.. note::
   If there is a file named "c2w_movie_config" in the same directory as
   the Python server script, the server reads this file to determine the
   available    movies, including their title, path to the video file,
   multicast IP address and corresponding port number for streaming.  See
   the source file and the configuration file for more details.

The main function instantiates the factory for the chat server protocol,
which is the only instance of the class :py:class:\
`~c2w_main.c2w_chat_server_protocol_factory.c2wChatServerProtocolFactory`.
"""
import argparse
import importlib
import traceback
import logging
import os
import sys
from c2w.main.chat_server_protocol_factory import c2wChatServerProtocolFactory
from c2w.main.server_model import c2wServerModel
from c2w.main.server_proxy import c2wServerProxy

sys.dont_write_bytecode = True

# in order to use gstreamer we need a glib reactor
try:
    from twisted.internet import gireactor
    from twisted.internet import error
except ImportError:
    print("IMPORT_ERROR: Unable to import the module twisted")
    sys.exit(1)
try:
    gireactor.install()
except error.ReactorAlreadyInstalledError:
    if os.environ['sphinx_active'] == '1':
        print('ignoring reactor error because we are running sphinx')
    else:
        print("FATAL ERROR: Unable to install the gireactor in the server")

from twisted.internet import reactor

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject
from gi.repository import Gst
#from gi.repository import GstVideo

GObject.threads_init()
Gst.init(None)

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.c2w_server')


#~ def buildServerArgParser():
    #~ """
    #~ Function needed by the sphinx-argparse module to automatically
    #~ generate the sphinx documentation based on the command line options.
    #~ Note that we're not currently using this extension, it was just a test
    #~ and the results were not satisfactory.
    #~ """
    #~ parser = argparse.ArgumentParser(description='c2w Server')
    #~ parser.add_argument('-p', '--port',
                        #~ dest='port',
                        #~ help='The port number to bind to.',
                        #~ type=int, default=1900)
    #~ parser.add_argument('-l', '--loss-pr',
                        #~ dest='lossPr',
                        #~ help='The packet loss probability for outgoing ' +
                        #~ 'packets (used only for the UDP-based protocol!).',
                        #~ type=float, default=0)
    #~ parser.add_argument('-n', '--no-video',
                        #~ dest='noVideoFlag',
                        #~ help='Do not use the video part.',
                        #~ action="store_true", default=False)
    #~ parser.add_argument('-s', '--stream-video',
                        #~ dest='streamVideoFlag',
                        #~ help='Enable sending the video stream to other ' +
                        #~ 'computers (if this option is not given, only ' +
                        #~ 'on the local machine will be able to receive the ' +
                        #~ 'video stream).',
                        #~ action="store_true", default=False)
    #~ parser.add_argument('-P', '--protocol',
                        #~ dest='protocol',
                        #~ help='The name of the protocol class to be used.',
                        #~ action='store',
                        #~ default=os.environ.get('C2W_SERVER_PROTOCOL', None))
    #~ parser.add_argument('-u', '--udp',
                        #~ dest='udpFlag',
                        #~ help='Use UDP rather than TCP.',
                        #~ action="store_true",
                        #~ default=False)
    #~ parser.add_argument('-e', '--debug',
                        #~ dest='debugFlag',
                        #~ help='Raise the log level to debug.',
                        #~ action="store_true",
                        #~ default=False)
    #~ return parser




def C2wStart(protocolChoice,          # 'UDP' or TCP'
             port,
             noVideoFlag,
             streamVideoFlag,
             debugFlag, 
             lossPr):
               
    logging.basicConfig()
    log = logging.getLogger('c2w.c2w_main.server')
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)

    if debugFlag:
        log.setLevel(logging.DEBUG)
        logC2w = logging.getLogger('c2w')
        logC2w.setLevel(logging.DEBUG)

    udpFlag = False        
    if(protocolChoice == 'UDP'):
        udpFlag = True
        protocol = 'c2w.protocol.udp_chat_server.c2wUdpChatServerProtocol'
    elif(protocolChoice == 'TCP'):
        udpFlag = False
        protocol = 'c2w.protocol.tcp_chat_server.c2wTcpChatServerProtocol'
    else:
        moduleLogger.critical('Unsuported protcol. ' +
                              'Only UDP and TCP are supported by c2w')
        raise SystemExit


    protocol = protocol.strip()
    module = importlib.import_module(protocol.rsplit('.', 1)[0])
    protocolName = getattr(module, protocol.rsplit('.', 1)[1])

    log.info("importing module=%s, protocolName=%s", module, protocolName)

    serverPort = port
    serverModel = c2wServerModel()
    serverProxy = c2wServerProxy(serverModel)
    serverProxy.initMovieStore(streamVideoFlag, noVideoFlag)

    if port > 65536 or port <= 1500:
        log.error("MAIN_ERROR: Invalid port given (%s), the port number" +
                  "has to be between 1501 and 65536", options.port)
        raise SystemExit

    if udpFlag:
        log.info("MAIN_INFO: Server listening on UDP port %s", serverPort)
        serverProtocolInstance = protocolName(serverProxy, lossPr)
        reactor.listenUDP(serverPort, serverProtocolInstance)
    else:
        log.info("MAIN_INFO: Server listening on TCP port %s", serverPort)
        f = c2wChatServerProtocolFactory(protocolName, serverProxy)
        reactor.listenTCP(serverPort, f)
    log.info("MAIN_INFO: Starting the reactor")
    reactor.run()



#~ if __name__ == '__main__':
    #~ try:
        #~ main()
    #~ except Exception as e:
        #~ moduleLogger.critical('Caught an exception, aborting')
        #~ moduleLogger.critical('Exception: %s', e)
        #~ traceback.print_exc()
        #~ if reactor.running:
            #~ reactor.stop()
        #~ sys.exit()
