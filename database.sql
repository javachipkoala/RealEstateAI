CREATE DATABASE IF NOT EXISTS real_estate_ai;
USE real_estate_ai;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS agents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    agency VARCHAR(150),
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    location VARCHAR(150),
    password VARCHAR(255) NOT NULL,
    certificate VARCHAR(255),
    certificate_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'Pending',
    role VARCHAR(20) DEFAULT 'agent'
);

CREATE TABLE IF NOT EXISTS properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    location VARCHAR(200) NOT NULL,
    type VARCHAR(50),
    price VARCHAR(50),
    bedrooms INT DEFAULT 0,
    bathrooms INT DEFAULT 0,
    area VARCHAR(50),
    description TEXT,
    images TEXT,
    documents TEXT,
    agent_name VARCHAR(100),
    agent_email VARCHAR(150),
    agent_agency VARCHAR(150),
    status VARCHAR(20) DEFAULT 'Pending'
);

CREATE TABLE IF NOT EXISTS inquiries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT,
    property_title VARCHAR(200),
    user_name VARCHAR(100),
    user_email VARCHAR(150),
    message TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    reply TEXT
);

CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(150) NOT NULL,
    property_id INT NOT NULL,
    UNIQUE KEY unique_favorite (user_email, property_id)
);