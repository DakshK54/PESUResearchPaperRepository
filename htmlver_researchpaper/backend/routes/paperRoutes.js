const express = require('express');
const router = express.Router();
const db = require('../db');

// Add Research Paper
router.post('/add', (req, res) => {
    const { title, abstract, doi, journal_name, publication_year, pdf_data, keywords, authors, areas } = req.body;

    db.query('CALL AddResearchPaper(?, ?, ?, ?, ?, ?, ?, ?, ?)', [title, abstract, doi, journal_name, publication_year, pdf_data, keywords, authors, areas], (err) => {
        if (err) return res.status(500).send(err);
        res.send("Research paper added successfully");
    });
});

// Get All Research Papers
router.get('/', (req, res) => {
    db.query('SELECT * FROM Research_papers WHERE approval_status = "Approved"', (err, results) => {
        if (err) return res.status(500).send(err);
        res.json(results);
    });
});

module.exports = router;