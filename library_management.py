"""
E-Library Management System (Python version)

A simple command-line library system. It lets a librarian register students,
add books, issue and return books, and view statistics.
Data is stored in a local SQLite database file (library.db), so nothing
extra needs to be installed.

Run it with:  python library_management.py
"""

import os
import sqlite3
from datetime import date, timedelta

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")
LOAN_DAYS = 7          # how many days a book can be kept
FINE_PER_DAY = 2       # fine (in rupees) for every late day

ADMIN_USER = "Admin"
# Change this password, or set the LMS_PASSWORD environment variable.
ADMIN_PASSWORD = os.environ.get("LMS_PASSWORD", "change-me")


# ---------- Database ----------

def get_connection():
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with get_connection() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS student (
                student_id  TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                father_name TEXT,
                course      TEXT,
                branch      TEXT,
                year        TEXT
            );
            CREATE TABLE IF NOT EXISTS book (
                book_id      TEXT PRIMARY KEY,
                name         TEXT NOT NULL,
                publisher    TEXT,
                publish_year TEXT
            );
            CREATE TABLE IF NOT EXISTS issue (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id     TEXT NOT NULL,
                student_id  TEXT NOT NULL,
                issue_date  TEXT NOT NULL,
                due_date    TEXT NOT NULL,
                return_date TEXT,
                returned    TEXT NOT NULL DEFAULT 'NO'
            );
            """
        )


# ---------- Small helpers ----------

def ask(prompt):
    """Ask for text and strip extra spaces."""
    return input(prompt).strip()


def ask_required(prompt):
    while True:
        value = ask(prompt)
        if value:
            return value
        print("This field cannot be empty.")


def choose(prompt, options):
    print(prompt)
    for number, option in enumerate(options, start=1):
        print(f"  {number}. {option}")
    while True:
        answer = ask("Enter number: ")
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        print("Please choose a valid number.")


def print_table(headers, rows):
    if not rows:
        print("  (no records)")
        return
    rows = [[str(cell) for cell in row] for row in rows]
    widths = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    line = "  " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(line)
    print("  " + "-+-".join("-" * w for w in widths))
    for row in rows:
        print("  " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))


def heading(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


# ---------- Features ----------

def login():
    heading("E-LIBRARY MANAGEMENT SYSTEM - LOGIN")
    for _ in range(3):
        user = ask("Username: ")
        password = ask("Password: ")
        if user == ADMIN_USER and password == ADMIN_PASSWORD:
            print("Login successful.")
            return True
        print("Incorrect username or password.")
    print("Too many failed attempts.")
    return False


def add_student():
    heading("NEW STUDENT REGISTRATION")
    student_id = ask_required("Student ID: ")
    name = ask_required("Name: ")
    father_name = ask_required("Father's name: ")
    course = choose("Course:", ["B.Tech"])
    branch = choose("Branch:", ["CSE", "IT", "ECE", "CE", "EE"])
    year = choose("Year:", ["1st", "2nd", "3rd", "4th"])
    try:
        with get_connection() as con:
            con.execute(
                "INSERT INTO student VALUES (?, ?, ?, ?, ?, ?)",
                (student_id, name, father_name, course, branch, year),
            )
        print("Saved successfully.")
    except sqlite3.IntegrityError:
        print("Student already exists.")


def add_book():
    heading("NEW BOOK ENTRY")
    book_id = ask_required("Book ID: ")
    name = ask_required("Book name: ")
    publisher = ask_required("Publisher: ")
    publish_year = ask_required("Publish year: ")
    try:
        with get_connection() as con:
            con.execute(
                "INSERT INTO book VALUES (?, ?, ?, ?)",
                (book_id, name, publisher, publish_year),
            )
        print("Saved successfully.")
    except sqlite3.IntegrityError:
        print("Book ID already exists.")


def issue_book():
    heading("ISSUE BOOK")
    book_id = ask_required("Book ID: ")
    student_id = ask_required("Student ID: ")
    with get_connection() as con:
        book = con.execute("SELECT * FROM book WHERE book_id = ?", (book_id,)).fetchone()
        if not book:
            print("Incorrect Book ID.")
            return
        student = con.execute(
            "SELECT * FROM student WHERE student_id = ?", (student_id,)
        ).fetchone()
        if not student:
            print("Incorrect Student ID.")
            return
        already = con.execute(
            "SELECT 1 FROM issue WHERE book_id = ? AND returned = 'NO'", (book_id,)
        ).fetchone()
        if already:
            print("This book is already issued to someone.")
            return
        today = date.today()
        due = today + timedelta(days=LOAN_DAYS)
        con.execute(
            "INSERT INTO issue (book_id, student_id, issue_date, due_date) VALUES (?, ?, ?, ?)",
            (book_id, student_id, today.isoformat(), due.isoformat()),
        )
    print(f"Book '{book['name']}' issued to {student['name']}.")
    print(f"Issue date: {today}   Due date: {due}")


def return_book():
    heading("RETURN BOOK")
    book_id = ask_required("Book ID: ")
    student_id = ask_required("Student ID: ")
    with get_connection() as con:
        row = con.execute(
            "SELECT * FROM issue WHERE book_id = ? AND student_id = ? AND returned = 'NO'",
            (book_id, student_id),
        ).fetchone()
        if not row:
            print("Book is not issued to this student.")
            return
        print(f"Issue date: {row['issue_date']}   Due date: {row['due_date']}")
        if ask("Return this book now? (y/n): ").lower() != "y":
            print("Cancelled.")
            return
        today = date.today()
        con.execute(
            "UPDATE issue SET returned = 'YES', return_date = ? WHERE id = ?",
            (today.isoformat(), row["id"]),
        )
    late_days = (today - date.fromisoformat(row["due_date"])).days
    print("Book successfully returned.")
    if late_days > 0:
        print(f"Returned {late_days} day(s) late. Fine: Rs {late_days * FINE_PER_DAY}")


def statistics():
    heading("STATISTICS")
    today = date.today().isoformat()
    with get_connection() as con:
        total_books = con.execute("SELECT COUNT(*) FROM book").fetchone()[0]
        total_students = con.execute("SELECT COUNT(*) FROM student").fetchone()[0]
        issued = con.execute(
            """SELECT issue.student_id, student.name, issue.book_id, book.name,
                      issue.issue_date, issue.due_date
               FROM issue
               JOIN student ON student.student_id = issue.student_id
               JOIN book ON book.book_id = issue.book_id
               WHERE issue.returned = 'NO'"""
        ).fetchall()
        returned = con.execute(
            """SELECT issue.student_id, student.name, issue.book_id, book.name,
                      issue.issue_date, issue.return_date
               FROM issue
               JOIN student ON student.student_id = issue.student_id
               JOIN book ON book.book_id = issue.book_id
               WHERE issue.returned = 'YES'"""
        ).fetchall()
    overdue = [r for r in issued if r[5] < today]

    print(f"Total books: {total_books}")
    print(f"Total students: {total_students}")
    print(f"Currently issued: {len(issued)}")
    print(f"Overdue: {len(overdue)}")
    print(f"Returned so far: {len(returned)}")

    print("\nIssue Details (not yet returned)")
    print_table(["Student ID", "Student", "Book ID", "Book", "Issued", "Due"], issued)
    print("\nReturn Details")
    print_table(["Student ID", "Student", "Book ID", "Book", "Issued", "Returned"], returned)


# ---------- Main menu ----------

def main():
    init_db()
    if not login():
        return
    actions = {
        "1": ("New Student", add_student),
        "2": ("New Book", add_book),
        "3": ("Issue Book", issue_book),
        "4": ("Return Book", return_book),
        "5": ("Statistics", statistics),
    }
    while True:
        heading("HOME")
        for key, (label, _) in actions.items():
            print(f"  {key}. {label}")
        print("  6. Log Out")
        choice = ask("Choose an option: ")
        if choice == "6":
            print("Logged out. Goodbye!")
            break
        if choice in actions:
            actions[choice][1]()
        else:
            print("Please choose a valid option.")


if __name__ == "__main__":
    main()
