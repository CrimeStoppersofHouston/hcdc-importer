'''
    This module contains the presets for handling
    different types of imports. Ideally, this should
    be the only place other than setting up models that 
    would require editing to add another dataset.
'''

### External Imports ###

import logging
import pyodbc

### Internal Imports ###

from model.database.database_model import DatabaseModel
from model.database import hcdc_snapshot, hpd_database
from utility.connection.connection_pool import ConnectionPool

### Class Declarations ###

class ImportType():
    def __init__(self, name:str, flag:str, model:DatabaseModel, stage_required=False):
        self.name = name
        self.flag = flag
        self.model = model

hcdc_import_type = ImportType(
    'Harris County District Clerk Snapshot',
    'hcdc',
    hcdc_snapshot
)

hpd_import_type = ImportType(
    'Houston Police Department Beats',
    'hpd',
    hpd_database
)
