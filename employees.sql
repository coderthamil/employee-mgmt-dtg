CREATE TABLE employees(
id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL,
department VARCHAR(100),
email varchar(100) UNIQUE NOT NULL
);