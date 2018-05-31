"""
enigma2.error
~~~~~~~~~~~~~~~~~~~~

Module errors and exceptionss

Copyright (c) 2018 Ronan Murray <https://github.com/ronanmu>
Licensed under the MIT license.
"""

class Enigma2Error(Exception):

    """
    This exception is raised when there has occurred an error related to
    communication with Enigma2/OpenWebIf. It is a subclass of Exception.
    """

    def __init__(self, message='', original=None):
        Exception.__init__(self)
        self.message = message
        self.original = original
