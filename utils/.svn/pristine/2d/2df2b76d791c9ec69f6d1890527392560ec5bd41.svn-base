import os
import logging

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gtk
# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11
from gi.repository import GstVideo

from twisted.internet import reactor

from c2w.main.constants import ROOM_IDS
from c2w.main.gst_pipeline import c2wGstClientPipeline
import sys

sys.dont_write_bytecode = True
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.view')


class c2wLoginWindow(Gtk.ApplicationWindow):
    """
    The class for the c2w login window.
    """

    def __init__(self, app, controller):
        Gtk.Window.__init__(self, title="c2w Login",
                            application=app)
        self.set_default_size(75, 300)
        self.set_border_width(10)
        self.set_title("c2w Login")
        self.controller = controller
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.statusicon.set_visible(True)
        self.set_icon_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=10,
                             row_spacing=10)
        self.add(self.grid)

        self.loginButton = Gtk.Button("Login")
        self.serverNameLabel = Gtk.Label("Sever Name (or IP address)")
        self.serverNameLabel.set_justify(Gtk.Justification.RIGHT)
        self.serverPortLabel = Gtk.Label("Sever Port Number")
        self.serverPortLabel.set_justify(Gtk.Justification.RIGHT)
        self.userNameLabel = Gtk.Label("User Name")
        self.userNameLabel.set_justify(Gtk.Justification.RIGHT)
        self.serverNameEntry = Gtk.Entry()
        self.serverNameEntry.set_text("127.0.0.1")
        self.serverPortEntry = Gtk.Entry()
        self.serverPortEntry.set_text("1950")
        self.userNameEntry = Gtk.Entry()
        self.userNameEntry.set_text("alice")
        self.c2w_image = Gtk.Image.new_from_file(
                                    os.path.join(os.path.dirname(__file__),
                                    'Images/ChatWhileWatching.png'))
        # Attach widgets to the grid
        self.grid.attach(self.c2w_image, 0, 0, 2, 1)
        self.grid.attach_next_to(self.serverNameLabel,
                                 self.c2w_image,
                                 Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.serverNameEntry,
                                 self.serverNameLabel,
                                 Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.serverPortLabel,
                                 self.serverNameLabel,
                                 Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.serverPortEntry,
                                 self.serverPortLabel,
                                 Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.userNameLabel,
                                 self.serverPortLabel,
                                 Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.userNameEntry,
                                 self.userNameLabel,
                                 Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.loginButton,
                                 self.userNameEntry,
                                 Gtk.PositionType.BOTTOM, 1, 1)

        self.loginButton.connect("clicked", self.onLoginClicked)
        self.connect("destroy", lambda x: reactor.stop())
        self.loginButton.grab_focus()

    def onLoginClicked(self, widget):
        serverName = self.serverNameEntry.get_text()
        serverPortString = self.serverPortEntry.get_text()
        userName = self.userNameEntry.get_text()

        if len(serverName) == 0:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.OK,
                                       "You must specify the server name")
            dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()
            return
        if len(userName) == 0:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.OK,
                                       "You must specify the user name")
            dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()
            return
        try:
            serverPort = int(serverPortString)
        except ValueError:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.OK,
                                       "The server port must be an integer")
            dialog.format_secondary_text("")
            dialog.run()
            self.serverPortEntry.set_text('')
            dialog.destroy()
            return
        if serverPort > 65536 or serverPort <= 1500:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.OK,
                                       "The server port must be between " +
                                       "1500 and 65535")
            dialog.format_secondary_text("")
            dialog.run()
            self.serverPortEntry.set_text('')
            dialog.destroy()
            return
        moduleLogger.info("VIEW: server name=%s", serverName)
        moduleLogger.info("VIEW: server port number=%s", serverPort)
        moduleLogger.info("VIEW: local user name=%s", userName)
        self.controller.setThisUserName(userName)
        self.controller.loginRequest(serverName, serverPort, userName)


class c2wConnectionErrorWindow(Gtk.ApplicationWindow):
    """
    Class for the connection error window of the c2w application.
    """
    def __init__(self, app, controller):
        Gtk.Window.__init__(self, title="Connection Error",
                            application=app)
        self.set_default_size(400, 5)
        self.set_border_width(20)
        #self.set_title("c2w Connecting")
        self.controller = controller
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.statusicon.set_visible(True)
        self.set_icon_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.label = Gtk.Label("Connection Error, make sure the server is" +
                           "running and that the address and port values" +
                           " are correct.")
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_line_wrap(True)
        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=10,
                             row_spacing=50)
        self.add(self.grid)
        self.grid.attach(self.label, 0, 0, 1, 1)
        self.okButton = Gtk.Button('OK')
        self.grid.attach(self.okButton, 0, 2, 1, 1)
        self.connect("destroy", lambda x: reactor.stop())
        self.okButton.connect("clicked", self.onOkClicked)

    def onOkClicked(self, widget):
        self.controller.connectionErrorUserDone()


class c2wConnectionRejectedWindow(Gtk.ApplicationWindow):
    """
    Class for the connection error window of the c2w application.
    """
    def __init__(self, app, controller):
        Gtk.Window.__init__(self, title='Connection Rejected',
                            application=app)
        self.set_default_size(400, 5)
        self.set_border_width(20)
        #self.set_title("c2w Connecting")
        self.controller = controller
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.statusicon.set_visible(True)
        self.set_icon_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.label = Gtk.Label("Connection Error, make sure the server is" +
                           "running and that the address and port values" +
                           " are correct.")
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_line_wrap(True)
        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=10,
                             row_spacing=50)
        self.add(self.grid)
        self.grid.attach(self.label, 0, 0, 1, 1)
        self.okButton = Gtk.Button('OK')
        self.grid.attach(self.okButton, 0, 2, 1, 1)
        self.connect('destroy', lambda x: reactor.stop())
        self.okButton.connect('clicked', self.onOkClicked)

    def onOkClicked(self, widget):
        self.controller.connectionRejectedUserDone()


class c2wSpinningWindow(Gtk.ApplicationWindow):
    """
    Class for the "spinning window" of the c2w application.
    """
    def __init__(self, app, controller):
        Gtk.Window.__init__(self, title="Connecting",
                            application=app)
        self.set_default_size(200, 100)
        self.set_border_width(10)
        #self.set_title("c2w Connecting")
        self.controller = controller
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.statusicon.set_visible(True)
        self.set_icon_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.label = Gtk.Label("Trying to connect, please wait.")
        self.spinner = Gtk.Spinner()

        self.table = Gtk.Table(3, 2, True)
        self.table.attach(self.label, 0, 2, 0, 1)
        self.table.attach(self.spinner, 0, 2, 2, 3)
        self.add(self.table)

        self.connect("destroy", lambda x: reactor.stop())
        self.connect("show", self.startSpin)
        self.connect("hide", self.stopSpin)

    def startSpin(self, widget):
        self.spinner.start()

    def stopSpin(self, widget):
        self.spinner.stop()


class c2wMainRoomWindow(Gtk.ApplicationWindow):
    """
    Class for the the "Main Window" of the c2w application.
    """

    def __init__(self, app, controller):
        Gtk.Window.__init__(self, title='c2w Main Room', application=app)
        self.set_default_size(1200, 600)
        self.set_border_width(10)
        self.controller = controller
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.statusicon.set_visible(True)
        self.set_icon_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=10,
                             row_spacing=10)
        self.add(self.grid)

        self.joinMovieButton = Gtk.Button('Watch')
        self.leaveButton = Gtk.Button('Leave')
        self.sendChatMsgButton = Gtk.Button('Send')
        self.chatMessageEntry = Gtk.Entry()

        self.mainRoomChatText = self.createTextview()
        #stuff for the user list
        self.mainRoomUserListColNames = ['Status', 'User Name']
        self.mainRoomUserListStore = self.controller.getMainRoomUserListStore()
        self.mainRoomUserListView = Gtk.TreeView(self.mainRoomUserListStore)
        # for each column
        for i in range(len(self.mainRoomUserListColNames)):
            # cellrenderer to render the text
            cell = Gtk.CellRendererText()
            # the column is created
            col = Gtk.TreeViewColumn(self.mainRoomUserListColNames[i],
                                     cell, text=i)
            # and it is appended to the treeview
            self.mainRoomUserListView.append_column(col)
        userSelection = self.mainRoomUserListView.get_selection()
        userSelection.set_mode(Gtk.SelectionMode.NONE)
        # Movie list
        self.mainRoomMovieListColNames = ['Movie Title']
        self.mainRoomMovieListStore = \
            self.controller.getMainRoomMovieListStore()
        self.mainRoomMovieListView = Gtk.TreeView(self.mainRoomMovieListStore)
        # for each column
        for i in range(len(self.mainRoomMovieListColNames)):
            # cellrenderer to render the text
            cell = Gtk.CellRendererText()
            # the column is created
            col = Gtk.TreeViewColumn(self.mainRoomMovieListColNames[i], cell,
                                     text=i)
            # and it is appended to the treeview
            self.mainRoomMovieListView.append_column(col)
        movieSelection = self.mainRoomMovieListView.get_selection()
        movieSelection.set_mode(Gtk.SelectionMode.SINGLE)
        # Attach widgets to the grid
        self.grid.attach(self.mainRoomMovieListView, 0, 0, 3, 2)
        self.grid.attach_next_to(self.mainRoomUserListView,
                                 self.mainRoomMovieListView,
                                 Gtk.PositionType.RIGHT, 2, 6)
        self.grid.attach_next_to(self.mainRoomChatText,
                                 self.mainRoomMovieListView,
                            Gtk.PositionType.BOTTOM, 3, 2)
        self.grid.attach_next_to(self.chatMessageEntry, self.mainRoomChatText,
                                 Gtk.PositionType.BOTTOM, 2, 1)
        self.grid.attach_next_to(self.sendChatMsgButton,
                                 self.chatMessageEntry,
                                 Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.joinMovieButton,
                                 self.mainRoomUserListView,
                                 Gtk.PositionType.BOTTOM,
                                 1, 1)
        self.grid.attach_next_to(self.leaveButton,
                                 self.joinMovieButton,
                                 Gtk.PositionType.RIGHT,
                                 1, 1)

        self.sendChatMsgButton.connect("clicked", self.onSendChatMsgClicked)
        self.joinMovieButton.connect("clicked", self.onJoinMovieClicked)
        self.leaveButton.connect("clicked", self.onLeaveClicked)

        self.chatMessageEntry.connect("activate", self.onSendChatMsgClicked)
        self.connect("destroy", lambda x: reactor.stop())

    def createTextview(self):
        chatWindow = Gtk.ScrolledWindow()
        chatWindow.set_hexpand(True)
        chatWindow.set_vexpand(True)
        chatWindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                              Gtk.PolicyType.AUTOMATIC)

        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textbuffer = self.textview.get_buffer()
        chatWindow.add(self.textview)
        return chatWindow

    def onSendChatMsgClicked(self, widget):
        moduleLogger.debug('Main Room Send Chat Message Button clicked.')
        msg = self.chatMessageEntry.get_text()
        msg += '\n'
        moduleLogger.debug("sending chat message: %s", msg)
        self.textbuffer.insert(
                self.textbuffer.get_end_iter(),
                self.controller.thisUserName + ': ' + msg)
        self.textview.scroll_to_iter(self.textbuffer.get_end_iter(), 0,
                                use_align=False, xalign=0.1, yalign=0.1)
        self.chatMessageEntry.set_text('')
        self.controller.sendChatMessageOIE(msg)

    def onJoinMovieClicked(self, widget):
        moduleLogger.debug('Main Room Join Movie Button clicked.')
        movieSelection = self.mainRoomMovieListView.get_selection()
        model, treeiter = movieSelection.get_selected()
        if treeiter is None:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.OK,
                                       "You must first select a movie")
            dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()
            return
        else:
            selectedMovieTitle = model[treeiter][0]
            moduleLogger.info('Selected Movie: %s', selectedMovieTitle)
            self.controller.sendJoinRoomRequestOIE(selectedMovieTitle)

    def onLeaveClicked(self, widget):
        moduleLogger.debug('Main Room Leave Button clicked.')
        self.controller.sendLeaveSystemRequestOIE()

    def displayChatMessage(self, remoteUserName, msg):
        """
        Called by the view to actually display the chat message.
        """
        self.textbuffer.insert(self.textbuffer.get_end_iter(),
                               remoteUserName + ': ' + msg)
        self.textview.scroll_to_iter(self.textbuffer.get_end_iter(), 0,
                                use_align=False, xalign=0.1, yalign=0.1)

    def hide(self):
        self.textbuffer.set_text('')
        Gtk.ApplicationWindow.hide(self)


class c2wMovieRoomWindow(Gtk.ApplicationWindow):
    """
    Class for the the "Movie Window" of the c2w application.
    """

    def __init__(self, app, controller):
        Gtk.Window.__init__(self, title='c2w Movie Room', application=app)
        self.set_default_size(1200, 600)
        self.set_border_width(10)
        self.controller = controller
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.statusicon.set_visible(True)
        self.set_icon_from_file(os.path.join(os.path.dirname(__file__),
                                      'Images/ChatWhileWatching.png'))
        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=10,
                             row_spacing=10)
        self.add(self.grid)

        self.pipeline = None
        self.videoArea = Gtk.DrawingArea()
        self.videoArea.set_hexpand(True)
        self.videoArea.set_vexpand(True)
        self.leaveButton = Gtk.Button('Leave')
        self.sendChatMsgButton = Gtk.Button('Send')
        self.chatMessageEntry = Gtk.Entry()

        self.movieRoomChatText = self.createTextview()
        #stuff for the user list
        self.movieRoomUserListColName = ['Users in the room:']
        self.movieRoomUserListStore = \
            self.controller.getMovieRoomUserListStore()
        self.movieRoomUserListView = Gtk.TreeView(self.movieRoomUserListStore)
        # for each column
        for i in range(len(self.movieRoomUserListColName)):
            # cellrenderer to render the text
            cell = Gtk.CellRendererText()
            # the column is created
            col = Gtk.TreeViewColumn(self.movieRoomUserListColName[i],
                                     cell, text=i)
            # and it is appended to the treeview
            self.movieRoomUserListView.append_column(col)
        userSelection = self.movieRoomUserListView.get_selection()
        userSelection.set_mode(Gtk.SelectionMode.NONE)

        # Attach widgets to the grid
        self.grid.attach(self.videoArea, 0, 0, 3, 2)
        self.grid.attach_next_to(self.movieRoomUserListView,
                                 self.videoArea,
                                 Gtk.PositionType.RIGHT, 2, 6)
        self.grid.attach_next_to(self.movieRoomChatText,
                                 self.videoArea,
                            Gtk.PositionType.BOTTOM, 3, 2)
        self.grid.attach_next_to(self.chatMessageEntry, self.movieRoomChatText,
                                 Gtk.PositionType.BOTTOM, 2, 1)
        self.grid.attach_next_to(self.sendChatMsgButton,
                                 self.chatMessageEntry,
                                 Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.leaveButton,
                                 self.movieRoomUserListView,
                                 Gtk.PositionType.BOTTOM,
                                 1, 1)

        self.sendChatMsgButton.connect("clicked", self.onSendChatMsgClicked)
        self.leaveButton.connect("clicked", self.onLeaveClicked)

        self.chatMessageEntry.connect("activate", self.onSendChatMsgClicked)
        self.connect("destroy", lambda x: reactor.stop())

    def buildPipeline(self, movieTitle):
        (dstIpAddress, rtpVideoRecvPort) = self.controller.getMovieAddrPort(
                                                                    movieTitle)
        self.pipeline = c2wGstClientPipeline(dstIpAddress, rtpVideoRecvPort)

    def on_error(self, bus, msg):
        """
        Method needed by Gst bus
        """
        moduleLogger.debug('on_error():', msg.parse_error())

    def on_sync_message(self, bus, msg):
        """
        Method needed by Gst bus
        """
        if msg.get_structure().get_name() == 'prepare-window-handle':
            msg.src.set_property('force-aspect-ratio', True)
            msg.src.set_window_handle(self.xid)

    def createTextview(self):
        chatWindow = Gtk.ScrolledWindow()
        chatWindow.set_hexpand(True)
        chatWindow.set_vexpand(True)

        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textbuffer = self.textview.get_buffer()
        chatWindow.add(self.textview)
        return chatWindow

    def onSendChatMsgClicked(self, widget):
        moduleLogger.debug('Movie Room Send Chat Message Button clicked.')
        msg = self.chatMessageEntry.get_text()
        msg += '\n'
        moduleLogger.debug("sending chat message: %s", msg)
        self.textbuffer.insert(
                self.textbuffer.get_end_iter(),
                self.controller.thisUserName + ': ' + msg)
        self.textview.scroll_to_iter(self.textbuffer.get_end_iter(), 0,
                                use_align=False, xalign=0.5, yalign=0.5)
        self.chatMessageEntry.set_text('')
        self.controller.sendChatMessageOIE(msg)

    def onLeaveClicked(self, widget):
        moduleLogger.debug('Movie Room Leave Button clicked.')
        self.controller.sendJoinRoomRequestOIE(ROOM_IDS.MAIN_ROOM)

    def displayChatMessage(self, remoteUserName, msg):
        """
        Called by the view to actually display the chat message.
        """
        self.textbuffer.insert(self.textbuffer.get_end_iter(),
                               remoteUserName + ': ' + msg)
        self.textview.scroll_to_iter(self.textbuffer.get_end_iter(), 0,
                                use_align=False, xalign=0.1, yalign=0.1)

    def hide(self):
        if self.pipeline is not None:
            self.pipeline.stop_video()
        self.textbuffer.set_text('')
        Gtk.ApplicationWindow.hide(self)


class c2wView(object):
    def __init__(self, appInstance, controller):
        self.controller = controller
        self.appInstance = appInstance
        # Initialize some useful variables
        self.spinningWindow = c2wSpinningWindow(appInstance, controller)
        self.loginWindow = c2wLoginWindow(appInstance, controller)
        self.connectionErrorWindow = c2wConnectionErrorWindow(appInstance,
                                                              controller)
        self.connectionRejectedWindow = c2wConnectionRejectedWindow(
                                                             appInstance,
                                                             controller)
        self.mainRoomWindow = c2wMainRoomWindow(appInstance, controller)
        self.movieRoomWindow = c2wMovieRoomWindow(appInstance, controller)
        self.currentWindow = self.loginWindow

    def chatReceivedMainWindow(self, remoteUserName, msg):
        """
        Display the chat message in the main window.
        """
        if self.currentWindow != self.mainRoomWindow:
            s = 'INTERNAL ERROR: chatReceivedMainWindow called in the view'
            s += 'when not in the main room'
            moduleLogger.critical(s)
            raise RuntimeError(s)
        else:
            self.mainRoomWindow.displayChatMessage(remoteUserName, msg)

    def chatReceivedMovieWindow(self, remoteUserName, msg):
        """
        Display the chat message in the main window.
        """
        if self.currentWindow != self.movieRoomWindow:
            s = 'INTERNAL ERROR: chatReceivedMovieWindow called in the view'
            s += 'when not in a movie room'
            moduleLogger.critical(s)
            raise RuntimeError(s)
        else:
            self.movieRoomWindow.displayChatMessage(remoteUserName, msg)

    def showLoginWindow(self):
        """
        Shows the login window.
        """
        self.currentWindow.hide()
        self.currentWindow = self.loginWindow
        self.loginWindow.show_all()
        self.loginWindow.loginButton.grab_focus()

    def showSpinningWindow(self, title, label):
        """
        Shows the spinning window.
        """
        self.currentWindow.hide()
        self.currentWindow = self.spinningWindow
        self.spinningWindow.set_title(title)
        self.spinningWindow.label.set_text(label)
        self.spinningWindow.show_all()

    def showConnectionErrorWindow(self):
        """
        Shows the connection error window.
        """
        moduleLogger.debug('showConnectionErrorWindow called, about to show ' +
                           'the error window.')
        self.currentWindow.hide()
        self.currentWindow = self.connectionErrorWindow
        self.connectionErrorWindow.show_all()

    def showConnectionRejectedWindow(self, msg):
        """
        Shows the connection error window.
        """
        self.currentWindow.hide()
        self.currentWindow = self.connectionRejectedWindow
        self.connectionRejectedWindow.label.set_text('Connection rejected: ' +
                                                     msg)
        self.connectionRejectedWindow.show_all()

    def showMainRoomWindow(self):
        """
        Shows the main room window.
        """
        self.currentWindow.hide()
        self.currentWindow = self.mainRoomWindow
        self.mainRoomWindow.set_title('c2w Main Room -- '
                                     + self.controller.thisUserName)
        self.mainRoomWindow.show_all()
        self.mainRoomWindow.chatMessageEntry.grab_focus()

    def showMovieRoomWindow(self):
        """
        Show the movie room window.
        """
        self.currentWindow.hide()
        self.currentWindow = self.movieRoomWindow
        # Build the gst pipeline
        self.movieRoomWindow.buildPipeline(self.controller.thisMovieRoom)
        self.movieRoomWindow.set_title('c2w Movie Room -- '
                                     + self.controller.thisMovieRoom + ' -- '
                                     + self.controller.thisUserName)
        self.controller.model.updateLocalUserRoom(
                                                self.controller.thisMovieRoom)
        self.movieRoomWindow.show_all()
        self.movieRoomWindow.pipeline.start_video(
                                            self.movieRoomWindow.videoArea)
        self.movieRoomWindow.chatMessageEntry.grab_focus()
