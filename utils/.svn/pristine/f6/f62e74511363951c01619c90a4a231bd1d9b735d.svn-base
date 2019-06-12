import sys

sys.dont_write_bytecode = True
from gi.repository import Gtk

from .controller import c2wController


class c2wClientApp(Gtk.Application):
    def __init__(self, protocolName, udpFlag, lossPr):
        """
        :param protocol: The *name* of the protocol class.
        :type protocol: string
        :param lossPr: The loss probability for outgoing packets (used only
                with the UDP version of the protocol).
        :type lossPr: float

        The application class for the client.  The main of the client
        instantiates the only instance of this class.
        """
        self.protocolName = protocolName
        self.udpFlag = udpFlag
        self.lossPr = lossPr
        Gtk.Application.__init__(self)

    def do_activate(self):
        # FIXME XXXXXXXX
        # probably here we should tell the controller to show the
        # login window
        #self.main_win = MainWindow(self)
        #self.main_win.show_all()
        self.c2wController = c2wController(self.protocolName, self,
                                           self.udpFlag, self.lossPr)

    def do_startup(self):
        Gtk.Application.do_startup(self)
