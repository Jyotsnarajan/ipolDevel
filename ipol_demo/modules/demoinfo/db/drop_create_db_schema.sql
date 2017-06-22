PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS "state" (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	name VARCHAR(500) UNIQUE,
	description TEXT,
	creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "demodescription" (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	DDL BLOB
);
CREATE TABLE IF NOT EXISTS "demo" (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	editor_demo_id INTEGER UNIQUE NOT NULL,
	title VARCHAR UNIQUE NOT NULL,
	creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	stateID INTEGER,
	FOREIGN KEY(stateID) REFERENCES state(id)
);
CREATE TABLE IF NOT EXISTS "demo_demodescription" (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        demoID INTEGER NOT NULL,
        demodescriptionId INTEGER NOT NULL,
        FOREIGN KEY(demodescriptionId) REFERENCES demodescription(id) ON DELETE CASCADE,
        FOREIGN KEY(demoID) REFERENCES demo(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "author" (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR ,
        mail VARCHAR(320) UNIQUE,
        creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "editor" (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR ,
        mail VARCHAR(320) UNIQUE,
        creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "demo_author" (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        demoID INTEGER NOT NULL,
        authorId INTEGER NOT NULL,
        FOREIGN KEY(authorId) REFERENCES author(id) ON DELETE CASCADE,
        FOREIGN KEY(demoID) REFERENCES demo(id) ON DELETE CASCADE,
        UNIQUE(demoID, authorId)
);
CREATE TABLE IF NOT EXISTS "demo_editor" (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        demoID INTEGER,
        editorId INTEGER,
        FOREIGN KEY(editorId) REFERENCES editor(id) ON DELETE CASCADE,
        FOREIGN KEY(demoID) REFERENCES demo(id) ON DELETE CASCADE,
        UNIQUE(demoID, editorId)
);