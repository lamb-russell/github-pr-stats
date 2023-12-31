

from flask import Flask, jsonify, render_template, request
import sqlite3
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def init_db():
    """
    Initialize the database by creating necessary tables.
    """
    with sqlite3.connect('github_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_mapping (
                username TEXT PRIMARY KEY,
                team_name TEXT
            )
        ''')
        conn.commit()

# Initialize the database when the application starts
init_db()

def query_db(query, args=()):
    """
    Execute a query on the database.

    :param query: SQL query string
    :param args: Arguments for the SQL query
    :return: Query result
    """
    conn = sqlite3.connect('github_data.db')
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchall()
    conn.close()
    return result

def get_weekly_pr_stats():
    """
    Fetch weekly PR statistics.

    :return: Tuple containing counts of PRs for this week and older
    """
    today = datetime.now()
    last_week = today - timedelta(days=7)
    prs_this_week = query_db("SELECT COUNT(*) FROM pull_requests WHERE created_at >= ?", (last_week,))
    prs_older = query_db("SELECT COUNT(*) FROM pull_requests WHERE created_at < ?", (last_week,))
    return prs_this_week[0][0], prs_older[0][0]

def get_author_breakdown():
    """
    Fetch the breakdown of PRs by author.

    :return: List of tuples containing author and their PR count
    """
    query = """
        SELECT ifnull(tm.team_name,pr.author) as team_name, COUNT(*)
        FROM pull_requests pr
        LEFT JOIN team_mapping tm ON pr.author = tm.username
        GROUP BY ifnull(tm.team_name,pr.author)
    """
    return query_db(query)

def get_daily_pr_counts():
    """
    Fetch daily PR counts.

    :return: List of tuples containing date and PR count for that date
    """
    time_horizon = datetime.now() - timedelta(days=30)
    return query_db("SELECT DATE(created_at), COUNT(*) FROM pull_requests WHERE created_at >= ? GROUP BY DATE(created_at)", (time_horizon,))

def get_pull_requests():
    """
    Fetch all pull requests with additional details.

    :return: List of tuples containing pull request details
    """
    conn = sqlite3.connect('github_data.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pr.date, pr.count, pr.pr_id, pr.pr_url, pr.repo_name, pr.author, pr.pr_status, pr.created_at, pr.comments_count, pr.commits_count, pr.pr_title, tm.team_name
        FROM pull_requests pr
        LEFT JOIN team_mapping tm ON pr.author = tm.username
    """)
    prs = cursor.fetchall()
    conn.close()
    return prs

def transform_weekly_data_by_team(weekly_data_by_team):
    """
    Transform weekly data by team for visualization.

    :param weekly_data_by_team: Raw data of weekly stats by team
    :return: Transformed data suitable for chart visualization
    """
    transformed_data = {
        'labels': ['This Week', 'Older'],
        'datasets': []
    }

    COLORS = [
        '#4e79a7',  # Blue
        '#f28e2b',  # Orange
        '#e15759',  # Red
        '#76b7b2',  # Cyan
        '#59a14f',  # Green
        '#edc948',  # Yellow
        '#b07aa1',  # Purple
        '#ff9da7',  # Pink
        '#9c755f',  # Brown
        '#bab0ac',  # Grey
        '#6b4c9a',  # Indigo
        '#ff6e54',  # Coral
        '#d37295',  # Mauve
        '#c5a5cf',  # Lavender
        '#8cd17d',  # Lime Green
        '#499894',  # Teal
        '#86bcb6',  # Turquoise
        '#f9c784',  # Peach
        '#f7a35c',  # Dark Orange
        '#a0cbe8'  # Sky Blue
    ]

    color_index = 0
    for team_name, this_week_count, older_count in weekly_data_by_team:
        dataset = {
            'label': team_name,
            'data': [this_week_count, older_count],
            'backgroundColor': COLORS[color_index % len(COLORS)]
        }
        transformed_data['datasets'].append(dataset)
        color_index += 1

    return transformed_data

@app.route('/data')
def data():
    """
    Endpoint to fetch pull request data.
    """
    prs = get_pull_requests()
    prs_list = [dict(zip(['date', 'count', 'pr_id', 'pr_url', 'repo_name', 'author', 'pr_status', 'created_at', 'comments_count', 'commits_count', 'pr_title', 'team_name'], pr)) for pr in prs]
    return jsonify(prs_list)

@app.route('/')
def index():
    """
    Render the main dashboard page.
    """
    return render_template('index.html')

@app.route('/data/weekly-stats')
def weekly_stats():
    """
    Endpoint for weekly PR statistics.
    """
    prs_this_week, prs_older = get_weekly_pr_stats()
    data = {
        'labels': ['This Week', 'Older'],
        'datasets': [{
            'label': 'PR Counts',
            'data': [prs_this_week, prs_older],
            'backgroundColor': ['#4e79a7', '#f28e2b']
        }]
    }
    return jsonify(data)

@app.route('/data/weekly-stats-by-team')
def weekly_stats_by_team():
    """
    Endpoint for weekly PR statistics by team.
    """
    today = datetime.now()
    last_week = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    query = """
        SELECT ifnull(tm.team_name,pr.author) as team_name, 
               SUM(CASE WHEN pr.created_at >= ? THEN 1 ELSE 0 END) as this_week_count,
               SUM(CASE WHEN pr.created_at < ? THEN 1 ELSE 0 END) as older_count
        FROM pull_requests pr
        LEFT JOIN team_mapping tm ON pr.author = tm.username
        GROUP BY ifnull(tm.team_name,pr.author)
    """
    weekly_data_by_team = query_db(query, (last_week, last_week))
    transformed_data = transform_weekly_data_by_team(weekly_data_by_team)

    return jsonify(transformed_data)

@app.route('/data/author-breakdown')
def author_breakdown():
    """
    Endpoint for author breakdown.
    """
    author_data = get_author_breakdown()
    labels = [item[0] for item in author_data]
    data_values = [item[1] for item in author_data]

    colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948', '#b07aa1', '#ff9da7', '#9c755f', '#bab0ac']

    if len(labels) > len(colors):
        colors *= (len(labels) // len(colors)) + 1

    data = {
        'labels': labels,
        'datasets': [{
            'label': 'PRs by Author',
            'data': data_values,
            'backgroundColor': colors[:len(labels)]
        }]
    }
    return jsonify(data)

@app.route('/data/daily-counts')
def daily_counts():
    """
    Endpoint for daily PR counts.
    """
    daily_data = get_daily_pr_counts()
    labels = [item[0] for item in daily_data]
    data_values = [item[1] for item in daily_data]

    data = {
        'labels': labels,
        'datasets': [{
            'label': 'Daily PR Counts',
            'data': data_values,
            'fill': False,
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        }]
    }
    return jsonify(data)

@app.route('/add-team-mapping', methods=['POST'])
def add_team_mapping():
    """
    Endpoint to add a team mapping.
    """
    data = request.json
    username = data['username']
    team_name = data['teamName']
    with sqlite3.connect('github_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO team_mapping (username, team_name) VALUES (?, ?)', (username, team_name))
        conn.commit()

    return jsonify({'status': 'success', 'message': 'Team mapping added'})

if __name__ == '__main__':
    app.run(debug=True)
