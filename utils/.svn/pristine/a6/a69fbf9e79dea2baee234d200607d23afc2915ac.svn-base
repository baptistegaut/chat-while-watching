# -*- coding: utf-8 -*-
import random


class SibylBrain(object):
    """
    This class implements the 'intelligence' of the system.  The Sibyl server
    has one instance of this class.  The protocol instance must use the
    :py:class:`~sibyl.main.sibyl_server_proxy.`has a reference to this instance
    so that it can call its
    :py:func:`~sibyl.main.sibyl_brain.SibylBrain.generateResponse` method.
    """
    def __init__(self, randomly=True):
        self.randomly = randomly
        self.responses = ["All work and no play makes Jack a dull boy",
                    "I've got a feeling we're not in Kansas anymore",
                    "People who live in glass houses should not throw stones",
                    "Two wrongs don't make a right"]

    def generateResponse(self, questionText):
        """Generates the response to the question.

        Args:
            questionText (str): The text of the question.

        Returns:
            string: The text of the response.
        """

        if self.randomly:
            return random.choice(self.responses)
        else:
            return self.responses[0]
