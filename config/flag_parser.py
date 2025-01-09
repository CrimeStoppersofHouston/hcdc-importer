'''
    This module contains the singleton instance of
    the flag parser. This is to avoid using multiple
    instances for the same program call.
'''

### External Imports ###

import argparse

### Class Declarations ###


class FlagParser(argparse.ArgumentParser):
    '''
    Handles collection and parsing of flags in commandline arguments using the argparse library.
    '''

    # Singleton instance to avoid creating multiple instances
    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super(FlagParser, self).__new__(self)
        return self.instance


    def __init__(self):
        super().__init__(
            prog='python main.py',
            description='''
                            This program is an import script for use in various CSOH mysql databases. 
                            Compatible with Python 3.11+
                        ''',
            fromfile_prefix_chars='@',
        )

        file_group = self.add_mutually_exclusive_group(required=True)

        file_group.add_argument(
            '-f', '--file', type=str, help='The filepath to load data from'
        )

        file_group.add_argument(
            '-d',
            '--directory',
            type=str,
            help='The directory to load data from (Will not search folders recursively)',
        )

        self.add_argument(
            '-e',
            '--extensions',
            nargs='+',
            default=[],
            help='The extensions to filter by when using the --directory argument',
        )

        self.add_argument(
            '-debug', action='store_true', default=False, help='Enable debug mode'
        )

        self.add_argument(
            '-r',
            '--recursive',
            action='store_true',
            default=False,
            help='Enables recursion through subdirectories when using the --directory argument',
        )

        self.add_argument(
            '-depth',
            type=int,
            default=3,
            help=('Depth of the recursion search when using the '
                  '--directory argument with --recursive enabled. Defaults to 3.'),
        )

        self.add_argument(
            '-delimiter',
            type=str,
            default=',',
            help='Delimiter for text files. Defaults to ",".',
        )

        self.add_argument(
            '-type',
            type=str,
            help='Specifies the type of file to use. (HCDC, etc.)',
            required=True,
        )

        self.add_argument(
            '-createDatabase',
            action='store_true',
            default=False,
            help='Creates the database if it does not exist'
        )

        self.add_argument(
            '-encoding',
            default='utf-8',
            help='Sets the encoding for files to be loaded in'
        )

        self.args = self.parse_args()

        if self.args.directory and self.args.extensions == []:
            self.error('--directory requires --extension argument')

        if self.args.depth and self.args.recursive is None:
            self.error('-depth requires --recursive argument')

        if self.args.recursive and self.args.directory is None:
            self.error('--recursive requires --directory argument')
