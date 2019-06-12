# -*- coding: utf-8 -*-
import os
import logging

import gi
from gi.repository import Gtk
from twisted.protocols.basic import LineReceiver


from twisted.internet import reactor

moduleLogger = logging.getLogger('sibyl_client.sibyl_view')


class SibylRequestWindow(Gtk.ApplicationWindow):
    """
    Class for the Sibyl request window
    """

    def __init__(self, app, controller):
        Gtk.Window.__init__(self, title="Sibyl (Request)",
                            application=app)
        self.set_default_size(75, 100)
        self.set_border_width(10)
        self.set_title("Sibyl (Request)")
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(os.path.join(os.path.dirname(__file__),
                                      'column.png'))
        self.statusicon.set_visible(True)
        self.set_icon_from_file(os.path.join(os.path.dirname(__file__),
                                      'column.png'))

        self.controller = controller
        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=2,
                             row_spacing=2)
        self.add(self.grid)

        self.sendRequestButton = Gtk.Button("Send Question")
        self.questionLabel = Gtk.Label("Your question for the Sibyl:")
        self.questionLabel.set_justify(Gtk.Justification.LEFT)
        self.questionEntry = Gtk.Entry()
        self.questionEntry.set_text('question')
        self.sibyl_image = Gtk.Image.new_from_file(
                                    os.path.join(os.path.dirname(__file__),
                                    'CumaeanSibylByMichelangelo.jpg'))
        # Attach widgets to the grid
        self.grid.attach(self.sibyl_image, 0, 0, 1, 5)
        self.grid.attach(self.questionLabel, 1, 0, 3, 1)
        self.grid.attach(self.questionEntry, 1, 1, 3, 1)
        self.grid.attach(self.sendRequestButton, 3, 4, 1, 1)

        self.sendRequestButton.connect("clicked", self.on_send_request_clicked)
        self.connect("destroy", lambda x: reactor.stop())
        self.sendRequestButton.grab_focus()

    def on_send_request_clicked(self, widget):
        questionText = self.questionEntry.get_text()
        moduleLogger.debug("VIEW: send request button clicked, question=%s",
                          questionText)
        self.controller.sendRequest(questionText)


class SibylResponseWindow(Gtk.ApplicationWindow):
    """
    Class for the Sibyl request window
    """

    def __init__(self, app, controller):
        Gtk.Window.__init__(self, title="Sibyl (Request)",
                            application=app)
        self.set_default_size(75, 100)
        self.set_border_width(10)
        self.set_title("Sibyl (Request)")
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(os.path.join(os.path.dirname(__file__),
                                      'column.png'))
        self.statusicon.set_visible(True)
        self.set_icon_from_file(os.path.join(os.path.dirname(__file__),
                                      'column.png'))

        self.controller = controller
        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=2,
                             row_spacing=2)
        self.add(self.grid)

        self.okButton = Gtk.Button("OK")
        self.responseLabel = Gtk.Label("The response of the Sibyl is:")
        self.responseLabel.set_justify(Gtk.Justification.LEFT)
        self.responseEntry = Gtk.Entry()
        self.responseEntry.set_editable(False)
        self.responseEntry.set_text('')
        self.responseEntry.set_property("editable", False)
        self.responseEntry.set_property('can_focus', False)
        self.responseEntry.set_property('has_frame', False)
        self.sibyl_image = Gtk.Image.new_from_file(
                                    os.path.join(os.path.dirname(__file__),
                                    'CumaeanSibylByMichelangelo.jpg'))
        # Attach widgets to the grid
        self.grid.attach(self.sibyl_image, 0, 0, 1, 5)
        self.grid.attach(self.responseLabel, 1, 0, 3, 1)
        self.grid.attach(self.responseEntry, 1, 1, 3, 1)
        self.grid.attach(self.okButton, 3, 4, 1, 1)

        self.okButton.connect("clicked", self.on_ok_clicked)
        self.connect("destroy", lambda x: reactor.stop())
        self.okButton.grab_focus()

    def on_ok_clicked(self, widget):
        moduleLogger.debug("VIEW: OK button clicked")
        reactor.stop()

    def setResponse(self, response):
        self.responseEntry.set_text(response)


class SibylSpinningWindow(Gtk.ApplicationWindow):
    """
    Class for the "spinning window" for the Sibyl application.
    """
    def __init__(self, app, controller, title, message):
        Gtk.Window.__init__(self, title=title,
                            application=app)
        self.set_default_size(200, 100)
        self.set_border_width(10)
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(os.path.join(os.path.dirname(__file__),
                                      'column.png'))
        self.statusicon.set_visible(True)
        self.set_icon_from_file(os.path.join(os.path.dirname(__file__),
                                      'column.png'))
        self.controller = controller

        self.label = Gtk.Label(message)
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

    def setMessageTitle(self, text):
        self.set_title(text)
        self.label.set_text(text)


class SibylErrorWindow(Gtk.ApplicationWindow):
    """
    Class for the error window for the Sibyl application.
    """
    def __init__(self, app, controller, title, message):
        Gtk.Window.__init__(self, title=title,
                            application=app)
        self.set_default_size(400, 5)
        self.set_border_width(20)
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(os.path.join(os.path.dirname(__file__),
                                      'column.png'))
        self.statusicon.set_visible(True)
        self.set_icon_from_file(os.path.join(os.path.dirname(__file__),
                                      'column.png'))
        self.controller = controller
        self.label = Gtk.Label(message)
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
        self.okButton.connect("clicked", self.on_OK_clicked)

    def on_OK_clicked(self, widget):
        self.controller.sibylErrorUserDone()

    def setMessageTitle(self, text):
        self.set_title(text)
        self.label.set_text(text)


class SibylView(object):
    def __init__(self, appInstance, controller):
        self.controller = controller
        self.appInstance = appInstance
        # Initialize some useful variables
        self.spinningWindow = SibylSpinningWindow(appInstance, controller,
                                        'Please Wait', 'Please wait.')
        self.requestWindow = SibylRequestWindow(appInstance, controller)
        self.errorMsgWindow = SibylErrorWindow(appInstance, controller,
                                               'Error', 'Error')
        self.responseWidnow = SibylResponseWindow(appInstance, controller)
        self.currentWindow = self.requestWindow

    def showRequestWindow(self):
        """
        Shows the request window.
        """
        self.currentWindow.hide()
        self.currentWindow = self.requestWindow
        self.requestWindow.show_all()
        self.requestWindow.sendRequestButton.grab_focus()

    def showResponseWindow(self, response):
        """
        Shows the response window.
        """
        self.currentWindow.hide()
        self.currentWindow = self.responseWidnow
        self.responseWidnow.setResponse(response)
        self.responseWidnow.show_all()
        self.responseWidnow.okButton.grab_focus()

    def showSpinningWindow(self, title, label):
        """
        Shows the spinning window.
        """
        self.currentWindow.hide()
        self.currentWindow = self.spinningWindow
        self.spinningWindow.set_title(title)
        self.spinningWindow.label.set_text(label)
        self.spinningWindow.show_all()

    def showErrorWindow(self, title, label):
        """
        Shows the error window.
        """
        self.currentWindow.hide()
        self.currentWindow = self.errorMsgWindow
        self.errorMsgWindow.set_title(title)
        self.errorMsgWindow.label.set_text(label)
        self.errorMsgWindow.show_all()


class TextInterface(LineReceiver):
    """A simple protocol class for input/output"""

    def __init__(self, controller):
        """
        :param controller: the controller of the Sibyl client.
        """
        self.promptString = ">>> "
        self.delimiter = os.linesep
        self.controller = controller

    def connectionMade(self):
        self.sendLine("Please type your question for the Sibyl:")
        self.transport.write(self.promptString)

    def lineReceived(self, line):
        self.transport.write('Request sent, waiting for the response ...\n')
        self.controller.sendRequest(line)

    def responseReceived(self, responseText):
        self.transport.write('The response of the Sibyl is: \n' +
                             responseText + '\n' + os.linesep)
        #self.transport.loseConnection()
        #reactor.stop()

    def displayErrorMessage(self, message):
        self.transport.write(message)
