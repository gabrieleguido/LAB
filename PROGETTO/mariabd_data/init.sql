CREATE DATABASE IF NOT EXISTS lab_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;
USE lab_db; 

-- Creazione dell'utente per il backend
CREATE USER IF NOT EXISTS 'backend_user'@'%' IDENTIFIED BY 'backend_password';
GRANT ALL PRIVILEGES ON lab_db.* TO 'backend_user'@'%';
FLUSH PRIVILEGES;

-- Tabella per memorizzare le risorse web
CREATE TABLE IF NOT EXISTS web_resources (
    url VARCHAR(768) PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    html_text LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tabella Gold Standard
CREATE TABLE IF NOT EXISTS gold_standard (
    url VARCHAR(768) PRIMARY KEY,
    gold_text LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_url FOREIGN KEY (url) 
        REFERENCES web_resources(url) 
        ON DELETE CASCADE
) ENGINE=InnoDB;