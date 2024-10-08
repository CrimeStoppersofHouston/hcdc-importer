'''
    Test suite for progress tracker
'''

import unittest
from utility.progress_tracking import Task, ProgressTracker
import time

class TestProgressTracker(unittest.TestCase):

    def testTaskSetProg(self):
        t = Task('Sample Task 1', 100)
        t.set_progress(50)
        self.assertEqual(t.current_progress, 50)

    def testTaskAddProg(self):
        t = Task('Sample Task 1', 100)
        t.add_progress(10)
        self.assertEqual(t.current_progress, 10)
        t.add_progress(50)
        self.assertEqual(t.current_progress, 60)
    
    def testTrackerVisuals(self):
        t1 = Task('Sample Task 1', 100)
        t2 = Task('Sample Task 2', 200)

        tracker = ProgressTracker()
        tracker.add_task(t1)
        tracker.add_task(t2)
        tracker.update()
        for i in range(10):
            t1.add_progress(10)
            t2.add_progress(10)
            tracker.update()
            time.sleep(.1)