import sqlite3
import pandas as pd


# =========================================
# DATABASE NAME
# =========================================
DB_NAME = "students.db"


# =========================================
# GET FULL DATA
# =========================================
def get_data():

    try:

        conn = sqlite3.connect(
            DB_NAME
        )

        query = """
            SELECT *
            FROM attendance
            ORDER BY id DESC
        """

        df = pd.read_sql_query(
            query,
            conn
        )

        conn.close()

        return df

    except Exception as e:

        print(
            f"Database Error: {e}"
        )

        return pd.DataFrame()


# =========================================
# TOTAL ATTENDANCE
# =========================================
def get_total_attendance(df):

    return len(df)


# =========================================
# TOTAL STUDENTS
# =========================================
def get_total_students(df):

    if df.empty:
        return 0

    return df["name"].nunique()


# =========================================
# TODAY ATTENDANCE
# =========================================
def get_today_attendance(df):

    if df.empty:
        return 0

    today = pd.Timestamp.today().strftime(
        "%Y-%m-%d"
    )

    return len(
        df[df["date"] == today]
    )


# =========================================
# ATTENDANCE PERCENTAGE
# =========================================
def get_attendance_percentage(df):

    total_students = (
        get_total_students(df)
    )

    today_attendance = (
        get_today_attendance(df)
    )

    if total_students == 0:
        return 0

    percentage = (
        today_attendance /
        total_students
    ) * 100

    return round(
        percentage,
        2
    )


# =========================================
# TOP ATTENDEES
# =========================================
def get_top_attendees(df):

    if df.empty:
        return pd.DataFrame()

    top = (
        df["name"]
        .value_counts()
        .reset_index()
    )

    top.columns = [
        "Student",
        "Attendance Count"
    ]

    return top


# =========================================
# DAILY TREND
# =========================================
def get_daily_trend(df):

    if df.empty:
        return pd.DataFrame()

    trend = (
        df.groupby("date")
        .size()
        .reset_index(name="count")
    )

    return trend


# =========================================
# WEEKDAY ANALYTICS
# =========================================
def get_weekday_stats(df):

    if df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(
        df["date"]
    )

    df["weekday"] = (
        df["date"]
        .dt.day_name()
    )

    weekday = (
        df.groupby("weekday")
        .size()
        .reset_index(name="count")
    )

    weekdays_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    weekday["weekday"] = pd.Categorical(
        weekday["weekday"],
        categories=weekdays_order,
        ordered=True
    )

    weekday = weekday.sort_values(
        "weekday"
    )

    return weekday


# =========================================
# MOST ACTIVE STUDENT
# =========================================
def get_best_student(df):

    if df.empty:
        return "No Data"

    return (
        df["name"]
        .value_counts()
        .idxmax()
    )


# =========================================
# LOWEST ATTENDANCE DAY
# =========================================
def get_lowest_day(df):

    weekday = get_weekday_stats(df)

    if weekday.empty:
        return "No Data"

    return (
        weekday.sort_values("count")
        .iloc[0]["weekday"]
    )


# =========================================
# AI INSIGHTS
# =========================================
def generate_ai_insights(df):

    if df.empty:

        return [
            "No attendance data available"
        ]

    insights = []

    # =====================================
    # BEST STUDENT
    # =====================================
    best_student = get_best_student(df)

    insights.append(
        f"🏆 Highest attendance: "
        f"{best_student}"
    )

    # =====================================
    # LOWEST DAY
    # =====================================
    low_day = get_lowest_day(df)

    insights.append(
        f"📉 Lowest attendance day: "
        f"{low_day}"
    )

    # =====================================
    # TOTAL STUDENTS
    # =====================================
    total_students = (
        get_total_students(df)
    )

    insights.append(
        f"👨‍🎓 Registered students: "
        f"{total_students}"
    )

    # =====================================
    # TODAY %
    # =====================================
    attendance_percent = (
        get_attendance_percentage(df)
    )

    insights.append(
        f"📈 Today's attendance: "
        f"{attendance_percent}%"
    )

    return insights