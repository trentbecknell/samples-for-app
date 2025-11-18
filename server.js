const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 3000;

// Configure rate limiting for upload endpoint
const uploadLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 10, // Limit each IP to 10 requests per windowMs
    message: 'Too many upload requests from this IP, please try again later.'
});

// Configure rate limiting for general API endpoints
const apiLimiter = rateLimit({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 30, // Limit each IP to 30 requests per windowMs
    message: 'Too many requests from this IP, please try again later.'
});

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = './uploads';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        // Preserve the original path structure from webkitRelativePath
        const relativePath = file.originalname;
        const filePath = path.join('./uploads', relativePath);
        const dirPath = path.dirname(filePath);
        
        if (!fs.existsSync(dirPath)) {
            fs.mkdirSync(dirPath, { recursive: true });
        }
        
        cb(null, relativePath);
    }
});

const upload = multer({ storage: storage });

// Serve static files
app.use(express.static('public'));

// Handle folder upload
app.post('/upload', uploadLimiter, upload.array('files'), (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: 'No files uploaded' });
    }

    const uploadedFiles = req.files.map(file => ({
        originalName: file.originalname,
        size: file.size,
        path: file.path
    }));

    res.json({
        message: 'Folder uploaded successfully',
        fileCount: req.files.length,
        files: uploadedFiles
    });
});

// Get list of uploaded files
app.get('/uploads', apiLimiter, (req, res) => {
    const uploadDir = './uploads';
    if (!fs.existsSync(uploadDir)) {
        return res.json({ files: [] });
    }

    const getFiles = (dir, baseDir = dir) => {
        let files = [];
        const items = fs.readdirSync(dir);
        
        for (const item of items) {
            const fullPath = path.join(dir, item);
            const stat = fs.statSync(fullPath);
            
            if (stat.isDirectory()) {
                files = files.concat(getFiles(fullPath, baseDir));
            } else {
                files.push({
                    name: path.relative(baseDir, fullPath),
                    size: stat.size,
                    modified: stat.mtime
                });
            }
        }
        
        return files;
    };

    try {
        const files = getFiles(uploadDir);
        res.json({ files });
    } catch (error) {
        res.status(500).json({ error: 'Error reading uploads directory' });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
