# 📚 Library Management System (Python)

A simple command-line library system written in **Python**. It is a Python version of my college project, the *E-Library Management System* (originally built in Java + MySQL at UIT, HPU Shimla).

A librarian can register students, add books, issue and return books, and view statistics. Everything is saved in a local database file, so there is nothing extra to install.

## ✨ Features
- 🔐 Admin login (3 attempts)
- 🎓 Register new students (ID, name, father's name, course, branch, year)
- 📖 Add new books (ID, name, publisher, publish year)
- 📤 Issue a book: checks that the book and student exist, and that the book is not already issued. Due date is set automatically (7 days)
- 📥 Return a book: shows issue and due date, and calculates a fine for late returns (Rs 2 per day)
- 📊 Statistics: total books and students, currently issued, overdue, returned, plus issue and return tables
- 🚪 Log out

## 🛠️ Built With
- Python 3
- SQLite (built into Python, no installation needed)

## 🚀 How to Run
1. Install Python 3 from python.org.
2. Download `library_management.py`.
3. Set your own admin password (recommended). In the terminal:
   - Windows: `set LMS_PASSWORD=yourpassword`
   - Mac/Linux: `export LMS_PASSWORD=yourpassword`
4. Run: `python library_management.py`
5. Log in with username `Admin` and your password.

If you don't set `LMS_PASSWORD`, the default password is `change-me`.

## 📂 Files
- `library_management.py`: the whole program
- `library.db`: created automatically the first time you run it

## 🔮 Future Improvements
- Search books by title or author
- Graphical interface 
- Multiple users (librarian and student logins)
- Export reports to Excel

## 👩‍💻 About
Made by Anandita. This started as a team project with Vishakha Thakur and Ankita, and this Python version was rebuilt from the original project report.
