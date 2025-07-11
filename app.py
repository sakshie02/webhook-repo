from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['github_webhooks']
collection = db['events']

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.json
        event_type = request.headers.get('X-GitHub-Event')
        
        if event_type == 'push':
            handle_push_event(payload)
        elif event_type == 'pull_request':
            handle_pull_request_event(payload)
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handle_push_event(payload):
    author = payload['pusher']['name']
    branch = payload['ref'].split('/')[-1]
    timestamp = datetime.utcnow()
    request_id = payload['head_commit']['id'] if payload.get('head_commit') else payload['after']
    
    event_data = {
        'request_id': request_id,
        'author': author,
        'action': 'PUSH',
        'from_branch': branch,
        'to_branch': branch,
        'timestamp': timestamp
    }
    
    collection.insert_one(event_data)

def handle_pull_request_event(payload):
    if payload['action'] == 'opened':
        author = payload['pull_request']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = datetime.utcnow()
        request_id = str(payload['pull_request']['id'])
        
        event_data = {
            'request_id': request_id,
            'author': author,
            'action': 'PULL_REQUEST',
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
        
        collection.insert_one(event_data)
    
    elif payload['action'] == 'closed' and payload['pull_request']['merged']:
        author = payload['pull_request']['merged_by']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = datetime.utcnow()
        request_id = str(payload['pull_request']['id'])
        
        event_data = {
            'request_id': request_id,
            'author': author,
            'action': 'MERGE',
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
        
        collection.insert_one(event_data)

def format_timestamp(timestamp):
    return timestamp.strftime('%d %B %Y - %I:%M %p UTC')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    events = list(collection.find({}).sort('timestamp', -1).limit(20))
    for event in events:
        event['_id'] = str(event['_id'])
        event['timestamp'] = event['timestamp'].isoformat()
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)