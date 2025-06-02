CREATE DATABASE IF NOT EXISTS wanghong_community1;
USE wanghong_community1;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    badge_answer_expert BOOLEAN DEFAULT 0,
    badge_site_engineer BOOLEAN DEFAULT 0,
    badge_log_analyst BOOLEAN DEFAULT 0,
    title_volunteer BOOLEAN DEFAULT 0,
    title_senior_volunteer BOOLEAN DEFAULT 0,
    title_support_staff BOOLEAN DEFAULT 0,
    title_tech_advisor BOOLEAN DEFAULT 0,
    title_admin BOOLEAN DEFAULT 0,
    title_site_owner BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(60) NOT NULL,
    content TEXT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reply_count INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS replies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    reply_to INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (reply_to) REFERENCES replies(id) ON DELETE SET NULL
);