# samples-for-app

A sample web application demonstrating how to upload an entire folder with all its contents.

## Features

- 📁 Upload entire folders with nested directory structures
- 🖱️ Drag and drop support for easy folder selection
- 📊 View previously uploaded files
- 🎨 Modern, responsive UI
- ⚡ Real-time upload progress

## Installation

1. Clone this repository:
```bash
git clone https://github.com/trentbecknell/samples-for-app.git
cd samples-for-app
```

2. Install dependencies:
```bash
npm install
```

## Usage

1. Start the server:
```bash
npm start
```

2. Open your browser and navigate to:
```
http://localhost:3000
```

3. Click "Select Folder" or drag and drop a folder onto the upload area

4. Review the selected files and click "Upload Files"

## How It Works

This application uses:
- **Express.js** - Web server framework
- **Multer** - Middleware for handling multipart/form-data (file uploads)
- **HTML5 File API** - For folder selection and drag-and-drop

The server preserves the folder structure when saving uploaded files.

## API Endpoints

- `GET /` - Serves the main HTML page
- `POST /upload` - Handles folder upload
- `GET /uploads` - Returns list of uploaded files

## License

ISC
