CREATE DATABASE IF NOT EXISTS mini_project;
USE mini_project;

CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    role VARCHAR(50) NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE pet (
    pet_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    breed VARCHAR(50),
    adoption_status VARCHAR(20) DEFAULT 'Available',
    date_of_registration DATE NOT NULL,
    age INT,
    weight FLOAT,
    owner_id INT,
    FOREIGN KEY (owner_id) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE pet_health (
    health_id INT PRIMARY KEY AUTO_INCREMENT,
    pet_id INT NOT NULL,
    allergies VARCHAR(100),
    vaccinations VARCHAR(100),
    medical_history TEXT,
    FOREIGN KEY (pet_id) REFERENCES pet(pet_id) ON DELETE CASCADE
);

CREATE TABLE care_schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    pet_id INT NOT NULL,
    vet_id INT NOT NULL,
    care_description TEXT,
    care_date DATE,
    FOREIGN KEY (pet_id) REFERENCES pet(pet_id) ON DELETE CASCADE,
    FOREIGN KEY (vet_id) REFERENCES user(user_id)
);

CREATE TABLE adoption_application (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    pet_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    application_date DATE,
    applicant_name VARCHAR(100),
    email_id VARCHAR(255),
    phone_no VARCHAR(20),
    house_no VARCHAR(20),
    apartment VARCHAR(50),
    street VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    pincode VARCHAR(10),
    FOREIGN KEY (pet_id) REFERENCES pet(pet_id) ON DELETE CASCADE
);

CREATE TABLE user_permissions (
    user_id INT NOT NULL,
    permissions VARCHAR(100) NOT NULL,
    PRIMARY KEY (user_id, permissions),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE notification (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    notification_type VARCHAR(50),
    notification_date DATE,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- Inserting sample data
INSERT INTO user (user_id, role, user_name, email, password) VALUES
(1, 'owner', 'John Doe', 'john@example.com', 'password123'),
(2, 'owner', 'Jane Smith', 'jane@example.com', 'password456');

INSERT INTO pet (name, breed, adoption_status, date_of_registration, age, weight, owner_id) VALUES 
('Buddy', 'Golden Retriever', 'Available', '2024-01-01', 3, 25.0, 1),
('Mittens', 'Siamese', 'Available', '2024-01-05', 2, 5.0, 1),
('Coco', 'Poodle', 'Available', '2024-01-10', 4, 10.0, 2);
