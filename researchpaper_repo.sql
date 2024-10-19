CREATE DATABASE IF NOT EXISTS Research_Paper_Repository;

USE Research_Paper_Repository;

CREATE TABLE Users(
    user_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    role ENUM('Researcher', 'Student', 'Admin'),
    email VARCHAR(100),
    affiliation VARCHAR(100)
);

CREATE TABLE Research_areas(
    area_id INT PRIMARY KEY,
    area_name VARCHAR(100),
    description TEXT
);

CREATE TABLE Research_papers (
    paper_id INT PRIMARY KEY,
    title VARCHAR(255),
    abstract TEXT,
    doi VARCHAR(50),
    citation_count INT,
    journal_name VARCHAR(100),
    publication_year INT,
    file_path VARCHAR(255),
    approval_status ENUM('Pending', 'Approved', 'Rejected'),
    version INT DEFAULT 1
);

CREATE TABLE Paper_reviews (
    review_id INT PRIMARY KEY,
    paper_id INT,
    reviewer_id INT,
    rating INT,
    comments TEXT,
    review_date DATE,
    FOREIGN KEY (paper_id) REFERENCES Research_papers(paper_id),
    FOREIGN KEY (reviewer_id) REFERENCES Users(user_id)
);

CREATE TABLE Paper_keywords (
    paper_id INT,
    keyword VARCHAR(50),
    PRIMARY KEY (paper_id, keyword),
    FOREIGN KEY (paper_id) REFERENCES Research_papers(paper_id)
);

CREATE TABLE Paper_authors (
    paper_id INT,
    author_id INT,
    PRIMARY KEY (paper_id, author_id),
    FOREIGN KEY (paper_id) REFERENCES Research_papers(paper_id),
    FOREIGN KEY (author_id) REFERENCES Users(user_id)
);

CREATE TABLE Paper_research_areas (
    paper_id INT,
    area_id INT,
    PRIMARY KEY (paper_id, area_id),
    FOREIGN KEY (paper_id) REFERENCES Research_papers(paper_id),
    FOREIGN KEY (area_id) REFERENCES Research_areas(area_id)
);

CREATE TABLE User_access_rights (
    user_id INT,
    resource_type ENUM('Paper', 'User', 'Review'),
    access_level ENUM('Read', 'Write', 'Admin'),
    PRIMARY KEY (user_id, resource_type),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);