import sqlite3

import os

DATABASE_PATH = 'github_data.db'
cwd = os.getcwd()
print(cwd)

# Connect to the SQLite database
conn = sqlite3.connect(DATABASE_PATH)

def validate_data():

    # Query the database to get the data
    query = """SELECT pr.date, pr.count, pr.pr_id, pr.pr_url, pr.repo_name, pr.author, pr.pr_status, pr.created_at, pr.comments_count, pr.commits_count, pr.pr_title, tm.team_name
        FROM pull_requests pr
        LEFT JOIN team_mapping tm ON pr.author = tm.username"""

    # Connect to the SQLite database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)

        # Fetch all records
        records = cursor.fetchall()

        if records:
            print("Data found in the database:")
            for row in records:
                print(row)
        else:
            print("No data found in the database.")


def validate_team_data():

    # Query the database to get the data
    query = "SELECT * FROM team_mapping"

    # Connect to the SQLite database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)

        # Fetch all records
        records = cursor.fetchall()

        if records:
            print("Data found in the database:")
            for row in records:
                print(row)
        else:
            print("No data found in the database.")

if __name__=="__main__":
    validate_data()
    validate_team_data()