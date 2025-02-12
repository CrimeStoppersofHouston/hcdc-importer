'''
    This module contains the presets for handling
    different types of imports. Ideally, this should
    be the only place other than setting up models that 
    would require editing to add another dataset.
'''

### External Imports ###

import logging

### Internal Imports ###

from model.database import hcdc_snapshot, hpd_database, crime_index
from config.flag_parser import FlagParser
from utility.connection.connection_pool import ConnectionPool

### Class Declarations ###

class ImportType():
    '''Singleton Class that contains global data related to import types'''
    # Singleton instance to avoid creating multiple instances
    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super(ImportType, self).__new__(self)
        return self.instance

    def __init__(self):
        parser = FlagParser()
        match parser.args.type:
            case 'hcdc':
                self.name = 'Harris County District Clerk Snapshot'
                self.model = hcdc_snapshot.database
            case 'hpd':
                self.name = 'Houston Police Department Beats'
                self.model = hpd_database.database
            case 'ci':
                self.name = 'Crime Index'
                self.model = crime_index.database
            case _:
                logging.error('Undefined import type %s!', parser.args.type)