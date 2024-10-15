'''
    Test suite for progress tracker
'''

import unittest
import time
from utility.progress_tracking import Task, ProgressTracker


class TestProgressTracker(unittest.TestCase):
    '''Test suite for the ProgressTracker and Task classes'''

    def test_task_set_prog(self):
        '''Tests setting progress of a Task'''
        t = Task('Sample Task 1', 100)
        t.set_progress(50)
        self.assertEqual(t.current_progress, 50)

    def test_task_add_prog(self):
        '''Tests adding progress to a Task'''
        t = Task('Sample Task 1', 100)
        t.add_progress(10)
        self.assertEqual(t.current_progress, 10)
        t.add_progress(50)
        self.assertEqual(t.current_progress, 60)

    def test_tracker_visuals(self):
        '''Visual demo of Progress Tracker at work'''
        t1 = Task('Sample Task 1', 100)
        t2 = Task('Sample Task 2', 200)

        tracker = ProgressTracker('Sample')
        tracker.add_task(t1)
        tracker.add_task(t2)
        tracker.update()
        for i in range(5):
            t1.add_progress(10)
            t2.add_progress(10)
            tracker.update()
            time.sleep(.1)
        t3 = Task('Sample Task 3', 400)
        tracker.add_task(t3)
        for i in range(5):
            t1.add_progress(10)
            t2.add_progress(10)
            t3.add_progress(10)
            tracker.update()
            time.sleep(.1)
        tracker.remove_task(t1)
        for i in range(10):
            t2.add_progress(10)
            t3.add_progress(10)
            tracker.update()
            time.sleep(.1)
        time.sleep(1)
        tracker.clear()
