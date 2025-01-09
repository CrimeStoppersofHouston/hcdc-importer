'''
    Preset for the hpd database
'''

### External Imports ###

from numpy import datetime64

### Internal Imports ###

from model.database.database_model import Table, Column, Schema
from automation.schema_creation import create_hpd

database = Schema(
    'default', False, create_hpd.create
).add_table(
    Table('offense').add_column(
        Column('NIBRSClass', 'code', str)
    ).add_column(
        Column('NIBRSDescription', 'literal', str)
    )
)

incidents = Table('incident').add_column(
    Column('Incident','incident_id', int)
).add_column(
    Column('RMSOccurrenceDate','incident_date', datetime64)
).add_column(
    Column('NIBRSClass','offense_code', str)
).add_column(
    Column('OffenseCount','offense_count', int)
).add_column(
    Column('Beat','beat', str)
).add_column(
    Column('Premise','premise', str)
).add_column(
    Column('StreetNo','street_number', str)
).add_column(
    Column('StreetName','street_name', str)
).add_column(
    Column('StreetType','street_type', str)
).add_column(
    Column('Suffix','suffix', str)
).add_column(
    Column('City','city', str)
).add_column(
    Column('ZIPCode','zip_code', str)
).add_column(
    Column('MapLongitude','map_longitude', float)
).add_column(
    Column('MapLatitude','map_latitude', float)
)

incidents.add_prereq(database.get_table_by_name('offense'))
database.add_table(incidents)
