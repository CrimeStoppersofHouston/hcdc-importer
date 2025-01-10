'''
This module is meant to be used to create a new instance of the hcdc database.
It includes a creation statement and a creation function for this purpose.
'''

### External Imports ###

import contextlib

import pyodbc

### Internal Imports ###

from utility.connection.connection_pool import ConnectionPool

### Variable Declarations ###

CREATE_STMT = '''
CREATE TABLE IF NOT EXISTS `attorney` (
  `spn` varchar(8) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`spn`)
);

CREATE TABLE IF NOT EXISTS `case_type` (
  `id` tinyint unsigned NOT NULL,
  `literal` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `case_status` (
  `id` varchar(1) NOT NULL,
  `literal` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `defendant` (
  `spn` varchar(8) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `race` varchar(10) DEFAULT NULL,
  `sex` varchar(10) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `street_number` varchar(255) DEFAULT NULL,
  `street_name` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(10) DEFAULT NULL,
  `zip` varchar(10) DEFAULT NULL,
  `citizen` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`spn`)
);

CREATE TABLE IF NOT EXISTS `defendant_status` (
  `id` varchar(1) NOT NULL,
  `literal` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `disposition` (
  `id` varchar(4) NOT NULL,
  `literal` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `event` (
  `entry` bigint NOT NULL AUTO_INCREMENT,
  `case_id` bigint NOT NULL,
  `case_type_id` tinyint unsigned NOT NULL,
  `disposition` varchar(60) NOT NULL,
  `disposition_code` varchar(4) DEFAULT NULL,
  `disposition_date` date DEFAULT NULL,
  `sentence` varchar(60) DEFAULT NULL,
  `bond_amount` varchar(30) DEFAULT NULL,
  `bond_explanation` varchar(30) DEFAULT NULL,
  `next_appearance` date DEFAULT NULL,
  PRIMARY KEY (`entry`, `case_id`,`case_type_id`),
  UNIQUE KEY `events_UI` (`case_id`,`case_type_id`,`disposition`)
);

CREATE TABLE IF NOT EXISTS `offense` (
  `id` int NOT NULL,
  `literal` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `report` (
  `num` int NOT NULL AUTO_INCREMENT,
  `id` varchar(25) NOT NULL,
  `agency` varchar(50) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`num`,`id`),
  UNIQUE KEY `report_UI` (`id`,`name`)
);

CREATE TABLE IF NOT EXISTS `stage_attorney` (
  `entry` int NOT NULL AUTO_INCREMENT,
  `spn` varchar(8) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`entry`,`spn`)
);

CREATE TABLE IF NOT EXISTS `stage_defendant` (
  `entry` int NOT NULL AUTO_INCREMENT,
  `spn` varchar(8) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `race` varchar(10) DEFAULT NULL,
  `sex` varchar(10) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `street_number` varchar(255) DEFAULT NULL,
  `street_name` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(10) DEFAULT NULL,
  `zip` varchar(10) DEFAULT NULL,
  `citizen` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`entry`,`spn`)
);

CREATE TABLE IF NOT EXISTS `stage_event` (
  `entry` int NOT NULL AUTO_INCREMENT,
  `case_id` bigint NOT NULL,
  `case_type_id` tinyint unsigned NOT NULL,
  `disposition` varchar(60) NOT NULL,
  `disposition_code` varchar(4) DEFAULT NULL,
  `disposition_date` date DEFAULT NULL,
  `sentence` varchar(60) DEFAULT NULL,
  `bond_amount` varchar(30) DEFAULT NULL,
  `bond_explanation` varchar(30) DEFAULT NULL,
  `next_appearance` date DEFAULT NULL,
  PRIMARY KEY (`entry`,`case_id`,`case_type_id`)
);

CREATE TABLE IF NOT EXISTS `stage_offense` (
  `entry` int NOT NULL AUTO_INCREMENT,
  `id` int NOT NULL,
  `literal` varchar(255) NOT NULL,
  PRIMARY KEY (`entry`,`id`)
);

CREATE TABLE IF NOT EXISTS `stage_report` (
  `entry` int NOT NULL AUTO_INCREMENT,
  `id` varchar(25) NOT NULL,
  `agency` varchar(50) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`entry`,`id`)
);

CREATE TABLE IF NOT EXISTS `stage_cases` (
  `entry` int NOT NULL AUTO_INCREMENT,
  `id` bigint NOT NULL,
  `case_type_id` tinyint unsigned NOT NULL,
  `report_id` varchar(25) DEFAULT NULL,
  `offense_id` int NOT NULL,
  `defendant_spn` varchar(8) NOT NULL,
  `case_status_id` varchar(1) DEFAULT NULL,
  `defendant_status_id` varchar(1) DEFAULT NULL,
  `attorney_spn` varchar(8) DEFAULT NULL,
  `court` smallint DEFAULT NULL,
  `filing_date` date NOT NULL,
  PRIMARY KEY (`entry`,`id`,`case_type_id`)
);

CREATE TABLE IF NOT EXISTS `cases` (
  `id` bigint NOT NULL,
  `case_type_id` tinyint unsigned NOT NULL,
  `report_id` varchar(25) DEFAULT NULL,
  `offense_id` int NOT NULL,
  `defendant_spn` varchar(8) NOT NULL,
  `case_status_id` varchar(1) DEFAULT NULL,
  `defendant_status_id` varchar(1) DEFAULT NULL,
  `attorney_spn` varchar(8) DEFAULT NULL,
  `court` smallint DEFAULT NULL,
  `filing_date` date NOT NULL,
  PRIMARY KEY (`id`,`case_type_id`),
  KEY `report_id` (`report_id`),
  KEY `offense_id` (`offense_id`),
  KEY `defendant_spn` (`defendant_spn`),
  KEY `case_status_id` (`case_status_id`),
  KEY `defendant_status_id` (`defendant_status_id`),
  KEY `attorney_spn` (`attorney_spn`),
  CONSTRAINT `cases_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `report` (`id`),
  CONSTRAINT `cases_ibfk_2` FOREIGN KEY (`offense_id`) REFERENCES `offense` (`id`),
  CONSTRAINT `cases_ibfk_3` FOREIGN KEY (`defendant_spn`) REFERENCES `defendant` (`spn`),
  CONSTRAINT `cases_ibfk_4` FOREIGN KEY (`case_status_id`) REFERENCES `case_status` (`id`),
  CONSTRAINT `cases_ibfk_5` FOREIGN KEY (`defendant_status_id`) REFERENCES `defendant_status` (`id`),
  CONSTRAINT `cases_ibfk_6` FOREIGN KEY (`attorney_spn`) REFERENCES `attorney` (`spn`),
  CONSTRAINT `cases_ibfk_7` FOREIGN KEY (`id`, `case_type_id`) REFERENCES `event` (`case_id`, `case_type_id`),
  CONSTRAINT `cases_ibfk_8` FOREIGN KEY (`case_type_id`) REFERENCES `case_type` (`id`)
);

alter table event AUTO_INCREMENT = 1;
alter table report AUTO_INCREMENT = 1;
insert into defendant (spn) values ('') on duplicate key update spn = spn;
insert into report (id, name) values ('', '') on duplicate key update id = id;
insert into offense (id, literal) values (-1, 'NULL') on duplicate key update id = id;
insert into defendant_status (id, literal) values (1, "Unknown") on duplicate key update id = id;

insert into disposition select * from HCDC_LookupTables.case_disposition n on duplicate key update id = n.id;
insert into case_status select * from HCDC_LookupTables.case_status n on duplicate key update id = n.id;
insert into case_type select * from HCDC_LookupTables.case_type n on duplicate key update id = n.id;
insert into defendant_status select * from HCDC_LookupTables.defendant_status n on duplicate key update id = n.id;
'''

### Function Declarations ###


def create(
    schema_name: str, connection: pyodbc.Connection, connection_pool: ConnectionPool
) -> None:
    '''Creates a new HCDC snapshot database with a predefined creation statement'''
    with contextlib.closing(connection.cursor()) as cursor:
        cursor.execute(f'create database if not exists {schema_name}')
        cursor.commit()

        old_database = connection_pool.database
        connection_pool.set_database(schema_name)
        new_connection = connection_pool.get_connection()
        new_cursor = new_connection.cursor()
        new_cursor.execute(f'use {schema_name};')
        new_cursor.commit()
        for statement in CREATE_STMT.split(';'):
            if statement.strip() == '':
                continue
            new_cursor.execute(statement)
        new_cursor.commit()
        new_connection.close()

        connection_pool.set_database(old_database)
        connection_pool.free_connection(connection)
