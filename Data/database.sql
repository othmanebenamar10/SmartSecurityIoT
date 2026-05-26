-- Schema for SmartSecurityIoT database
-- Password is provided via DB_ENCRYPTION_KEY environment variable

CREATE TABLE IF NOT EXISTS Users
(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    FullName TEXT NOT NULL,
    Embedding BLOB NOT NULL,
    CreatedAt TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS IntrusionEvents
(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Snapshot BLOB NOT NULL,
    EventDate TEXT NOT NULL,
    LivenessPassed INTEGER NOT NULL
);
