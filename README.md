# Calendar Application

A modern, responsive web-based calendar application built with Flask, featuring event management, intuitive navigation, and a clean user interface. This application allows users to create, view, edit, and delete calendar events with a professional-grade user experience.

## Features

### 🗓️ Calendar View
- **Monthly Calendar Display**: Clean grid layout showing the full month
- **Navigation Controls**: Easy month/year navigation with previous/next buttons
- **Today Highlighting**: Current date is visually highlighted
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

### 📅 Event Management
- **Create Events**: Add new events with title, description, date, and time
- **Edit Events**: Modify existing events with full form validation
- **Delete Events**: Remove events with confirmation dialogs
- **Event Categories**: Organize events by category (work, personal, meeting, etc.)
- **Priority Levels**: Set event importance (normal, low, high, urgent)
- **All-Day Events**: Support for events without specific times

### 🔍 Advanced Features
- **Event Search**: Search events by title or description
- **Quick Date Selection**: Shortcuts for today, tomorrow, next week, etc.
- **Event Statistics**: View event counts and analytics
- **Recurring Events**: Support for repeating events (daily, weekly, monthly, yearly)
- **Location & Links**: Add location and related URLs to events

### 🎨 User Interface
- **Modern Design**: Clean, professional interface with gradient themes
- **Interactive Modals**: Smooth modal dialogs for event creation/editing
- **Toast Notifications**: User-friendly success/error messages
- **Loading Indicators**: Visual feedback during operations
- **Keyboard Navigation**: Full keyboard accessibility support

## Technology Stack

- **Backend**: Flask 3.0.0 (Python web framework)
- **Database**: SQLite (lightweight, serverless database)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom CSS with responsive grid layout
- **Architecture**: MVC pattern with repository design pattern

## Project Structure

```
calendar-application/
├── app.py                 # Main Flask application
├── models.py              # Database models and repository
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── calendar_app.log      # Application logs
├── calendar.db           # SQLite database (created automatically)
├── templates/
│   ├── calendar.html     # Main calendar template
│   └── event_form.html   # Event form modal template
└── static/
    ├── css/
    │   └── calendar.css  # Application styles
    └── js/
        └── calendar.js   # Frontend JavaScript
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd calendar-application
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv calendar_env

# Activate virtual environment
# On Windows:
calendar_env\Scripts\activate
# On macOS/Linux:
source calendar_env/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
The database will be automatically created when you first run the application.

### Step 5: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage Guide

### Creating Events
1. Click the **"Add Event"** button in the calendar header
2. Fill in the event details:
   - **Title** (required): Event name
   - **Description** (optional): Additional details
   - **Date** (required): Event date
   - **Time** (optional): Event time
   - **Category** (optional): Event type
   - **Priority** (optional): Event importance
3. Click **"Save Event"** to create the event

### Viewing Events
- Events appear as colored blocks on calendar days
- Click on an event to view full details
- Days with multiple events show a "more events" indicator

### Editing Events
1. Click on an existing event
2. Click the **"Edit"** button in the event details modal
3. Modify the event information
4. Click **"Save Event"** to update

### Deleting Events
1. Click on an existing event
2. Click the **"Delete"** button in the event details modal
3. Confirm the deletion in the dialog

### Navigation
- Use **Previous/Next** buttons to navigate between months
- Click on month abbreviations in the quick navigation panel
- Use year links to jump between years

### Searching Events
- Use the search functionality to find events by title or description
- Search results show matching events across all dates

## API Endpoints

The application provides a RESTful API for event management:

### Events API
- `GET /events` - Retrieve all events or filter by date/month
- `POST /events` - Create a new event
- `GET /events/<id>` - Get specific event by ID
- `PUT /events/<id>` - Update an existing event
- `DELETE /events/<id>` - Delete an event

### Search & Statistics
- `GET /events/search?q=<term>` - Search events
- `GET /events/count` - Get event statistics

### Example API Usage
```javascript
// Create a new event
fetch('/events', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        title: 'Meeting',
        description: 'Team standup',
        date: '2024-01-15',
        time: '10:00'
    })
});

// Get events for a specific month
fetch('/events?year=2024&month=1')
    .then(response => response.json())
    .then(events => console.log(events));
```

## Configuration

### Environment Variables
Create a `.env` file for custom configuration:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=calendar.db
DEBUG=True
LOG_LEVEL=INFO
```

### Database Configuration
The application uses SQLite by default. The database file (`calendar.db`) is created automatically in the project root directory.

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Run tests
pytest
```

### Adding New Features
1. **Database Changes**: Modify `models.py` for new data structures
2. **API Endpoints**: Add new routes in `app.py`
3. **Frontend**: Update templates and JavaScript in respective directories
4. **Styling**: Modify `static/css/calendar.css` for visual changes

## Deployment

### Production Deployment with Gunicorn
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Environment Setup for Production
- Set `DEBUG=False`
- Use a strong `SECRET_KEY`
- Configure proper logging
- Set up database backups
- Use HTTPS in production

## Troubleshooting

### Common Issues

**Database Connection Errors**
- Ensure the application has write permissions in the directory
- Check that SQLite is properly installed

**Port Already in Use**
- Change the port in `app.py`: `app.run(port=5001)`
- Or kill the process using the port

**JavaScript Errors**
- Check browser console for detailed error messages
- Ensure all static files are loading correctly

**Styling Issues**
- Clear browser cache
- Check that CSS files are loading properly

### Logging
Application logs are written to `calendar_app.log` and console output. Check logs for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on the GitHub repository or contact the development team.

## Changelog

### Version 1.0.0
- Initial release with full calendar functionality
- Event CRUD operations
- Responsive design
- Search and filtering capabilities
- RESTful API
- Comprehensive error handling and logging

