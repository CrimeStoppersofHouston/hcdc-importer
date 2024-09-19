'''
    This module contains the ProgressTracker class which
    gives a visual representation of the progress of
    execution.
'''

class ProgressTracker:
    '''
        Singleton class which provides a visual representation
        of the progress of execution
    '''
    # Singleton instance to avoid creating multiple instances
    @classmethod
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ProgressTracker, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.tasks = []
        pass