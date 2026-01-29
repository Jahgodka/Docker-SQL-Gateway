CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    department VARCHAR(100),
    hire_date DATE
);

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100)
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    deadline DATE,
    department VARCHAR(100)
);

-- Seed Data (English)
INSERT INTO employees (first_name, last_name, department, hire_date) VALUES
('Anna', 'Smith', 'HR', '2021-03-15'),
('John', 'Doe', 'IT', '2022-06-01'),
('Julia', 'Walker', 'Finance', '2020-11-22'),
('Paul', 'Lewinsky', 'IT', '2019-04-10'),
('Kate', 'Newton', 'Marketing', '2023-01-05');

INSERT INTO departments (name, location) VALUES
('HR', 'Warsaw'),
('IT', 'Cracow'),
('Finance', 'Gdansk'),
('Marketing', 'Wroclaw');

INSERT INTO projects (name, deadline, department) VALUES
('Database Migration', '2024-10-01', 'IT'),
('Banking App API', '2024-08-15', 'Finance'),
('Q3 Ad Campaign', '2024-09-30', 'Marketing');