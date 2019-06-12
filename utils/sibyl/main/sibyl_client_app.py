# -*- coding: utf-8 -*-
from gi.repository import Gtk
from .sibyl_controller import SibylGuiController
import logging

moduleLogger = logging.getLogger('sibyl_client.sibyl_client_application')


class SibylClientApplication(Gtk.Application):
    def __init__(self, protocolName, usingUdp, serverHost, serverPort):
        """
        The application class for the client.  The main of the client
        instantiates the only instance of this class.
        """

        self.usingUdp = usingUdp
        self.protocolName = protocolName
        self.serverHost = serverHost
        self.serverPort = serverPort
        Gtk.Application.__init__(self)

    def do_activate(self):
        self.sibylController = SibylGuiController(self.protocolName,
                                                  self.usingUdp,
                                                  self.serverHost,
                                                  self.serverPort, self)

    def do_startup(self):
        Gtk.Application.do_startup(self)
