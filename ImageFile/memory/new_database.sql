--
-- File generated with SQLiteStudio v3.3.3 on Sa Jul 17 14:53:03 2021
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: images
CREATE TABLE images (
    basename  STRING  NOT NULL,
    extension STRING  NOT NULL,
    tags      TAGS    NOT NULL
                      DEFAULT (''),
    [groups]  STRING  NOT NULL
                      DEFAULT (''),
    preview   BLOB    NOT NULL,
    data      BLOB    NOT NULL,
    timestamp INTEGER NOT NULL
                      DEFAULT (CURRENT_TIMESTAMP)
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
