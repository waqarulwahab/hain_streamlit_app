CREATE DATABASE upwork_client;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_favorite_recipes (
    favorite_id INT AUTO_INCREMENT PRIMARY KEY,
    user_fave_id INT,
    recipe_info VARCHAR(255) NOT NULL,
    liked BOOLEAN DEFAULT TRUE, 
    FOREIGN KEY (user_fave_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE recipe_rating (
    recipe_rating_id INT AUTO_INCREMENT PRIMARY KEY,
    liked BOOLEAN NOT NULL,
    recipe_comment VARCHAR(255) NOT NULL,
    recipe_info VARCHAR(255) NOT NULL,    
);

