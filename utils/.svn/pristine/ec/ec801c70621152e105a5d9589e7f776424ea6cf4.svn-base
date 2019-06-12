#!/usr/bin/env python2.7
"""
The Client Module
=================
This module contains the main function of the client.  It supports the
following command line option:

.. program:: c2w_client

.. cmdoption:: -e, --debug

   The client will print extra debugging messages if this option is present
   on the command line.

The client uses a Model-View-Controller pattern. The model is in
the :py:mod:`~c2w_main.c2w_model` module.  The view is in the
:py:mod:`~c2w_main.c2w_view` module and controller is in the
:py:mod:`~c2w_main.c2w_controller` module.
The class :py:class:`~c2w_main.c2w_client_proxy.c2wClientProxy` is the
interface between the controller (and hence the graphical user interface)
and the protocol that is implemented by the |c2wChatClientProtocolClass|
(which you have to write).

The main function of the client instantiates the c2w application (instance of
the c2wClientApp), which then instantiates the controller.  Finally, the
controller instantiates the view, the model and the c2wClientProxy.
"""


import gi
import traceback
gi.require_version('Gst', '1.0')
from gi.repository import GObject
from gi.repository import Gst
from gi.repository import Gtk
# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11
from gi.repository import GstVideo
from gi.repository import Pango

import argparse
import sys

sys.dont_write_bytecode = True

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

from c2w.main.client_app import c2wClientApp

# The following three lines can be used to debug the gst pipeline
import os
os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp"
os.putenv('GST_DEBUG_DUMP_DIR_DIR', '/tmp')

GObject.threads_init()
Gst.init(None)

import logging
import importlib

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.c2w_client')

def C2wStart(protocolChoice,          # 'UDP' or TCP'
             debugFlag, 
             lossPr):
    logging.basicConfig()
    log = logging.getLogger('c2w.main.c2wclient')
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)

    udpFlag = False        
    if(protocolChoice == 'UDP'):
        udpFlag = True
        protocol = 'c2w.protocol.udp_chat_client.c2wUdpChatClientProtocol'
    elif(protocolChoice == 'TCP'):
        udpFlag = False
        protocol = 'c2w.protocol.tcp_chat_client.c2wTcpChatClientProtocol'
    else:
        moduleLogger.critical('Unsuported protcol. ' +
                              'Only UDP and TCP are supported by c2w')
        raise SystemExit

    protocol = protocol.strip()
    module = importlib.import_module(protocol.rsplit('.', 1)[0])
    protocolName = getattr(module, protocol.rsplit('.', 1)[1])
    log.debug("MAIN_DEBUG: imported module=%s, protocol=%s", module, protocolName)

    if debugFlag:
        log.setLevel(logging.DEBUG)
        logC2w = logging.getLogger('c2w')
        logC2w.setLevel(logging.DEBUG)

    log.info("MAIN_INFO: Starting the c2wClientApp")
    c2wClientAppInstance = c2wClientApp(protocolName, udpFlag,
                                        lossPr)
    log.info("MAIN_INFO: Registering the c2wClientApp")
    reactor.registerGApplication(c2wClientAppInstance)
    log.info("MAIN_INFO: Starting the reactor")
    reactor.run()


#~ if __name__ == "__main__":
    #~ try:
        #~ main()
    #~ except Exception as e:
        #~ moduleLogger.critical('Caught an exception, aborting')
        #~ moduleLogger.critical('Exception: %s', e)
        #~ traceback.print_exc()
        #~ if reactor.running:
            #~ reactor.stop()
        #~ sys.exit()
