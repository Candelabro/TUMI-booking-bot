from eventList import EventList

class User:
  def __init__(self, chat_id):
      self.user_id = chat_id
      self.accountName = ""
      self.accountPassword = ""
      self.eventList = EventList()