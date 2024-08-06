import datetime

class Event:
  def __init__(self, name):
    self.name = name
    self.date = ""
    self.time = ""

  def setDate(self, date):
    self.date = date

  def getDate(self):
    return self.date

  def setTime(self, time):
    self.time = time 

  def getTime(self):
    return self.time