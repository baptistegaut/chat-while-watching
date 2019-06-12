# -*- coding: utf-8 -*-
import logging

moduleLogger = logging.getLogger('sibyl_client.sibyl_server_proxy')


class SibylServerProxy(object):
    """
    This class is the interface between the `SibylServerProtocol` and
    the Sibyl application (Sibyl Brain).

    .. warning::
        Your protocol implementation can interact with server only through this
        class.

    .. warning::
        Do no instantiate this class in your code.  This is already done in the
        code called by the main function.

    """
    def __init__(self, sibylBrain):
        moduleLogger.debug("SibyServerProxy constructor started")
        self.sibylBrain = sibylBrain

    def generateResponse(self, questionText):
        """Forward the question to the Sibyl Brain.

        Calls the
        :py:func:`~sibyl.main.sibyl_brain.SibylBrain.generateResponse`
        method of the :py:class:`~sibyl.main.sibyl_brain.SibylBrain` instance
        used by the server.

        Args:
            questionText (str): The text of the question.

        Returns:
            string: The text of the response.
        """

        return self.sibylBrain.generateResponse(questionText)
