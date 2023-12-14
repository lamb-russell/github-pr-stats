

# GitHub Pull Requests Dashboard

## Overview

The GitHub Pull Requests Dashboard is a web application that visualizes pull request data from GitHub repositories. It provides insights into various metrics such as weekly PR statistics, author activity, and team contributions through interactive charts and tables.

## Project Structure

The project consists of several key components:

- `main.py`: Script to populate the local SQLite database with pull request information from GitHub.
- `app.py`: Flask application that serves as the backend API, providing data to the frontend.
- `static/script.js`: JavaScript file that powers the interactive charts on the web page.
- `static/styles.css`: Stylesheet for the web application, defining its visual appearance.
- `templates/index.html`: HTML template that lays out the structure of the web application.

## Environment Setup

Before running the application, set the following environment variables:

- `GITHUB_ORGANIZATION`: The GitHub organization or account that owns the repository.
- `GITHUB_REPO`: The repository of the account to analyze.
- `GITHUB_PERSONAL_TOKEN`: The GitHub personal access token with permissions to access the repository.

These variables are essential for the application to authenticate and interact with the GitHub API.


## Installation

To set up the GitHub Pull Requests Dashboard, follow these steps:


1. **Install Dependencies** (if applicable):
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   - Set up environment variables such as `GITHUB_PERSONAL_TOKEN`.
   - Configure database connections if necessary.

## Getting Started

To get the application up and running, follow these steps:

### 1. Populate the Database

Run `main.py` to fetch and store pull request data in your local database.

```bash
python main.py
```

### 2. Start the Flask Application

After populating the database, start the Flask app by running `app.py`.

```bash
python app.py
```

### 3. Access the Dashboard

Open a web browser and navigate to `http://localhost:5000` to view the dashboard.
