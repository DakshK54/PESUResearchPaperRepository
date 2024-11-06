-- Database Setup
DROP DATABASE IF EXISTS Research_Paper_Repository;
CREATE DATABASE IF NOT EXISTS Research_Paper_Repository;
USE Research_Paper_Repository;

-- Tables with AUTO_INCREMENT primary keys
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    role ENUM('Researcher', 'Student', 'Admin'),
    email VARCHAR(100),
    affiliation VARCHAR(100)
);

CREATE TABLE Research_areas (
    area_id INT AUTO_INCREMENT PRIMARY KEY,
    area_name VARCHAR(100),
    description TEXT
);

CREATE TABLE Research_papers (
    paper_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    abstract TEXT,
    doi VARCHAR(50),
    citation_count INT DEFAULT 0,
    journal_name VARCHAR(100),
    publication_year INT,
    approval_status ENUM('Pending', 'Approved', 'Rejected'),
    version INT DEFAULT 1,
    pdf_data LONGBLOB
);

CREATE TABLE Paper_reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT,
    reviewer_id INT,
    rating INT,
    comments TEXT,
    review_date DATE,
    FOREIGN KEY (paper_id) REFERENCES Research_papers(paper_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES Users(user_id) ON DELETE SET NULL
);

CREATE TABLE Paper_keywords (
    paper_id INT,
    keyword VARCHAR(50),
    PRIMARY KEY (paper_id, keyword),
    FOREIGN KEY (paper_id) REFERENCES Research_papers(paper_id) ON DELETE CASCADE
);

CREATE TABLE Paper_authors (
    paper_id INT,
    author_id INT,
    PRIMARY KEY (paper_id, author_id),
    FOREIGN KEY (paper_id) REFERENCES Research_papers(paper_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Paper_research_areas (
    paper_id INT,
    area_id INT,
    PRIMARY KEY (paper_id, area_id),
    FOREIGN KEY (paper_id) REFERENCES Research_papers(paper_id) ON DELETE CASCADE,
    FOREIGN KEY (area_id) REFERENCES Research_areas(area_id) ON DELETE CASCADE
);

CREATE TABLE User_access_rights (
    user_id INT,
    resource_type ENUM('Paper', 'User', 'Review'),
    access_level ENUM('Read', 'Write', 'Admin'),
    PRIMARY KEY (user_id, resource_type),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Function to Check User Permissions
DELIMITER //
CREATE FUNCTION CheckUserAccess(userId INT, resourceType ENUM('Paper', 'User', 'Review'), requiredLevel ENUM('Read', 'Write', 'Admin'))
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE accessLevel ENUM('Read', 'Write', 'Admin');
    SELECT access_level INTO accessLevel
    FROM User_access_rights
    WHERE user_id = userId AND resource_type = resourceType;

    RETURN (accessLevel >= requiredLevel);
END //
DELIMITER ;

-- Procedure for Adding a Research Paper with Validation
DELIMITER //

CREATE PROCEDURE AddResearchPaper(
    IN p_title VARCHAR(255),
    IN p_abstract TEXT,
    IN p_doi VARCHAR(50),
    IN p_journal_name VARCHAR(100),
    IN p_publication_year INT,
    IN p_pdf_data LONGBLOB,
    IN p_keywords JSON,
    IN p_authors JSON,
    IN p_areas JSON
)
BEGIN
    DECLARE paper_id INT;
    DECLARE keyword VARCHAR(50);
    DECLARE author_id INT;
    DECLARE area_id INT;
    DECLARE keyword_count INT;
    DECLARE author_count INT;
    DECLARE area_count INT;
    DECLARE author_exists INT DEFAULT 0;

    -- Insert research paper
    INSERT INTO Research_papers (title, abstract, doi, journal_name, publication_year, pdf_data)
    VALUES (p_title, p_abstract, p_doi, p_journal_name, p_publication_year, p_pdf_data);

    -- Get the last inserted paper ID
    SET paper_id = LAST_INSERT_ID();

    -- Insert keywords
    SET keyword_count = JSON_LENGTH(p_keywords);
    SET @i = 0;
    WHILE @i < keyword_count DO
        SET keyword = JSON_UNQUOTE(JSON_EXTRACT(p_keywords, CONCAT('$[', @i, ']')));
        INSERT INTO Paper_keywords (paper_id, keyword) VALUES (paper_id, keyword);
        SET @i = @i + 1;
    END WHILE;

    -- Insert authors
    SET author_count = JSON_LENGTH(p_authors);
    SET @j = 0;
    WHILE @j < author_count DO
        SET author_id = JSON_UNQUOTE(JSON_EXTRACT(p_authors, CONCAT('$[', @j, ']')));

        -- Check if author exists
        SELECT COUNT(*) INTO author_exists FROM Users WHERE user_id = author_id;
        IF author_exists = 0 THEN
            -- Insert new author if not exists
            INSERT INTO Users (user_id, username, password, role, email, affiliation)
            VALUES (author_id, CONCAT('author', author_id), 'default_password', 'Researcher', CONCAT('author', author_id, '@example.com'), 'Unknown Affiliation');
        END IF;

        -- Insert into Paper_authors table
        INSERT INTO Paper_authors (paper_id, author_id) VALUES (paper_id, author_id);
        SET @j = @j + 1;
    END WHILE;

    -- Insert research areas
    SET area_count = JSON_LENGTH(p_areas);
    SET @k = 0;
    WHILE @k < area_count DO
        SET area_id = JSON_UNQUOTE(JSON_EXTRACT(p_areas, CONCAT('$[', @k, ']')));
        INSERT INTO Paper_research_areas (paper_id, area_id) VALUES (paper_id, area_id);
        SET @k = @k + 1;
    END WHILE;
END //

DELIMITER ;

-- Trigger to Cascade Delete Related Records in Other Tables
DELIMITER //
CREATE TRIGGER BeforeDeleteResearchPaper
BEFORE DELETE ON Research_papers
FOR EACH ROW
BEGIN
    DELETE FROM Paper_reviews WHERE paper_id = OLD.paper_id;
    DELETE FROM Paper_keywords WHERE paper_id = OLD.paper_id;
    DELETE FROM Paper_authors WHERE paper_id = OLD.paper_id;
    DELETE FROM Paper_research_areas WHERE paper_id = OLD.paper_id;
END //
DELIMITER ;