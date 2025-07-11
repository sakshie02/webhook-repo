from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

# Simple in-memory storage instead of MongoDB
events_storage = []

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
    
    event_data = {
        'author': author,
        'action': 'PUSH',
        'to_branch': branch,
        'from_branch': branch,
        'timestamp': timestamp.isoformat()
    }
    
    events_storage.append(event_data)

def handle_pull_request_event(payload):
    if payload['action'] == 'opened':
        author = payload['pull_request']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = datetime.utcnow()
        
        event_data = {
            'author': author,
            'action': 'PULL_REQUEST',
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp.isoformat()
        }
        
        events_storage.append(event_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    return jsonify(events_storage[-20:])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
