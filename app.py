from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import calendar
import os
from models import EventRepository, Event, create_event_from_dict, event_repository

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Use the repository from models
repo = event_repository

@app.route('/')
def index():
    """Main calendar view"""
    # Get current date or date from query parameters
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Handle month/year navigation
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    # Get calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Get events for the current month using repository
    events = repo.get_events_grouped_by_date(year, month)
    
    return render_template('calendar.html', 
                         calendar_data=cal,
                         year=year,
                         month=month,
                         month_name=month_name,
                         events=events,
                         today=datetime.now().date())

@app.route('/events')
def get_events():
    """API endpoint to get events for a specific date or month"""
    date = request.args.get('date')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    conn = get_db_connection()
    
    if date:
        # Get events for specific date
        events = conn.execute(
            'SELECT * FROM events WHERE date = ? ORDER BY time',
            (date,)
        ).fetchall()
    elif year and month:
        # Get events for specific month
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        events = conn.execute(
            'SELECT * FROM events WHERE date >= ? AND date < ? ORDER BY date, time',
            (start_date, end_date)
        ).fetchall()
    else:
        events = []
    
    conn.close()
    
    # Convert to list of dictionaries
    events_list = []
    for event in events:
        events_list.append({
            'id': event['id'],
            'title': event['title'],
            'description': event['description'],
            'date': event['date'],
            'time': event['time']
        })
    
    return jsonify(events_list)

@app.route('/events', methods=['POST'])
def create_event():
    """API endpoint to create a new event"""
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('date'):
        return jsonify({'error': 'Title and date are required'}), 400
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO events (title, description, date, time) VALUES (?, ?, ?, ?)',
        (data['title'], data.get('description', ''), data['date'], data.get('time', ''))
    )
    conn.commit()
    event_id = conn.lastrowid
    conn.close()
    
    return jsonify({'id': event_id, 'message': 'Event created successfully'}), 201

@app.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """API endpoint to delete an event"""
    conn = get_db_connection()
    result = conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    
    if result.rowcount == 0:
        return jsonify({'error': 'Event not found'}), 404
    
    return jsonify({'message': 'Event deleted successfully'})

@app.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """API endpoint to update an event"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    conn = get_db_connection()
    
    # Check if event exists
    event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
    if not event:
        conn.close()
        return jsonify({'error': 'Event not found'}), 404
    
    # Update event
    conn.execute(
        'UPDATE events SET title = ?, description = ?, date = ?, time = ? WHERE id = ?',
        (
            data.get('title', event['title']),
            data.get('description', event['description']),
            data.get('date', event['date']),
            data.get('time', event['time']),
            event_id
        )
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Event updated successfully'})

def get_events_for_month(year, month):
    """Helper function to get events for a specific month"""
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"
    
    conn = get_db_connection()
    events = conn.execute(
        'SELECT * FROM events WHERE date >= ? AND date < ? ORDER BY date, time',
        (start_date, end_date)
    ).fetchall()
    conn.close()
    
    # Group events by date
    events_by_date = {}
    for event in events:
        date = event['date']
        if date not in events_by_date:
            events_by_date[date] = []
        events_by_date[date].append({
            'id': event['id'],
            'title': event['title'],
            'description': event['description'],
            'time': event['time']
        })
    
    return events_by_date

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)


