# Replace MongoDB code with simple list storage
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
        'timestamp': timestamp.isoformat()
    }
    
    events_storage.append(event_data)

@app.route('/api/events')
def get_events():
    return jsonify(events_storage[-20:])  # Last 20 events
