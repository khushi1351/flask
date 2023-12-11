from flask import Flask, request, jsonify
from datetime import datetime
import requests  # Import requests library to make API requests

app = Flask(__name__)

# Function to fetch comments data from the API
def fetch_comments_data():
    api_url = "https://app.ylytic.com/ylytic/test"  # Replace this with your API endpoint
    response = requests.get(api_url)
    
    if response.status_code == 200:
        comments_data = response.json()
        return comments_data
    else:
        return []  # Return an empty list if there's an issue fetching data

def filter_comments(comments_data, author=None, at_from=None, at_to=None, like_from=None, like_to=None, reply_from=None, reply_to=None, search_text=None):
    # Ensure comments_data is a list of dictionaries
    if not isinstance(comments_data, dict) or 'comments' not in comments_data:
        print("Invalid comments data format:", comments_data)  # Debug print
        return []
    comments_list = comments_data['comments']
    filtered_comments = comments_list

    if author:
        filtered_comments = [c for c in filtered_comments if author.lower() in c.get("author", "").lower()]

    if at_from:
        at_from_date = datetime.strptime(at_from, "%m-%d-%Y")
        filtered_comments = [c for c in filtered_comments if parse_date(c.get("at", "")) >= at_from_date]

    if at_to:
        at_to_date = datetime.strptime(at_to, "%m-%d-%Y")
        filtered_comments = [c for c in filtered_comments if parse_date(c.get("at", "")) <= at_to_date]

    if like_from:
        filtered_comments = [c for c in filtered_comments if c.get("like", 0) >= int(like_from)]

    if like_to:
        filtered_comments = [c for c in filtered_comments if c.get("like", 0) <= int(like_to)]

    if reply_from:
        filtered_comments = [c for c in filtered_comments if c.get("reply", 0) >= int(reply_from)]

    if reply_to:
        filtered_comments = [c for c in filtered_comments if c.get("reply", 0) <= int(reply_to)]

    if search_text:
        filtered_comments = [c for c in filtered_comments if search_text.lower() in c.get("text", "").lower()]

    return filtered_comments

# Function to parse date strings with different formats
def parse_date(date_str):
    date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S %Z"]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    raise ValueError("Date format not recognized")

@app.route('/search', methods=['GET'])
def search_comments():
    search_author = request.args.get('search_author')
    at_from = request.args.get('at_from')
    at_to = request.args.get('at_to')
    like_from = request.args.get('like_from')
    like_to = request.args.get('like_to')
    reply_from = request.args.get('reply_from')
    reply_to = request.args.get('reply_to')
    search_text = request.args.get('search_text')

    # Fetch comments data from the API
    comments_data = fetch_comments_data()

    # Filter comments based on the provided parameters
    filtered_comments = filter_comments(
        comments_data,
        author=search_author,
        at_from=at_from,
        at_to=at_to,
        like_from=like_from,
        like_to=like_to,
        reply_from=reply_from,
        reply_to=reply_to,
        search_text=search_text
    )

    return jsonify(filtered_comments)

if __name__ == '__main__':
    app.run(debug=True)
