-- Create Database
CREATE DATABASE IF NOT EXISTS test_db;
USE test_db;

-- Table 1: users (Customer information)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age INT,
    email VARCHAR(100),
    city VARCHAR(50),
    signup_date DATE,
    loyalty_points INT DEFAULT 0,
    active BOOLEAN DEFAULT TRUE
);

-- Table 2: products (Items available for purchase)
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2),
    stock INT,
    release_date DATE,
    is_available BOOLEAN DEFAULT TRUE
);

-- Table 3: orders (Customer purchases)
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT,
    amount DECIMAL(10, 2),
    order_date DATETIME,
    status ENUM('pending', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Table 4: reviews (User feedback on products)
CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    review_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Table 5: payments (Transaction details)
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    user_id INT,
    amount DECIMAL(10, 2),
    payment_method ENUM('credit_card', 'debit_card', 'paypal', 'cash') DEFAULT 'credit_card',
    payment_date DATETIME,
    success BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert Sample Data: users
INSERT INTO users (first_name, last_name, age, email, city, signup_date, loyalty_points, active) VALUES
('John', 'Doe', 25, 'john.doe@example.com', 'New York', '2023-05-10', 150, TRUE),
('Jane', 'Smith', 32, 'jane.smith@example.com', 'Los Angeles', '2022-11-15', 300, TRUE),
('Alice', 'Johnson', 28, 'alice.j@example.com', 'Chicago', '2024-01-20', 50, TRUE),
('Bob', 'Brown', 45, 'bob.brown@example.com', 'Houston', '2021-03-12', 500, FALSE),
('Emma', 'Davis', 19, 'emma.davis@example.com', 'Seattle', '2024-06-01', 20, TRUE),
('Michael', 'Lee', 37, 'michael.lee@example.com', 'Boston', '2023-09-05', 200, TRUE),
('Sarah', 'Wilson', 29, 'sarah.w@example.com', 'Denver', '2022-07-18', 250, TRUE),
('David', 'Clark', 52, 'david.clark@example.com', 'Miami', '2020-12-01', 800, FALSE);

-- Insert Sample Data: products
INSERT INTO products (name, category, price, stock, release_date, is_available) VALUES
('Laptop Pro', 'Electronics', 999.99, 25, '2023-01-10', TRUE),
('Smartphone X', 'Electronics', 499.99, 50, '2023-06-15', TRUE),
('Headphones', 'Accessories', 79.99, 100, '2022-09-01', TRUE),
('Monitor 4K', 'Electronics', 299.99, 15, '2024-01-05', TRUE),
('Tablet Lite', 'Electronics', 199.99, 30, '2023-11-20', TRUE),
('Desk Chair', 'Furniture', 149.99, 10, '2022-03-15', FALSE),
('Wireless Mouse', 'Accessories', 29.99, 200, '2024-02-10', TRUE),
('Smartwatch', 'Wearables', 249.99, 40, '2023-08-25', TRUE);

-- Insert Sample Data: orders
INSERT INTO orders (user_id, product_id, quantity, amount, order_date, status) VALUES
(1, 1, 1, 999.99, '2025-01-15 10:30:00', 'shipped'),
(2, 2, 2, 999.98, '2025-02-10 14:15:00', 'delivered'),
(3, 3, 3, 239.97, '2025-03-01 09:45:00', 'pending'),
(4, 4, 1, 299.99, '2025-02-20 16:00:00', 'cancelled'),
(5, 5, 2, 399.98, '2025-03-05 11:20:00', 'shipped'),
(6, 1, 1, 999.99, '2024-12-25 13:00:00', 'delivered'),
(7, 7, 5, 149.95, '2025-01-30 08:15:00', 'pending'),
(8, 8, 1, 249.99, '2025-02-15 17:30:00', 'shipped'),
(1, 2, 1, 499.99, '2024-11-10 12:00:00', 'delivered'),
(3, 5, 1, 199.99, '2025-03-07 10:00:00', 'pending');

-- Insert Sample Data: reviews
INSERT INTO reviews (user_id, product_id, rating, comment, review_date) VALUES
(1, 1, 4, 'Great laptop, but battery life could be better.', '2025-01-20'),
(2, 2, 5, 'Best phone I’ve ever used!', '2025-02-15'),
(3, 3, 3, ' Decent sound, but uncomfortable after a while.', '2025-03-02'),
(4, 4, 2, 'Monitor flickers sometimes.', '2025-02-25'),
(5, 5, 4, 'Good value for the price.', '2025-03-06'),
(6, 1, 5, 'Perfect for work!', '2024-12-30'),
(7, 7, 4, 'Mouse is smooth and responsive.', '2025-02-01'),
(8, 8, 3, 'Smartwatch is okay, but app support is limited.', '2025-02-20');

-- Insert Sample Data: payments
INSERT INTO payments (order_id, user_id, amount, payment_method, payment_date, success) VALUES
(1, 1, 999.99, 'credit_card', '2025-01-15 10:35:00', TRUE),
(2, 2, 999.98, 'paypal', '2025-02-10 14:20:00', TRUE),
(3, 3, 239.97, 'debit_card', '2025-03-01 09:50:00', FALSE),
(4, 4, 299.99, 'credit_card', '2025-02-20 16:05:00', FALSE),
(5, 5, 399.98, 'cash', '2025-03-05 11:25:00', TRUE),
(6, 6, 999.99, 'credit_card', '2024-12-25 13:05:00', TRUE),
(7, 7, 149.95, 'paypal', '2025-01-30 08:20:00', FALSE),
(8, 8, 249.99, 'debit_card', '2025-02-15 17:35:00', TRUE),
(9, 1, 499.99, 'credit_card', '2024-11-10 12:05:00', TRUE),
(10, 3, 199.99, 'cash', '2025-03-07 10:05:00', FALSE);