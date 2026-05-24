# Library Management System - Installation & Setup Guide

## Prerequisites

Ensure you have the following installed:
- **Python 3.8+** - Download from [python.org](https://www.python.org/)
- **Node.js 14+** - Download from [nodejs.org](https://nodejs.org/)
- **Git** - Download from [git-scm.com](https://git-scm.com/)
- **SQLite3** - Usually pre-installed

Verify installations:
```bash
python --version
node --version
npm --version
git --version
```

---

## Step 1: Navigate to the Project

```powershell
# Windows PowerShell — use the full path to the inner project folder
cd "C:\Users\Administrator\Desktop\AFDE_May26_LMS\AFDE_May26_LMS"
```

> **Note:** The project is inside a double-nested folder
> (`AFDE_May26_LMS\AFDE_May26_LMS\`).
> Always `cd` to the **inner** folder before running backend or frontend commands.

---

## Step 2: Backend Setup

### 2.1 Create Virtual Environment

```powershell
# Windows PowerShell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
cd backend
python -m venv venv
source venv/bin/activate
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.111.0 uvicorn-0.29.0 sqlalchemy-2.0.30 pydantic-2.7.1
```

### 2.3 Verify Backend

```bash
python -c "import fastapi; import sqlalchemy; print('✅ Dependencies ready')"
```

### 2.4 Initialize Database

The database is auto-created on first run, but you can seed it manually:

```bash
# Using SQLite directly
sqlite3 ../database/library.db < ../database/schema.sql

# Or Python will auto-create it when you start the server
```

### 2.5 Start Backend Server

```bash
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Started server process [1234]
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Backend is ready at**: `http://localhost:8000`
**Swagger Docs**: `http://localhost:8000/docs`
**ReDoc Docs**: `http://localhost:8000/redoc`

**Keep this terminal running!**

---

## Step 3: Frontend Setup

### 3.1 Install Dependencies

Open a **new terminal** window:

```bash
cd frontend
npm install
```

This will install React, Axios, and other dependencies.

**Expected:** Completes without errors.

### 3.2 Start Frontend Server

```bash
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view lms-frontend in the browser.

Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000
```

**Frontend is ready at**: `http://localhost:3000`

---

## Step 4: Access the Application

### 4.1 Open Browser

Navigate to: **`http://localhost:3000`**

You should see the Library Management System dashboard.

### 4.2 Test the Application

1. **Dashboard** - View statistics (should show 5 sample books, 3 borrowers)
2. **Books Management** - Click "Add Book" to create a new book
3. **Borrowers** - Register a new borrower
4. **Transactions** - Borrow a book and return it
5. **Search** - Search for books by title, author, or category

---

## Step 5: Test API Endpoints

### 5.1 Using Swagger UI

Go to: `http://localhost:8000/docs`

- Click on any endpoint (e.g., `GET /books/`)
- Click "Try it out"
- Click "Execute"
- View the response

### 5.2 Using Postman

1. Download [Postman](https://www.postman.com/downloads/)
2. Create a new collection: "Library Management System"
3. Create requests:

**GET All Books:**
```
GET http://localhost:8000/books/
```

**Create Book:**
```
POST http://localhost:8000/books/
Content-Type: application/json

{
  "title": "Django for Beginners",
  "author": "William Vincent",
  "category": "Programming",
  "isbn": "9781491905739"
}
```

**Borrow Book:**
```
POST http://localhost:8000/borrow
Content-Type: application/json

{
  "book_id": 1,
  "borrower_id": 1
}
```

---

## Troubleshooting

### Issue: Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt  # Reinstall
```

---

### Issue: Port 8000 already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Kill process on port 8000
# On macOS/Linux
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# On Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Or use different port
uvicorn main:app --port 8001
```

---

### Issue: Frontend can't connect to API

**Error:** Network error when trying to fetch

**Solution:**
1. Verify backend is running on `http://localhost:8000`
2. Check browser console for CORS errors
3. Clear browser cache: Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
4. Restart both frontend and backend

---

### Issue: Database file corrupted

**Error:** `database disk image is malformed`

**Solution:**
```bash
cd backend
rm library.db  # Delete corrupted database
# Backend will auto-create new one on next start
python main.py
```

---

## Project Layout

```
AFDE_May26_LMS/
│
├── backend/
│   ├── main.py           ← START HERE (Backend server)
│   ├── requirements.txt
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── routers/
│   │   ├── books.py
│   │   ├── borrowers.py
│   │   └── transactions.py
│   ├── library.db        ← (Auto-created)
│   └── venv/             ← Virtual environment
│
├── frontend/
│   ├── package.json
│   ├── public/
│   ├── src/
│   │   ├── App.js        ← Main component
│   │   ├── App.css
│   │   ├── pages/
│   │   ├── components/
│   │   └── services/
│   ├── node_modules/     ← (Auto-created)
│   └── package-lock.json ← (Auto-created)
│
├── database/
│   └── schema.sql        ← Database schema
│
└── README.md
```

---

## Useful Commands

### Backend

```bash
# Start server
uvicorn main:app --reload

# Start on different port
uvicorn main:app --port 8001

# Without auto-reload (production)
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Start development server
npm start

# Build for production
npm run build

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database

```bash
# Connect to SQLite database
sqlite3 backend/library.db

# View tables
.tables

# View schema
.schema

# Exit
.quit
```

---

## Next Steps

After setup:

1. **Explore the API**: Visit `http://localhost:8000/docs`
2. **Test all CRUD operations** using the UI
3. **Create sample data** through the dashboard
4. **Test search functionality**
5. **Review logs** in terminal windows

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review error messages in terminal
3. Check browser console (F12) for frontend errors
4. Verify all prerequisites are installed
5. Ensure ports 3000 and 8000 are available

---

## Production Deployment

For deploying to production:

1. Install Gunicorn: `pip install gunicorn`
2. Run backend: `gunicorn -w 4 main:app`
3. Build frontend: `npm run build`
4. Deploy static files to web server
5. Set up reverse proxy (Nginx/Apache)
6. Use PostgreSQL instead of SQLite

---

**Setup Complete! Happy coding! 🚀**
