CREATE TABLE admin (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE candidates (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    party VARCHAR(100),
    image VARCHAR(100),
    votes INT DEFAULT 0
);

CREATE TABLE voter (
    voterid INT PRIMARY KEY,
    name VARCHAR(100),
    password VARCHAR(100),
    voted TINYINT DEFAULT 0  -- 0 = not voted, 1 = voted
);

-- Sample Data

INSERT INTO admin VALUES ('admin', 'admin123');

INSERT INTO candidates VALUES
(1, 'Vijay', 'TVK', 'vijay.jpg', 0),
(2, 'Stalin', 'DMK', 'stalin.jpg', 0),
(3, 'Palanisami', 'ADMK', 'eps.jpeg', 0)
(4, 'Seeman', 'NTK', 'seeman.jpeg', 0);

INSERT INTO voter VALUES
(101, 'Abi', 'Abi@123', 0),
(102, 'Annish', 'Annish@123', 0),
(103, 'Arun', 'Arun@123', 0);
-- Add more voters similarly
