import sqlite3

from datetime import datetime

# =========================================
# DATABASE NAME
# =========================================
DB_NAME = "students.db"


# =========================================
# INITIALIZE DATABASE
# =========================================
def init_db():

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    # =====================================
    # ATTENDANCE TABLE
    # =====================================
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            date TEXT,

            time TEXT,

            status TEXT

        )
        """
    )

    # =====================================
    # USERS TABLE
    # =====================================
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE,

            password TEXT,

            role TEXT

        )
        """
    )

    conn.commit()

    conn.close()

    print("Database Initialized")


# =========================================
# REGISTER USER
# =========================================
def register_user(
    username,
    password,
    role
):

    try:

        conn = sqlite3.connect(DB_NAME)

        c = conn.cursor()

        c.execute(
            """
            INSERT INTO users(

                username,
                password,
                role

            )
            VALUES (?, ?, ?)
            """,
            (
                username,
                password,
                role
            )
        )

        conn.commit()

        conn.close()

        return True

    except Exception as e:

        print(
            f"Register Error: {e}"
        )

        return False


# =========================================
# LOGIN USER
# =========================================
def login_user(
    username,
    password,
    role
):

    try:

        conn = sqlite3.connect(DB_NAME)

        c = conn.cursor()

        c.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            AND password=?
            AND role=?
            """,
            (
                username,
                password,
                role
            )
        )

        user = c.fetchone()

        conn.close()

        return user

    except Exception as e:

        print(
            f"Login Error: {e}"
        )

        return None


# =========================================
# MARK ATTENDANCE
# =========================================
def mark_attendance(
    name,
    status="Present"
):

    try:

        now = datetime.now()

        date = now.strftime(
            "%Y-%m-%d"
        )

        time = now.strftime(
            "%H:%M:%S"
        )

        conn = sqlite3.connect(DB_NAME)

        c = conn.cursor()

        # =================================
        # CHECK EXISTING ATTENDANCE
        # =================================
        c.execute(
            """
            SELECT *
            FROM attendance
            WHERE name=? AND date=?
            """,
            (name, date)
        )

        existing = c.fetchone()

        # =================================
        # NEW ATTENDANCE
        # =================================
        if not existing:

            c.execute(
                """
                INSERT INTO attendance(

                    name,
                    date,
                    time,
                    status

                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    date,
                    time,
                    status
                )
            )

            conn.commit()

            conn.close()

            return "marked"

        # =================================
        # ALREADY MARKED
        # =================================
        else:

            conn.close()

            return "already_marked"

    except Exception as e:

        print(
            f"Attendance Error: {e}"
        )

        return "error"


# =========================================
# GET STUDENT ATTENDANCE
# =========================================
def get_student_attendance(name):

    try:

        conn = sqlite3.connect(DB_NAME)

        c = conn.cursor()

        c.execute(
            """
            SELECT *
            FROM attendance
            WHERE name=?
            ORDER BY id DESC
            """,
            (name,)
        )

        data = c.fetchall()

        conn.close()

        return data

    except Exception as e:

        print(
            f"Student Fetch Error: {e}"
        )

        return []


# =========================================
# GET ALL ATTENDANCE
# =========================================
def get_all_attendance():

    try:

        conn = sqlite3.connect(DB_NAME)

        c = conn.cursor()

        c.execute(
            """
            SELECT *
            FROM attendance
            ORDER BY id DESC
            """
        )

        data = c.fetchall()

        conn.close()

        return data

    except Exception as e:

        print(
            f"Fetch Error: {e}"
        )

        return []