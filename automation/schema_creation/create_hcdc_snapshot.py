"""
This module is meant to be used to create a new instance of the hcdc database.
It includes a creation statement and a creation function for this purpose.
"""

### External Imports ###

import contextlib

import pyodbc

### Internal Imports ###

from utility.connection.connection_pool import ConnectionPool

### Variable Declarations ###

CREATE_STMT = """
CREATE TABLE IF NOT EXISTS `attorney` (
    `spn` varchar(8) NOT NULL,
    `name` varchar(255) NOT NULL,
    PRIMARY KEY (`spn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `attorney_prep` (
    `entry` int NOT NULL AUTO_INCREMENT,
    `spn` varchar(8) NOT NULL,
    `name` varchar(255) NOT NULL,
    PRIMARY KEY (`entry`,`spn`)
) ENGINE=InnoDB AUTO_INCREMENT=8616 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `case_disposition` (
    `id` varchar(4) NOT NULL,
    `literal` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `case_status` (
    `id` varchar(1) NOT NULL,
    `literal` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `case_type` (
    `id` tinyint unsigned NOT NULL,
    `literal` varchar(15) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `cases` (
    `id` bigint NOT NULL,
    `case_type_id` tinyint unsigned NOT NULL,
    `filing_date` date NOT NULL,
    PRIMARY KEY (`id`,`case_type_id`),
    KEY `cases_ibfk_1` (`case_type_id`),
    CONSTRAINT `cases_ibfk` FOREIGN KEY (`case_type_id`) REFERENCES `case_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `cases_prep` (
    `entry` int NOT NULL AUTO_INCREMENT,
    `id` bigint NOT NULL,
    `case_type_id` tinyint unsigned NOT NULL,
    `filing_date` date NOT NULL,
    PRIMARY KEY (`entry`,`id`,`case_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9869 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `coc` (
    `id` varchar(3) NOT NULL,
    `literal` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `coc_prep` (
    `entry` int NOT NULL AUTO_INCREMENT,
    `id` varchar(3) NOT NULL,
    `literal` varchar(255) NOT NULL,
    PRIMARY KEY (`entry`,`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8616 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `defendant_prep` (
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
) ENGINE=InnoDB AUTO_INCREMENT=9869 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `defendant_status` (
    `id` varchar(1) NOT NULL,
    `literal` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `instrument` (
    `id` text,
    `literal` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `level_and_degree` (
    `id` text,
    `literal` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `offense` (
    `id` int NOT NULL,
    `literal` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `offense_prep` (
    `entry` int NOT NULL AUTO_INCREMENT,
    `id` int NOT NULL,
    `literal` varchar(255) NOT NULL,
    PRIMARY KEY (`entry`,`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9869 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `report` (
    `num` int NOT NULL AUTO_INCREMENT,
    `id` varchar(25) NOT NULL,
    `agency` varchar(50) DEFAULT NULL,
    `name` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`num`,`id`),
    UNIQUE KEY `report_UI` (`id`,`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3203498 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `report_prep` (
    `entry` int NOT NULL AUTO_INCREMENT,
    `id` varchar(25) NOT NULL,
    `agency` varchar(50) DEFAULT NULL,
    `name` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`entry`,`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `setting_reason` (
    `id` text,
    `literal` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `events` (
    `entry` bigint NOT NULL AUTO_INCREMENT,
    `case_id` bigint NOT NULL,
    `case_type_id` tinyint unsigned NOT NULL,
    `offense_id` int NOT NULL,
    `defendant_spn` varchar(8) NOT NULL,
    `disposition` varchar(60) NOT NULL,
    `report_id` varchar(25) DEFAULT NULL,
    `attorney_spn` varchar(8) DEFAULT NULL,
    `case_status_id` varchar(1) DEFAULT NULL,
    `defendant_status_id` varchar(1) DEFAULT NULL,
    `case_disposition_id` varchar(4) DEFAULT NULL,
    `court` smallint DEFAULT NULL,
    `disposition_date` date DEFAULT NULL,
    PRIMARY KEY (`entry`,`case_id`),
    UNIQUE KEY `case_id` (`case_id`,`case_type_id`,`offense_id`,`defendant_spn`,`disposition`),
    KEY `offense_id` (`offense_id`),
    KEY `defendant_spn` (`defendant_spn`),
    KEY `attorney_spn` (`attorney_spn`),
    KEY `case_status_id` (`case_status_id`),
    KEY `defendant_status_id` (`defendant_status_id`),
    KEY `case_disposition_id` (`case_disposition_id`),
    KEY `case_type_id` (`case_type_id`),
    KEY `events_ibfk_4` (`report_id`),
    CONSTRAINT `events_ibfk_1` FOREIGN KEY (`case_id`, `case_type_id`) REFERENCES `cases` (`id`, `case_type_id`),
    CONSTRAINT `events_ibfk_2` FOREIGN KEY (`offense_id`) REFERENCES `offense` (`id`),
    CONSTRAINT `events_ibfk_3` FOREIGN KEY (`defendant_spn`) REFERENCES `defendant` (`spn`),
    CONSTRAINT `events_ibfk_4` FOREIGN KEY (`report_id`) REFERENCES `report` (`id`),
    CONSTRAINT `events_ibfk_5` FOREIGN KEY (`attorney_spn`) REFERENCES `attorney` (`spn`),
    CONSTRAINT `events_ibfk_6` FOREIGN KEY (`case_status_id`) REFERENCES `case_status` (`id`),
    CONSTRAINT `events_ibfk_7` FOREIGN KEY (`defendant_status_id`) REFERENCES `defendant_status` (`id`),
    CONSTRAINT `events_ibfk_8` FOREIGN KEY (`case_disposition_id`) REFERENCES `case_disposition` (`id`),
    CONSTRAINT `events_ibfk_9` FOREIGN KEY (`case_type_id`) REFERENCES `case_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3896240 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `events_descriptor` (
    `entry` bigint NOT NULL,
    `case_id` bigint NOT NULL,
    `case_type_id` tinyint unsigned NOT NULL,
    `sentence` varchar(60) DEFAULT NULL,
    `bond_amount` varchar(30) DEFAULT NULL,
    `bond_explanation` varchar(30) DEFAULT NULL,
    `next_appearance` date DEFAULT NULL,
    `level_and_degree` varchar(3) DEFAULT NULL,
    `instrument` varchar(6) DEFAULT NULL,
    `setting_calendar_code` varchar(6) DEFAULT NULL,
    `setting_reason` varchar(6) DEFAULT NULL,
    PRIMARY KEY (`entry`,`case_id`),
    KEY `case_id` (`case_id`),
    KEY `events_descriptor_ibfk_2` (`case_id`,`case_type_id`),
    CONSTRAINT `events_descriptor_ibfk_1` FOREIGN KEY (`entry`) REFERENCES `events` (`entry`),
    CONSTRAINT `events_descriptor_ibfk_2` FOREIGN KEY (`case_id`, `case_type_id`) REFERENCES `events` (`case_id`, `case_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `events_prep` (
    `entry` int NOT NULL AUTO_INCREMENT,
    `case_id` bigint NOT NULL,
    `offense_id` int DEFAULT NULL,
    `defendant_spn` varchar(8) DEFAULT NULL,
    `disposition` varchar(60) DEFAULT NULL,
    `report_id` varchar(25) DEFAULT NULL,
    `attorney_spn` varchar(8) DEFAULT NULL,
    `case_status_id` varchar(1) DEFAULT NULL,
    `defendant_status_id` varchar(1) DEFAULT NULL,
    `case_disposition_id` varchar(4) DEFAULT NULL,
    `case_type_id` tinyint unsigned DEFAULT NULL,
    `sentence` varchar(60) DEFAULT NULL,
    `bond_amount` varchar(30) DEFAULT NULL,
    `bond_explanation` varchar(30) DEFAULT NULL,
    `next_appearance` date DEFAULT NULL,
    `disposition_date` date DEFAULT NULL,
    `level_and_degree` varchar(3) DEFAULT NULL,
    `instrument` varchar(6) DEFAULT NULL,
    `setting_calendar_code` varchar(6) DEFAULT NULL,
    `setting_reason` varchar(6) DEFAULT NULL,
    `court` smallint DEFAULT NULL,
    PRIMARY KEY (`entry`),
    UNIQUE KEY `events_UI` (`case_id`,`offense_id`,`defendant_spn`,`disposition`)
) ENGINE=InnoDB AUTO_INCREMENT=9869 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

alter table events AUTO_INCREMENT = 1;
alter table report AUTO_INCREMENT = 1;
insert into defendant (spn) values ('');
insert into report (id, name) values ('', '');
insert into offense (id, literal) values (-1, 'NULL');
insert into defendant_status (id, literal) values (1, "Unknown");

insert into case_disposition select * from HCDCMigration.case_disposition;
insert into case_status select * from HCDCMigration.case_status;
insert into case_type select * from HCDCMigration.case_type;
insert into defendant_status select * from HCDCMigration.defendant_status;
insert into instrument select * from HCDCMigration.instrument;
insert into level_and_degree select * from HCDCMigration.level_and_degree;
insert into setting_reason select * from HCDCMigration.setting_reason;
"""

### Function Declarations ###


def create(
    schema_name: str, connection: pyodbc.Connection, connection_pool: ConnectionPool
) -> None:
    '''Creates a new HCDC snapshot database with a predefined creation statement'''
    with contextlib.closing(connection.cursor()) as cursor:
        cursor.execute(f"create database if not exists {schema_name}")
        cursor.commit()

        old_database = connection_pool.database
        connection_pool.set_database(schema_name)
        new_connection = connection_pool.get_connection()
        new_cursor = new_connection.cursor()
        new_cursor.execute(f"use {schema_name};")
        new_cursor.commit()
        for statement in CREATE_STMT.split(";"):
            new_cursor.execute(statement)
        new_cursor.commit()
        new_connection.close()

        connection_pool.set_database(old_database)
        connection_pool.free_connection(connection)
