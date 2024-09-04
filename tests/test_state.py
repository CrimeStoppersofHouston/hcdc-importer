'''
    Test suite for state classes which control program execution
'''

import unittest

from config.states import FileStateHolder, ProgramStateHolder, FileStates, ProgramStates


class TestStateHolders(unittest.TestCase):
    '''Tests functionality of state holders'''
    def setUp(self):
        self.fstate = FileStateHolder()
        self.pstate = ProgramStateHolder()

    def test_set_get_state(self):
        '''Tests setters and getters'''
        self.fstate.set_state(FileStates.END)
        self.assertEqual(self.fstate.get_state(), FileStates.END)

        self.pstate.set_state(ProgramStates.END)
        self.assertEqual(self.pstate.get_state(), ProgramStates.END)

    def test_state_exclusivity(self):
        '''Tests that states cannot be used interchangeably'''
        try:
            self.fstate.set_state(ProgramStates.END)
            self.assertEqual(1, 0, "File state exclusivity violated!")
        except Exception as e:
            self.assertIsInstance(e, ValueError)
        
        try:
            self.pstate.set_state(FileStates.END)
            self.assertEqual(1, 0, "Program state exclusivity violated!")
        except Exception as e:
            self.assertIsInstance(e, ValueError)