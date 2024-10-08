'''
    This module contains the ProgressTracker class which
    gives a visual representation of the progress of
    execution.
'''

### External Imports ###

import logging
import math

### Class Declarations ###

class Task:
    def __init__(self, name: str, total_progress: int, current_progress: int = 0):
        self.name = name
        self.total_progress = total_progress
        self.current_progress = current_progress

    def set_progress(self, current_progress: int):
        self.current_progress = current_progress

    def add_progress(self, progression: int):
        self.current_progress += progression


class ProgressTracker:
    '''
        Singleton class which provides a visual representation
        of the progress of execution
    '''
    # Singleton instance to avoid creating multiple instances
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ProgressTracker, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.tasks = []
        self.name = 'Sample'
        self.progress_length = 20
        self.bounding_symbol = '-'
        self.progress_symbol = '='

    
#    def __init__(self, name: str, progress_length: int= 20, bounding_symbol: str= '-', progress_symbol: str= '='):
#        self.tasks = []
#        self.name = name
#        self.progress_length = progress_length
#        self.bounding_symbol = bounding_symbol
#        self.progress_symbol = progress_symbol
#    '''

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def update(self) -> None:
        self.bounding_symbol = '-'
        item_bars = []
        max_length = 0
        overall_current_progress = 0
        overall_total_progress = 0

        for task in self.tasks:
            progress = task.current_progress/task.total_progress
            progress_bar_length = math.floor(progress*self.progress_length)
            row = f'{self.bounding_symbol} {task.name} [{(self.progress_symbol*progress_bar_length).ljust(self.progress_length, '-')}] {progress*100:.2f}% ({task.current_progress}/{task.total_progress})'
            item_bars.append(row)
            overall_current_progress += task.current_progress
            overall_total_progress += task.total_progress
            if len(row) > max_length:
                max_length = len(row)

        bounding_bar = f'{self.bounding_symbol*(max_length+2)}'
        overall_progress_bar_length = math.floor((overall_current_progress/overall_total_progress)*self.progress_length)
        output = f'{bounding_bar}\n{self.bounding_symbol} {self.name} [{(overall_progress_bar_length*self.bounding_symbol).ljust(self.progress_length, '-')}]'.ljust(max_length)
        output += '\n'
        for index, row in enumerate(item_bars):
            output += f'{row.ljust(max_length)} {self.bounding_symbol}\n'
        output += f'{bounding_bar}'
        print(f'{output}', end='\r')