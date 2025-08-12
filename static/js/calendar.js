// Calendar Application JavaScript
class CalendarApp {
    constructor() {
        this.currentDate = new Date();
        this.selectedDate = null;
        this.editingEventId = null;
        this.events = {};
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadEvents();
    }

    bindEvents() {
        // Modal event bindings
        this.bindModalEvents();
        
        // Calendar day click events
        this.bindCalendarEvents();
        
        // Form submission events
        this.bindFormEvents();
        
        // Navigation events
        this.bindNavigationEvents();
        
        // Event item click events
        this.bindEventItemEvents();
    }

    bindModalEvents() {
        // Add event button
        const addEventBtn = document.getElementById('add-event-btn');
        if (addEventBtn) {
            addEventBtn.addEventListener('click', () => {
                this.openEventForm();
            });
        }

        // Close modal buttons
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal'));
            });
        });

        // Close modal when clicking outside
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });

        // Cancel form button
        const cancelBtn = document.getElementById('cancel-form-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.closeModal(document.getElementById('event-form-modal'));
            });
        }

        // Close modal button in event details
        const closeModalBtn = document.getElementById('close-modal-btn');
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => {
                this.closeModal(document.getElementById('event-modal'));
            });
        }

        // Edit event button
        const editEventBtn = document.getElementById('edit-event-btn');
        if (editEventBtn) {
            editEventBtn.addEventListener('click', () => {
                this.editCurrentEvent();
            });
        }

        // Delete event button
        const deleteEventBtn = document.getElementById('delete-event-btn');
        if (deleteEventBtn) {
            deleteEventBtn.addEventListener('click', () => {
                this.deleteCurrentEvent();
            });
        }
    }

    bindCalendarEvents() {
        // Calendar day click events
        document.querySelectorAll('.calendar-day:not(.empty-day)').forEach(day => {
            day.addEventListener('click', (e) => {
                // Don't trigger if clicking on an event
                if (!e.target.closest('.event-item')) {
                    const date = day.dataset.date;
                    this.selectDate(date);
                    this.openEventForm(date);
                }
            });
        });
    }

    bindFormEvents() {
        // Event form submission
        const eventForm = document.getElementById('event-form');
        if (eventForm) {
            eventForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitEventForm();
            });
        }
    }

    bindNavigationEvents() {
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    bindEventItemEvents() {
        // Event item click events
        document.querySelectorAll('.event-item').forEach(eventItem => {
            eventItem.addEventListener('click', (e) => {
                e.stopPropagation();
                const eventId = eventItem.dataset.eventId;
                this.showEventDetails(eventId);
            });
        });

        // More events click
        document.querySelectorAll('.more-events').forEach(moreEvents => {
            moreEvents.addEventListener('click', (e) => {
                e.stopPropagation();
                const date = e.target.closest('.calendar-day').dataset.date;
                this.showDayEvents(date);
            });
        });
    }

    // Modal Management
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            modal.style.display = 'flex';
            
            // Focus first input if it's a form modal
            const firstInput = modal.querySelector('input, textarea');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
            
            // Reset form if it's the event form modal
            if (modal.id === 'event-form-modal') {
                this.resetEventForm();
            }
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            this.closeModal(modal);
        });
    }

    // Event Form Management
    openEventForm(date = null) {
        this.editingEventId = null;
        this.resetEventForm();
        
        if (date) {
            document.getElementById('event-date').value = date;
        } else if (this.selectedDate) {
            document.getElementById('event-date').value = this.selectedDate;
        } else {
            // Set to today's date
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('event-date').value = today;
        }
        
        document.getElementById('form-modal-title').textContent = 'Add New Event';
        this.openModal('event-form-modal');
    }

    resetEventForm() {
        const form = document.getElementById('event-form');
        if (form) {
            form.reset();
        }
        this.editingEventId = null;
    }

    submitEventForm() {
        const form = document.getElementById('event-form');
        const formData = new FormData(form);
        
        const eventData = {
            title: formData.get('title'),
            description: formData.get('description'),
            date: formData.get('date'),
            time: formData.get('time')
        };

        // Validate required fields
        if (!eventData.title || !eventData.date) {
            this.showToast('Please fill in all required fields', 'error');
            return;
        }

        this.showLoading(true);

        if (this.editingEventId) {
            // Update existing event
            this.updateEvent(this.editingEventId, eventData);
        } else {
            // Create new event
            this.createEvent(eventData);
        }
    }

    // Event CRUD Operations
    async createEvent(eventData) {
        try {
            const response = await fetch('/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showToast('Event created successfully', 'success');
                this.closeModal(document.getElementById('event-form-modal'));
                this.refreshCalendar();
            } else {
                this.showToast(result.error || 'Failed to create event', 'error');
            }
        } catch (error) {
            console.error('Error creating event:', error);
            this.showToast('Failed to create event', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async updateEvent(eventId, eventData) {
        try {
            const response = await fetch(`/events/${eventId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showToast('Event updated successfully', 'success');
                this.closeModal(document.getElementById('event-form-modal'));
                this.refreshCalendar();
            } else {
                this.showToast(result.error || 'Failed to update event', 'error');
            }
        } catch (error) {
            console.error('Error updating event:', error);
            this.showToast('Failed to update event', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async deleteEvent(eventId) {
        if (!confirm('Are you sure you want to delete this event?')) {
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch(`/events/${eventId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (response.ok) {
                this.showToast('Event deleted successfully', 'success');
                this.closeModal(document.getElementById('event-modal'));
                this.refreshCalendar();
            } else {
                this.showToast(result.error || 'Failed to delete event', 'error');
            }
        } catch (error) {
            console.error('Error deleting event:', error);
            this.showToast('Failed to delete event', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadEvents() {
        const urlParams = new URLSearchParams(window.location.search);
        const year = urlParams.get('year') || new Date().getFullYear();
        const month = urlParams.get('month') || new Date().getMonth() + 1;

        try {
            const response = await fetch(`/events?year=${year}&month=${month}`);
            const events = await response.json();

            this.events = {};
            events.forEach(event => {
                if (!this.events[event.date]) {
                    this.events[event.date] = [];
                }
                this.events[event.date].push(event);
            });
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    // Event Details
    async showEventDetails(eventId) {
        try {
            // Find event in current events data
            let event = null;
            for (const date in this.events) {
                const foundEvent = this.events[date].find(e => e.id == eventId);
                if (foundEvent) {
                    event = foundEvent;
                    break;
                }
            }

            if (!event) {
                this.showToast('Event not found', 'error');
                return;
            }

            this.currentEventId = eventId;
            this.displayEventDetails(event);
            this.openModal('event-modal');
        } catch (error) {
            console.error('Error showing event details:', error);
            this.showToast('Failed to load event details', 'error');
        }
    }

    displayEventDetails(event) {
        const eventDetails = document.getElementById('event-details');
        if (eventDetails) {
            eventDetails.innerHTML = `
                <div class="event-detail-item">
                    <strong>Title:</strong> ${this.escapeHtml(event.title)}
                </div>
                <div class="event-detail-item">
                    <strong>Date:</strong> ${this.formatDate(event.date)}
                </div>
                ${event.time ? `
                <div class="event-detail-item">
                    <strong>Time:</strong> ${this.formatTime(event.time)}
                </div>
                ` : ''}
                ${event.description ? `
                <div class="event-detail-item">
                    <strong>Description:</strong> ${this.escapeHtml(event.description)}
                </div>
                ` : ''}
            `;
        }
    }

    editCurrentEvent() {
        if (!this.currentEventId) return;

        // Find the event
        let event = null;
        for (const date in this.events) {
            const foundEvent = this.events[date].find(e => e.id == this.currentEventId);
            if (foundEvent) {
                event = foundEvent;
                break;
            }
        }

        if (!event) {
            this.showToast('Event not found', 'error');
            return;
        }

        // Close event details modal
        this.closeModal(document.getElementById('event-modal'));

        // Populate form with event data
        this.editingEventId = event.id;
        document.getElementById('event-title').value = event.title;
        document.getElementById('event-description').value = event.description || '';
        document.getElementById('event-date').value = event.date;
        document.getElementById('event-time').value = event.time || '';

        document.getElementById('form-modal-title').textContent = 'Edit Event';
        this.openModal('event-form-modal');
    }

    deleteCurrentEvent() {
        if (this.currentEventId) {
            this.deleteEvent(this.currentEventId);
        }
    }

    showDayEvents(date) {
        const dayEvents = this.events[date] || [];
        
        if (dayEvents.length === 0) {
            this.showToast('No events for this day', 'info');
            return;
        }

        // Create a simple list of events for the day
        const eventsList = dayEvents.map(event => `
            <div class="day-event-item" data-event-id="${event.id}">
                <strong>${this.escapeHtml(event.title)}</strong>
                ${event.time ? `<span class="event-time"> - ${this.formatTime(event.time)}</span>` : ''}
                ${event.description ? `<p>${this.escapeHtml(event.description)}</p>` : ''}
            </div>
        `).join('');

        const eventDetails = document.getElementById('event-details');
        if (eventDetails) {
            eventDetails.innerHTML = `
                <h4>Events for ${this.formatDate(date)}</h4>
                <div class="day-events-list">
                    ${eventsList}
                </div>
            `;
        }

        // Bind click events to individual events
        setTimeout(() => {
            document.querySelectorAll('.day-event-item').forEach(item => {
                item.addEventListener('click', () => {
                    const eventId = item.dataset.eventId;
                    this.closeModal(document.getElementById('event-modal'));
                    setTimeout(() => this.showEventDetails(eventId), 100);
                });
            });
        }, 100);

        this.openModal('event-modal');
    }

    // Date Selection
    selectDate(date) {
        this.selectedDate = date;
        
        // Remove previous selection
        document.querySelectorAll('.calendar-day.selected').forEach(day => {
            day.classList.remove('selected');
        });
        
        // Add selection to current date
        const dayElement = document.querySelector(`[data-date="${date}"]`);
        if (dayElement) {
            dayElement.classList.add('selected');
        }
    }

    // Utility Functions
    refreshCalendar() {
        // Reload the page to refresh calendar data
        window.location.reload();
    }

    showLoading(show) {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            if (show) {
                spinner.classList.add('show');
            } else {
                spinner.classList.remove('show');
            }
        }
    }

    showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-message">${this.escapeHtml(message)}</div>
        `;

        toastContainer.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(dateString) {
        const date = new Date(dateString + 'T00:00:00');
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    formatTime(timeString) {
        if (!timeString) return '';
        
        const [hours, minutes] = timeString.split(':');
        const date = new Date();
        date.setHours(parseInt(hours), parseInt(minutes));
        
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
}

// Initialize the calendar application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.calendarApp = new CalendarApp();
});

// Additional utility functions for calendar navigation
function navigateToMonth(year, month) {
    const url = new URL(window.location);
    url.searchParams.set('year', year);
    url.searchParams.set('month', month);
    window.location.href = url.toString();
}

function navigateToToday() {
    const today = new Date();
    navigateToMonth(today.getFullYear(), today.getMonth() + 1);
}

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CalendarApp;
}
