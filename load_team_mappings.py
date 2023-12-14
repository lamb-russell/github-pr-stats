import csv
import sqlite3

def load_team_mappings(csv_file, db_file):
    """
    Load team mappings from a CSV file into the SQLite database.

    :param csv_file: Path to the CSV file containing team mappings.
    :param db_file: Path to the SQLite database file.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create the team_mapping table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_mapping (
            username TEXT PRIMARY KEY,
            team_name TEXT
        )
    ''')

    # Open the CSV file and insert each row into the database
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute('INSERT OR IGNORE INTO team_mapping (username, team_name) VALUES (?, ?)', row)

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    load_team_mappings('team_mappings.csv', 'github_data.db')
