-- Migration: add_userdata
-- Created at: 20241109195708
-- Branch: htf02
-- Up Migration

CREATE TABLE user_data (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    password VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
