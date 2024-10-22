'''
    This module contains the ProgressTracker class which
    gives a visual representation of the progress of
    execution.
'''

### External Imports ###

import math
from threading import Lock
import time

### Class Declarations ###

class Task:
    '''Holds the name, current progress, and total progress of a task'''
    def __init__(self, name: str, total_progress: int, current_progress: int = 0):
        self.name = name
        self.total_progress = total_progress
        self.current_progress = current_progress

    def set_progress(self, current_progress: int):
        '''Sets progress value of the Task'''
        self.current_progress = current_progress

    def add_progress(self, progression: int):
        '''Adds progress to progress value of the Task'''
        self.current_progress += progression


class ProgressTracker:
    '''Class that provide a visual representation of Task progress'''
    def __init__(
            self,
            name: str,
            progress_length: int= 20,
            bounding_symbol: str= '-',
            progress_symbol: str= '=',
            max_displayed_tasks: int = 7
        ):
        self.tasks = []
        self.name = name
        self.progress_length = progress_length
        self.bounding_symbol = bounding_symbol
        self.progress_symbol = progress_symbol
        self.max_displayed_tasks = max_displayed_tasks
        self.previous_height = 0
        self.previous_length = 0
        self.update_lock = Lock()
        self.clear_lock = Lock()

    def reset_to_top(self):
        '''Resets the cursor up lines equal to the previous height'''
        for i in range(self.previous_height):
            print("\r\033[1A", end='\r')

    def clear(self):
        '''Clears the previous lines equal to the previous height'''
        with self.clear_lock:
            for i in range(self.previous_height):
                print("\r\033[1A", end='\r')
                print(" "*self.previous_length, end='\r')

    def add_task(self, task: Task) -> None:
        '''Adds a task'''
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        '''Removes a task'''
        self.tasks.remove(task)

    def set_previous_height(self, height: int) -> None:
        '''Setter for the previous height'''
        self.previous_height = height

    def set_previous_length(self, length: int) -> None:
        '''Setter for the previous length'''
        self.previous_length = length

    def get_previous_height(self) -> int:
        '''Getter for the previous height'''
        return self.previous_height

    def get_previous_length(self) -> int:
        '''Getter for the previous length'''
        return self.previous_length

    def update(self, skip_clear: bool= False) -> None:
        '''
            Prints a representation of the tasks contained within. 
            Will skip clearing if skip_clear is True
        '''
        with self.update_lock:
            self.bounding_symbol = '-'
            item_bars = []
            max_length = 0
            overall_current_progress = 0
            overall_total_progress = 0
            if len(self.tasks) > self.max_displayed_tasks:
                item_bars.append(
                    f'{self.bounding_symbol} '
                    f'({len(self.tasks)-self.max_displayed_tasks}) additional tasks...'
                )
            for task in self.tasks[-self.max_displayed_tasks:]:
                progress = task.current_progress/task.total_progress
                progress_bar_length = math.floor(progress*self.progress_length)
                row = (
                    f'{self.bounding_symbol} {task.name}'
                    f' [{(self.progress_symbol*progress_bar_length).ljust(self.progress_length, '-')}]'
                    f' {progress*100:.2f}% ({task.current_progress}/{task.total_progress})'
                )
                item_bars.append(row)
                overall_current_progress += task.current_progress
                overall_total_progress += task.total_progress

            lines = []
            overall_progress_bar_length = math.floor(
                (overall_current_progress/overall_total_progress)*self.progress_length
            )

            lines.append(
                (
                    f'{self.bounding_symbol} {self.name}'
                    f' [{(overall_progress_bar_length*self.progress_symbol).ljust(self.progress_length, '-')}]'
                    f' {overall_current_progress/overall_total_progress*100:.2f}%'
                )
            )
            for index, row in enumerate(item_bars):
                lines.append(f'{row}')

            for line in lines:
                max_length = max(len(line), max_length)

            bounding_bar = f'{self.bounding_symbol*(max_length+2)}'

            output = f'{bounding_bar}\n'

            for line in lines:
                output += f'{line.ljust(max_length)} {self.bounding_symbol}\n'

            output += f'{bounding_bar}'

            if self.previous_height != 0 and not skip_clear:
                self.clear()
            print(f'{output}')
            self.set_previous_height(len(item_bars)+3)
            self.set_previous_length(max_length+2)
