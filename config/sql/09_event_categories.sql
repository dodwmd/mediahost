CREATE TABLE IF NOT EXISTS event_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    category_id INT NOT NULL,
    UNIQUE KEY (event_id, category_id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
