# This file contains the class needed to set and
# read the execution state of the program. This class
# should remain small and leave more complicated
# responsibilities to other classes. More modes can be
# added at a later time.

### External Imports ###

from enum import Enum

### Class Declarations ###

class ExecutionState(Enum):
    currentState = 0
    INITIALIZATION = 0
    FILE = 1
    DIRECTORY = 2
    IMPORT = 3

    def setState(self, state):
        if state not in self:
            raise ValueError('Invalid state: %s' % state)
        self.currentState = state

    def getState(self):
        return self.currentState