const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const router = express.Router();
const db = require('../db');  // Add this to handle database connection

// User Registration
router.post('/register', async (req, res) => {
    const { username, password, email, role, affiliation } = req.body;
    const hashedPassword = await bcrypt.hash(password, 10);

    const query = 'INSERT INTO Users (username, password, email, role, affiliation) VALUES (?, ?, ?, ?, ?)';
    db.query(query, [username, hashedPassword, email, role, affiliation], (err) => {
        if (err) return res.status(500).send(err);
        res.send("User registered successfully");
    });
});

// User Login
router.post('/login', (req, res) => {
    const { username, password } = req.body;
    db.query('SELECT * FROM Users WHERE username = ?', [username], async (err, results) => {
        if (err || results.length === 0) return res.status(400).send("User not found");
        
        const user = results[0];
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) return res.status(400).send("Incorrect password");

        const token = jwt.sign({ user_id: user.user_id }, process.env.JWT_SECRET);
        res.json({ token });
    });
});

module.exports = router;