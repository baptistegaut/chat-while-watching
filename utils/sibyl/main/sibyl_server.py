#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import importlib
from twisted.internet import reactor
from sibyl.main.sibyl_brain import SibylBrain
from sibyl.main.sibyl_server_proxy import SibylServerProxy
from sibyl.main.sibyl_tcp_server_factory import SibylTcpSeverProtocolFactory


def SibylStart(protocol,          # 'UDP' or TCP'
               protocolType,      # 'text' or 'binary'
               server_port,
               debugFlag):

    """The main for the twisted Sibyl client"""
    # logging.basicConfig()
    log = logging.getLogger('sibyl_client')
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] [%(name)s] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)

    if server_port > 65536 or server_port <= 1500:
        print("Invalid port: the port number has to be between 1501 and 65536")
        exit(-1)

    if debugFlag:
        log.setLevel(logging.DEBUG)

    sibylBrain = SibylBrain()
    sibylServerProxy = SibylServerProxy(sibylBrain)

    usingUdp = False

    if(protocol == 'UDP'):
        usingUdp = True
        if(protocolType == 'text'):
            protocol = 'sibyl.protocol.sibyl_server_udp_text'
            protocol += '_protocol.SibylServerUdpTextProtocol'
            log.info('using the UDP text protocol')
        elif(protocolType == 'binary'):
            protocol = 'sibyl.protocol.sibyl_server_udp_bin'
            protocol += '_protocol.SibylServerUdpBinProtocol'
            log.info('using the UDP binary protocol')
        elif(protocolType == 'binary_timer'):
            protocol = 'sibyl.protocol.sibyl_server_timer_udp_bin'
            protocol += '_protocol.SibylServerTimerUdpBinProtocol'
            log.info('using the UDP binary protocol (timer version)')
    elif(protocol == 'TCP'):
        if(protocolType == 'text'):
            protocol = 'sibyl.protocol.sibyl_server_tcp_text'
            protocol += '_protocol.SibylServerTcpTextProtocol'
            log.info('using the TCP text protocol')
        elif(protocolType == 'binary'):
            protocol = 'sibyl.protocol.sibyl_server_tcp_bin'
            protocol += '_protocol.SibylServerTcpBinProtocol'
            log.info('using the TCP binary protocol')
    else:
        print("Invalid transport protocol: protocol has to be 'UDP' or 'TCP'")

    log.debug('module name=%s', str(protocol.rsplit('.', 1)[0]))
    log.debug('protocol name=%s', str(protocol.rsplit('.', 1)[1]))
    module = importlib.import_module(protocol.rsplit('.', 1)[0])
    protocolName = getattr(module, protocol.rsplit('.', 1)[1])
    log.debug("importing module=%s, protocol=%s", str(module),
              str(protocolName))

    if usingUdp:
        serverProtocolInstance = protocolName(sibylServerProxy)
        log.debug('protocol instance created')
        reactor.listenUDP(server_port, serverProtocolInstance)
        log.info('Server listening (UDP) on port %d', server_port)
    else:
        reactor.listenTCP(server_port,
                          SibylTcpSeverProtocolFactory(protocolName,
                                                       sibylServerProxy))
        log.info('Server listening (TCP) on port %d', server_port)
    log.info("MAIN_INFO: Starting the reactor")
    reactor.run()
