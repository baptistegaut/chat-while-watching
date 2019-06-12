#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import importlib

try:
    from twisted.internet import gtk3reactor  # for gtk-3.0
    try:
        gtk3reactor.install()
    except Exception as e:
        print("[*] ERROR: Could not initiate GTK modules: %s" % (e))
        sys.exit(1)
    from twisted.internet import reactor
except ImportError:
    print("[*] ERROR: Could not import Twisted Network Framework")
    sys.exit(1)

from .sibyl_client_app import SibylClientApplication
from .sibyl_controller import SibylTextInterfaceController


def SibylStart(protocol,  # 'UDP' or TCP'
               protocolType,  # 'text' or 'binary'
               port,  host,
               debugFlag):

    """The main for the twisted Sibyl client"""
    # logging.basicConfig()
    log = logging.getLogger('sibyl_client')
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] [%(name)s] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)

    if port > 65536 or port <= 1500:
        print("Invalid port: the port number has to be between 1501 and 65536")
        exit(-1)

    if debugFlag:
        log.setLevel(logging.DEBUG)

    usingUdp = False

    if(protocol == 'UDP'):
        usingUdp = True
        if(protocolType == 'text'):
            protocol = 'sibyl.protocol.sibyl_client_udp_text'
            protocol += '_protocol.SibylClientUdpTextProtocol'
        elif(protocolType == 'binary'):
            protocol = 'sibyl.protocol.sibyl_client_udp_bin'
            protocol += '_protocol.SibylClientUdpBinProtocol'
    elif(protocol == 'TCP'):
        if(protocolType == 'text'):
            protocol = 'sibyl.protocol.sibyl_client_tcp_text'
            protocol += '_protocol.SibylClientTcpTextProtocol'
        elif(protocolType == 'binary'):
            protocol = 'sibyl.protocol.sibyl_client_tcp_bin'
            protocol += '_protocol.SibylClientTcpBinProtocol'
    else:
        print("Invalid transport protocol: protocol has to be 'UDP' or 'TCP'")

    module = importlib.import_module(protocol.rsplit('.', 1)[0])
    protocolName = getattr(module, protocol.rsplit('.', 1)[1])
    log.debug("importing module=%s, protocol=%s", module, protocolName)

#    host = reactor.resolve(host)

    log.info("MAIN_INFO: Starting the SibylClientApp")
    sibylClientAppInstance = SibylClientApplication(protocolName,
                                                    usingUdp, host, port)
    log.info("MAIN_INFO: Registering the sibylClientApp")
    reactor.registerGApplication(sibylClientAppInstance)

    log.info("MAIN_INFO: Starting the reactor")
    reactor.run()
