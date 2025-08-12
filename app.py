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
    
    try:
        if date:
            # Get events for specific date
            events = repo.get_by_date(date)
        elif year and month:
            # Get events for specific month
            events = repo.get_by_month(year, month)
        else:
            # Get all events if no parameters provided
            events = repo.get_all()
        
        # Convert to list of dictionaries
        events_list = [event.to_dict() for event in events]
        return jsonify(events_list)
        
    except Exception as e:
        app.logger.error(f"Error retrieving events: {str(e)}")
        return jsonify({'error': 'Failed to retrieve events'}), 500

@app.route('/events', methods=['POST'])
def create_event():
    """API endpoint to create a new event"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create event from dictionary data
        event = create_event_from_dict(data)
        
        # Validate event data
        validation_errors = event.validate()
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        # Create event using repository
        event_id = repo.create(event)
        
        return jsonify({
            'id': event_id, 
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
        
    except ValueError as e:
        app.logger.error(f"Validation error creating event: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error creating event: {str(e)}")
        return jsonify({'error': 'Failed to create event'}), 500

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




