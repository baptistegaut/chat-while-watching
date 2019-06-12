"""
c2wConstants class
------------------

This module defines the constants used both in the server and in the
client to indicate the main room, a generic movie room and the 'special'
room corresponding to a user no longer connected (out of the system room).

These constants are represented as class names, which is a standard
way of representing 'constants' in Python.
"""
import sys

sys.dont_write_bytecode = True

class ROOM_IDS(object):
    """
    Class grouping all the constant values.
    """
    class MAIN_ROOM(object):
        """
        Class representing the main room.
        """
        pass

    class OUT_OF_THE_SYSTEM_ROOM(object):
        """
        Class representing a special room, used for users who have left
        the system.
        """
        pass

    class MOVIE_ROOM(object):
        """
        Class representing a generic movie room.
        """
        pass
