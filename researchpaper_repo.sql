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
CREATE PROCEDURE AddResearchPaper (
    IN p_title VARCHAR(255),
    IN p_abstract TEXT,
    IN p_doi VARCHAR(50),
    IN p_journal_name VARCHAR(100),
    IN p_publication_year INT,
    IN p_pdf_data LONGBLOB,
    IN p_keywords JSON,
    IN p_authors JSON,
    IN p_research_areas JSON
)
BEGIN
    DECLARE paperId INT;

    -- Insert main paper record
    INSERT INTO Research_papers (title, abstract, doi, journal_name, publication_year, pdf_data)
    VALUES (p_title, p_abstract, p_doi, p_journal_name, p_publication_year, p_pdf_data);
    
    SET paperId = LAST_INSERT_ID();

    -- Insert keywords
    DECLARE keyword VARCHAR(50);
    DECLARE keywordCursor CURSOR FOR SELECT value FROM JSON_TABLE(p_keywords, '$[*]' COLUMNS(value VARCHAR(50) PATH '$'));

    OPEN keywordCursor;
    FETCH keywordCursor INTO keyword;
    WHILE keyword IS NOT NULL DO
        INSERT INTO Paper_keywords (paper_id, keyword) VALUES (paperId, keyword);
        FETCH keywordCursor INTO keyword;
    END WHILE;
    CLOSE keywordCursor;

    -- Insert authors
    DECLARE authorId INT;
    DECLARE authorCursor CURSOR FOR SELECT value FROM JSON_TABLE(p_authors, '$[*]' COLUMNS(value INT PATH '$'));

    OPEN authorCursor;
    FETCH authorCursor INTO authorId;
    WHILE authorId IS NOT NULL DO
        INSERT INTO Paper_authors (paper_id, author_id) VALUES (paperId, authorId);
        FETCH authorCursor INTO authorId;
    END WHILE;
    CLOSE authorCursor;

    -- Insert research areas
    DECLARE areaId INT;
    DECLARE areaCursor CURSOR FOR SELECT value FROM JSON_TABLE(p_research_areas, '$[*]' COLUMNS(value INT PATH '$'));

    OPEN areaCursor;
    FETCH areaCursor INTO areaId;
    WHILE areaId IS NOT NULL DO
        INSERT INTO Paper_research_areas (paper_id, area_id) VALUES (paperId, areaId);
        FETCH areaCursor INTO areaId;
    END WHILE;
    CLOSE areaCursor;

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