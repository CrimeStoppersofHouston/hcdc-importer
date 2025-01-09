'''
    Preset for the hcdc snapshot database
'''

### External Imports ###

from numpy import datetime64

### Internal Imports ###

from model.database.database_model import Table, Column, Schema
from automation.schema_creation import create_hcdc_snapshot

### Execution ###

database = Schema(
    'default', True, create_hcdc_snapshot.create
).add_table(
    Table(
        'offense'
    ).add_column(
        Column('curr_off', 'id', int)
    ).add_column(
        Column('curr_off_lit', 'literal', str)
    )
).add_table(
    Table(
        'attorney'
    ).add_column(
        Column('aty_spn', 'spn', str)
    ).add_column(
        Column('aty_nam', 'name', str)
    )
).add_table(
    Table(
        'report'
    ).add_column(
        Column('off_rpt_num', 'id', str)
    ).add_column(
        Column('comp_agency', 'agency', str)
    ).add_column(
        Column('comp_nam', 'name', str)
    )
).add_table(
    Table(
        'defendant'
    ).add_column(
        Column('def_spn', 'spn', str)
    ).add_column(
        Column('def_nam', 'name', str)
    ).add_column(
        Column('def_rac', 'race', str)
    ).add_column(
        Column('def_sex', 'sex', str)
    ).add_column(
        Column('def_dob', 'date_of_birth', str)
    ).add_column(
        Column('def_stnum', 'street_number', str)
    ).add_column(
        Column('def_stnam', 'street_name', str)
    ).add_column(
        Column('def_cty', 'city', str)
    ).add_column(
        Column('def_st', 'state', str)
    ).add_column(
        Column('def_zip', 'zip', str)
    ).add_column(
        Column('def_citizen', 'citizen', str)
    )
).add_table(
    Table(
        'event'
    ).add_column(
        Column('cas', 'case_id', int)
    ).add_column(
        Column('cdi', 'case_type_id', int)
    ).add_column(
        Column('disposition', 'disposition', str)
    ).add_column(
        Column('cad', 'disposition_code', str)
    ).add_column(
        Column('sentence', 'sentence', str)
    ).add_column(
        Column('dispdt', 'disposition_date', datetime64)
    ).add_column(
        Column('bamexp', 'bond_explanation', str)
    ).add_column(
        Column('bam', 'bond_amount', str)
    )
)

cases = Table(
        'cases'
    ).add_column(
        Column('cas', 'id', int)
    ).add_column(
        Column('cdi', 'case_type_id', int)
    ).add_column(
        Column('off_rpt_num', 'report_id', str)
    ).add_column(
        Column('curr_off', 'offense_id', int)
    ).add_column(
        Column('def_spn', 'defendant_spn', str)
    ).add_column(
        Column('cst', 'case_status_id', str)
    ).add_column(
        Column('dst', 'defendant_status_id', str)
    ).add_column(
        Column('aty_spn', 'attorney_spn', str)
    ).add_column(
        Column('crt', 'court', int)
    ).add_column(
        Column('fda', 'filing_date', datetime64)
    )

cases.add_prereq(database.get_table_by_name('offense'))
cases.add_prereq(database.get_table_by_name('attorney'))
cases.add_prereq(database.get_table_by_name('defendant'))
cases.add_prereq(database.get_table_by_name('event'))
cases.add_prereq(database.get_table_by_name('report'))

database.add_table(cases)
