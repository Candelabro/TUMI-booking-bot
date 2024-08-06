from event import Event
import threading
import time
import datetime
from datetime import date, datetime

class EventList:
  def __init__(self):
    self.events = []
    self.threads = []

  def add_event(self, event):
    # Add event to events list
    self.events.append(event)

  def start_thread(self, func, user):
    event = self.events[-1]
    # Start a new thread for the event
    #thread = threading.Thread(target=self.generate_notification, args=(event,))
    thread = threading.Thread(target=func, args=[user])
    thread.start()
    self.threads.append(thread)

  def generate_notification(self, event):
    dateTime = datetime.strptime(event.date + ' ' + event.time, "%d.%m.%Y %H:%M")
    # Calculate the number of seconds until the specified date and time
    sleep_time = (dateTime - datetime.now()).total_seconds()
    # Only sleep if the date is in the future
    if sleep_time > 0:
      time.sleep(sleep_time)
    print(f"{event.name} event occurred!")
    
  def stop_event(self, event_name):
    # Find the event and corresponding thread
    for event, thread in zip(self.events, self.threads):
      if event.name == event_name:
        # Stop the thread
        thread.stop()
        # Remove the event and thread from the lists
        self.events.remove(event)
        self.threads.remove(thread)
        print(f"{event_name} stopped!")
        break