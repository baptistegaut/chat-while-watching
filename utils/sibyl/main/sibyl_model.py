# -*- coding: utf-8 -*-
"""
The sibyl_model Module
===================
"""

import logging

moduleLogger = logging.getLogger('sibyl_client.sibyl_model')


class SibylModel(object):
    """
    The model for the Sibyl client, that is just the question sent!

    """
    def __init__(self):
        self.questionText = ''

    def setQuestionText(self, text):
        """
        Set the question text.
        """
        self.questionText = text

    def getQuestionText(self):
        return self.questionText
