from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import calendar
import os
import sys
import logging
from models import EventRepository, Event, create_event_from_dict, event_repository, DatabaseManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calendar_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Use the repository from models
repo = event_repository

def init_database():
    """Initialize the database and handle any initialization errors"""
    try:
        app.logger.info("Initializing database...")
        
        # Create database manager instance to ensure database is initialized
        db_manager = DatabaseManager()
        
        # Test database connection
        test_connection = db_manager.get_connection()
        test_connection.close()
        
        app.logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        app.logger.error(f"Database initialization failed: {str(e)}")
        return False

def handle_database_error(operation, error):
    """Centralized database error handling"""
    error_msg = f"Database error during {operation}: {str(error)}"
    app.logger.error(error_msg)
    
    # Return appropriate error response based on operation type
    if "connection" in str(error).lower():
        return jsonify({'error': 'Database connection failed. Please try again later.'}), 503
    elif "constraint" in str(error).lower():
        return jsonify({'error': 'Data validation error. Please check your input.'}), 400
    else:
        return jsonify({'error': f'Database operation failed: {operation}'}), 500

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
    try:
        # Check if event exists first
        event = repo.get_by_id(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Delete the event
        success = repo.delete(event_id)
        
        if success:
            return jsonify({'message': 'Event deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete event'}), 500
            
    except Exception as e:
        app.logger.error(f"Error deleting event {event_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete event'}), 500

@app.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """API endpoint to update an event"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if event exists
        existing_event = repo.get_by_id(event_id)
        if not existing_event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Update event fields with provided data or keep existing values
        existing_event.title = data.get('title', existing_event.title)
        existing_event.description = data.get('description', existing_event.description)
        existing_event.date = data.get('date', existing_event.date)
        existing_event.time = data.get('time', existing_event.time)
        
        # Validate updated event data
        validation_errors = existing_event.validate()
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        # Update event using repository
        success = repo.update(existing_event)
        
        if success:
            return jsonify({
                'message': 'Event updated successfully',
                'event': existing_event.to_dict()
            })
        else:
            return jsonify({'error': 'Failed to update event'}), 500
            
    except ValueError as e:
        app.logger.error(f"Validation error updating event {event_id}: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error updating event {event_id}: {str(e)}")
        return jsonify({'error': 'Failed to update event'}), 500

# Additional event management routes

@app.route('/events/search')
def search_events():
    """API endpoint to search events by title or description"""
    search_term = request.args.get('q', '').strip()
    
    if not search_term:
        return jsonify({'error': 'Search term is required'}), 400
    
    try:
        events = repo.search(search_term)
        events_list = [event.to_dict() for event in events]
        return jsonify({
            'events': events_list,
            'count': len(events_list),
            'search_term': search_term
        })
        
    except Exception as e:
        app.logger.error(f"Error searching events: {str(e)}")
        return jsonify({'error': 'Failed to search events'}), 500

@app.route('/events/count')
def count_events():
    """API endpoint to get event count statistics"""
    date = request.args.get('date')
    
    try:
        if date:
            count = repo.count_events_by_date(date)
            return jsonify({'date': date, 'count': count})
        else:
            total_count = repo.count_events()
            return jsonify({'total_count': total_count})
            
    except Exception as e:
        app.logger.error(f"Error counting events: {str(e)}")
        return jsonify({'error': 'Failed to count events'}), 500

@app.route('/events/<int:event_id>')
def get_event_by_id(event_id):
    """API endpoint to get a specific event by ID"""
    try:
        event = repo.get_by_id(event_id)
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        return jsonify(event.to_dict())
        
    except Exception as e:
        app.logger.error(f"Error retrieving event {event_id}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve event'}), 500

if __name__ == '__main__':
    # Database is automatically initialized by the models module
    app.run(debug=True, host='0.0.0.0', port=5000)








