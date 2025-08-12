import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Union

class DatabaseManager:
    """Database connection and management class"""
    
    def __init__(self, db_path: str = 'calendar.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with events table"""
        conn = self.get_connection()
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    date TEXT NOT NULL,
                    time TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for better query performance
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_date 
                ON events(date)
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute SELECT query and return results"""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            raise
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Update execution error: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT query and return last row ID"""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Insert execution error: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()


class Event:
    """Event data model class"""
    
    def __init__(self, title: str, date: str, description: str = None, 
                 time: str = None, event_id: int = None, 
                 created_at: str = None, updated_at: str = None):
        self.id = event_id
        self.title = title
        self.description = description
        self.date = date
        self.time = time
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date,
            'time': self.time,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Event':
        """Create Event instance from database row"""
        return cls(
            event_id=row['id'],
            title=row['title'],
            description=row['description'],
            date=row['date'],
            time=row['time'],
            created_at=row['created_at'],
            updated_at=row.get('updated_at')
        )
    
    def validate(self) -> List[str]:
        """Validate event data and return list of errors"""
        errors = []
        
        if not self.title or not self.title.strip():
            errors.append("Title is required")
        elif len(self.title.strip()) > 200:
            errors.append("Title must be less than 200 characters")
        
        if not self.date:
            errors.append("Date is required")
        else:
            try:
                datetime.strptime(self.date, '%Y-%m-%d')
            except ValueError:
                errors.append("Date must be in YYYY-MM-DD format")
        
        if self.time:
            try:
                datetime.strptime(self.time, '%H:%M')
            except ValueError:
                errors.append("Time must be in HH:MM format")
        
        if self.description and len(self.description) > 1000:
            errors.append("Description must be less than 1000 characters")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if event data is valid"""
        return len(self.validate()) == 0


class EventRepository:
    """Repository class for Event CRUD operations"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
    
    def create(self, event: Event) -> int:
        """Create a new event and return its ID"""
        if not event.is_valid():
            raise ValueError(f"Invalid event data: {', '.join(event.validate())}")
        
        query = '''
            INSERT INTO events (title, description, date, time, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''
        params = (event.title, event.description, event.date, event.time)
        
        event_id = self.db.execute_insert(query, params)
        event.id = event_id
        return event_id
    
    def get_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID"""
        query = 'SELECT * FROM events WHERE id = ?'
        rows = self.db.execute_query(query, (event_id,))
        
        if rows:
            return Event.from_row(rows[0])
        return None
    
    def get_all(self) -> List[Event]:
        """Get all events ordered by date and time"""
        query = '''
            SELECT * FROM events 
            ORDER BY date ASC, time ASC, title ASC
        '''
        rows = self.db.execute_query(query)
        return [Event.from_row(row) for row in rows]
    
    def get_by_date(self, date: str) -> List[Event]:
        """Get events for a specific date"""
        query = '''
            SELECT * FROM events 
            WHERE date = ? 
            ORDER BY time ASC, title ASC
        '''
        rows = self.db.execute_query(query, (date,))
        return [Event.from_row(row) for row in rows]
    
    def get_by_date_range(self, start_date: str, end_date: str) -> List[Event]:
        """Get events within a date range"""
        query = '''
            SELECT * FROM events 
            WHERE date >= ? AND date <= ? 
            ORDER BY date ASC, time ASC, title ASC
        '''
        rows = self.db.execute_query(query, (start_date, end_date))
        return [Event.from_row(row) for row in rows]
    
    def get_by_month(self, year: int, month: int) -> List[Event]:
        """Get events for a specific month"""
        start_date = f"{year}-{month:02d}-01"
        
        # Calculate end date (first day of next month)
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        query = '''
            SELECT * FROM events 
            WHERE date >= ? AND date < ? 
            ORDER BY date ASC, time ASC, title ASC
        '''
        rows = self.db.execute_query(query, (start_date, end_date))
        return [Event.from_row(row) for row in rows]
    
    def update(self, event: Event) -> bool:
        """Update an existing event"""
        if not event.id:
            raise ValueError("Event ID is required for update")
        
        if not event.is_valid():
            raise ValueError(f"Invalid event data: {', '.join(event.validate())}")
        
        query = '''
            UPDATE events 
            SET title = ?, description = ?, date = ?, time = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        params = (event.title, event.description, event.date, event.time, event.id)
        
        affected_rows = self.db.execute_update(query, params)
        return affected_rows > 0
    
    def delete(self, event_id: int) -> bool:
        """Delete an event by ID"""
        query = 'DELETE FROM events WHERE id = ?'
        affected_rows = self.db.execute_update(query, (event_id,))
        return affected_rows > 0
    
    def delete_by_date(self, date: str) -> int:
        """Delete all events for a specific date"""
        query = 'DELETE FROM events WHERE date = ?'
        return self.db.execute_update(query, (date,))
    
    def search(self, search_term: str) -> List[Event]:
        """Search events by title or description"""
        query = '''
            SELECT * FROM events 
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY date ASC, time ASC, title ASC
        '''
        search_pattern = f"%{search_term}%"
        rows = self.db.execute_query(query, (search_pattern, search_pattern))
        return [Event.from_row(row) for row in rows]
    
    def count_events(self) -> int:
        """Get total number of events"""
        query = 'SELECT COUNT(*) as count FROM events'
        rows = self.db.execute_query(query)
        return rows[0]['count'] if rows else 0
    
    def count_events_by_date(self, date: str) -> int:
        """Get number of events for a specific date"""
        query = 'SELECT COUNT(*) as count FROM events WHERE date = ?'
        rows = self.db.execute_query(query, (date,))
        return rows[0]['count'] if rows else 0
    
    def get_events_grouped_by_date(self, year: int = None, month: int = None) -> Dict[str, List[Event]]:
        """Get events grouped by date for calendar display"""
        if year and month:
            events = self.get_by_month(year, month)
        else:
            events = self.get_all()
        
        grouped_events = {}
        for event in events:
            date = event.date
            if date not in grouped_events:
                grouped_events[date] = []
            grouped_events[date].append(event)
        
        return grouped_events


# Utility functions for common operations
def create_event_from_dict(data: Dict) -> Event:
    """Create Event instance from dictionary data"""
    return Event(
        title=data.get('title', ''),
        description=data.get('description', ''),
        date=data.get('date', ''),
        time=data.get('time', ''),
        event_id=data.get('id')
    )

def validate_date_format(date_string: str) -> bool:
    """Validate date string format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_time_format(time_string: str) -> bool:
    """Validate time string format (HH:MM)"""
    try:
        datetime.strptime(time_string, '%H:%M')
        return True
    except ValueError:
        return False

def format_date_for_display(date_string: str) -> str:
    """Format date string for display"""
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except ValueError:
        return date_string

def format_time_for_display(time_string: str) -> str:
    """Format time string for display"""
    try:
        time_obj = datetime.strptime(time_string, '%H:%M')
        return time_obj.strftime('%I:%M %p')
    except ValueError:
        return time_string


# Global repository instance for easy access
event_repository = EventRepository()

# Export main classes and functions
__all__ = [
    'DatabaseManager',
    'Event',
    'EventRepository',
    'event_repository',
    'create_event_from_dict',
    'validate_date_format',
    'validate_time_format',
    'format_date_for_display',
    'format_time_for_display'
]
