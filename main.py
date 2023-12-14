import requests
import sqlite3
from datetime import datetime
import os
import time
import logging

# Setup logging for debugging and tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_token():
    """
    Retrieve the GitHub API token from environment variables.

    :return: String containing the API token.
    :raises PermissionError: If the API token is not found in environment variables.
    """
    environment_variable = "GITHUB_PERSONAL_TOKEN"
    api_key = os.environ.get(environment_variable)
    if not api_key:
        raise PermissionError(f"API key missing in environment variable {environment_variable}")
    return api_key

# Initialize GitHub API token and repository details
GITHUB_TOKEN = get_token()
REPO_OWNER = os.environ.get('GITHUB_ORGANIZATION','<MY GITHUB ACCOUNT OR ORGANIZATION>')
REPO_NAME = os.environ.get('GITHUB_REPO','<MY GITHUB REPO REPO>')
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
logging.info(f"API URL: {API_URL}")

# Connect to SQLite database and set up the pull_requests table
conn = sqlite3.connect('github_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pull_requests (
        date TEXT, 
        count INTEGER, 
        pr_id INTEGER PRIMARY KEY, 
        pr_url TEXT,
        repo_name TEXT,
        author TEXT,
        pr_status TEXT,
        created_at TEXT,
        comments_count INTEGER,
        commits_count INTEGER,
        pr_title TEXT
    )
''')

def fetch_pull_requests(url, headers):
    """
    Fetch pull requests from the GitHub API and store them in the database.

    :param url: GitHub API URL for pull requests.
    :param headers: Headers to be used in the API request.
    :return: Total number of rows inserted into the database.
    """
    total_inserted = 0
    while url:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            pull_requests = response.json()
            for pr in pull_requests:
                # Fetch additional details for each PR
                pr_details_response = requests.get(pr['url'], headers=headers)
                if pr_details_response.status_code == 200:
                    pr_details = pr_details_response.json()
                    comments_count = pr_details['comments']
                    commits_count = pr_details['commits']
                else:
                    comments_count = commits_count = 0  # Default value in case of failure

                # Prepare data for insertion into the database
                pr_data = (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    len(pull_requests),
                    pr['id'],
                    pr['html_url'],
                    REPO_NAME,
                    pr['user']['login'],
                    pr['state'],
                    pr['created_at'],
                    comments_count,
                    commits_count,
                    pr['title']
                )
                cursor.execute("INSERT OR IGNORE INTO pull_requests (date, count, pr_id, pr_url, repo_name, author, pr_status, created_at, comments_count, commits_count, pr_title) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", pr_data)
                total_inserted += cursor.rowcount

            logging.info(f"Fetched {len(pull_requests)} pull requests.")

            # Check for pagination and move to the next page if available
            if 'next' in response.links:
                url = response.links['next']['url']
                logging.info(f"Moving to next page: {url}")
            else:
                url = None
        else:
            # Handle errors in fetching data
            error_message = response.json().get('message', 'No error message provided')
            logging.error(f"Failed to fetch data: {response.status_code} - {error_message}")
            if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
                # Handle GitHub API rate limiting
                reset_time = response.headers['X-RateLimit-Reset']
                wait_time = max(0, int(reset_time) - int(time.time()))
                logging.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds until reset.")
                time.sleep(wait_time)
            break

    return total_inserted

# Set up headers for GitHub API request
headers = {'Authorization': f'token {GITHUB_TOKEN}'}
total_inserted_rows = fetch_pull_requests(API_URL, headers)
logging.info(f"Total rows inserted: {total_inserted_rows}")

# Commit changes to the database and close the connection
conn.commit()
conn.close()
logging.info("Data fetching complete and database connection closed.")


