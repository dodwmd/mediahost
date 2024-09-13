CREATE TABLE IF NOT EXISTS event_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    tag_id INT NOT NULL,
    UNIQUE KEY (event_id, tag_id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
