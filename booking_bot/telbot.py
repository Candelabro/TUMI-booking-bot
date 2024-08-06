#!/usr/bin/env python3

#from asyncio.windows_events import NULL
from unicodedata import name
import telebot
from telebot import types
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
from datetime import date, datetime
import schedule
import requests
import logging
from threading import Thread
import copy

from user import User
from event import Event


API_KEY = "" # add the API Key here
bot = telebot.TeleBot(API_KEY)
url = "https://tumi.esn.world/home"
all_users = {}

def waitAndClick(driver, loctype, loc):
  wait = WebDriverWait(driver, 9)
  elem = wait.until(EC.element_to_be_clickable((loctype, loc)))
  elem.click()

def login(driver, user):
  try:
    driver.get(url)
    waitAndClick(driver, By.XPATH,"//button[@class='mat-focus-indicator mat-stroked-button mat-button-base ng-star-inserted']/span[@class='mat-button-wrapper']")
    userBlock = driver.find_element("name", "username")
    userBlock.send_keys(user.accountName)
    waitAndClick(driver, By.XPATH, "//button[@type='submit']")
    pwBlock = driver.find_element(By.NAME, "password")

    if pwBlock:
        pwBlock.send_keys(user.accountPassword)
        waitAndClick(driver, By.XPATH, "//button[@type='submit']")
    time.sleep(3)
  except Exception as e:
    return
    
def findAndClickEvent(driver, user):
  time.sleep(2)
  elements = driver.find_elements(By.CLASS_NAME, 'mb-2.font-bold')
  maxLen = len(elements)
  count = 0
  while count < maxLen:
      elements = driver.find_elements(By.CLASS_NAME,'mb-2.font-bold')
      elem = elements[count]
      str = elem.text
      if str.find(user.name) != -1:
          elem.click()
          break
      if count == maxLen-1 and str.find(user.name) == -1:
        notify = "The event " + name + " does not exist!!"
        print(notify)
        notifyEvent(user, notify)
        break        
      count = count + 1
  time.sleep(5)

def registerToEvent(driver, user, name):
  max_attempts = 5
  notify = ""
  
  for i in range(max_attempts):
    try:
      link = driver.find_element(By.XPATH, "//p[@class='font-bold ng-star-inserted']")
      str = link.text
      print(str)
      if str.find("This event is not open for registration yet") != -1:
        if (i == max_attempts-1):
          notify = "Event " + name + " not open yet, please /book it again!!"
          print(notify)
          notifyEvent(user, notify)
          break
        driver.refresh()
        time.sleep(3)
        continue
    except NoSuchElementException:
      isFull = False
      break

    isFull = False
    try:
      link1 = driver.find_element(By.CLASS_NAME, 'mb-4.text-lg.font-bold')
      str1 = link1.text
      if str1.find("Event is full") != -1:
        notify = "Event " + name +  " is full!! ◞‸◟"
        print(notify)
        notifyEvent(user, notify)
        isFull = True
        break       
    except NoSuchElementException:
      isFull = False
      break

    if (not isFull):
      try :
        #driver.find_element_by_xpath("//button[@class='mat-focus-indicator mat-raised-button mat-button-base mat-primary ng-star-inserted']")
        waitAndClick(driver, By.XPATH, "//button[@class='mat-focus-indicator mat-raised-button mat-button-base mat-primary ng-star-inserted']")
        notify = "Registered to " + name + "! :o)"
        print(notify)
        notifyEvent(user, notify)
        break
      except NoSuchElementException:
        time.sleep(1)

def jobEvent(user):
  loggedIn = False
  options = Options()
  options.headless = False
  driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)
  userEvent = copy.copy(user.eventList.events[-1])

  dateTime = datetime.strptime(userEvent.date + ' ' + userEvent.time, "%d.%m.%Y %H:%M")
  timeDiff = (dateTime - datetime.now()).total_seconds()

  if timeDiff > 0:
        time.sleep(timeDiff-2)
  else:
      notify = "The " + name + " event is in the past, please /book another one! =)"
      print(notify)
      notifyEvent(user, notify)
      user.eventList.stop_event(userEvent.name)
      return   

  #timeDiffMinutes = timeDiff.total_seconds()/60

  #if (timeDiffMinutes > 0.0 and timeDiffMinutes <= 2.0) and not loggedIn:
  if not loggedIn:
      login(driver, user)
      loggedIn = True
  
  if (datetime.now() >= dateTime):
    if (loggedIn):
      findAndClickEvent(driver,userEvent)
      registerToEvent(driver, user, userEvent.name)

  user.eventList.stop_event(userEvent.name)


# ---------------------- BOT ------------------------

#------------------------------------------------------------------------------------------------------------------------
def notifyEvent(user, notify):
  bot.send_message(user.user_id, notify)

@bot.message_handler(commands=['start'])
def start(message):
  user = User(message.chat.id)
  all_users[message.chat.id] = user
  bot.send_message(message.chat.id, "Hello *{}*!\n".format(message.from_user.first_name))
  sent = bot.send_message(message.chat.id, 'Please enter your user name (/cancel to abort): ')
  bot.register_next_step_handler(sent, getAccountName)

def getAccountName(message):
  user = all_users[message.chat.id]
  if message.text == '/cancel':
    user.accountName = ""
    return

  user.accountName = message.text
  sent = bot.send_message(message.chat.id, 'Please enter your password: ')
  bot.register_next_step_handler(sent, getAccountPassword)

def getAccountPassword(message):
  user = all_users[message.chat.id]
  if message.text == '/cancel':
    user.accountName = ""
    user.accountPassword = ""
    return

  user.accountPassword = message.text
  bot.send_message(message.chat.id, 'Great! Type /book to reserve an event')

@bot.message_handler(commands=['book'])
def book(message):
  if (not message.chat.id in all_users):
    start(message)
  else:
    sent = bot.send_message(message.chat.id, 'Please enter event name (/cancel to abort): ')
    bot.register_next_step_handler(sent, getName)

def getName(message):
  user = all_users[message.chat.id]
  if message.text == '/cancel':
    return

  user.eventList.add_event(Event(message.text))
  sent = bot.send_message(message.chat.id, "Enter event date (es. 15.05.2022): ")
  bot.register_next_step_handler(sent, getDate)

def getDate(message):
  user = all_users[message.chat.id]
  if message.text == '/cancel':
    return

  user.eventList.events[-1].date = message.text
  sent = bot.send_message(message.chat.id, "Enter event time (es. 19:00): ")
  bot.register_next_step_handler(sent, getTime) 

def getTime(message):
  user = all_users[message.chat.id]
  if message.text == '/cancel':
    return

  user = all_users[message.chat.id]
  user.eventList.events[-1].time = message.text
  try:
    dateTime = datetime.strptime(user.eventList.events[-1].date + ' ' + user.eventList.events[-1].time, "%d.%m.%Y %H:%M")
  except Exception as e:
    bot.send_message(message.chat.id, "Sorry, wrong date or time format, try /book again.")
    return

  user.eventList.start_thread(jobEvent, user)

@bot.message_handler(commands=['stop'])
def book(message):
    sent = bot.send_message(message.chat.id, 'Please enter event name to stop: ')
    bot.register_next_step_handler(sent, getEventStop)

def getEventStop(message):
  user = all_users[message.chat.id]
  if message.text == '/cancel':
    return

  user.eventList.stop_event(Event(message.text))
  sent = bot.send_message(message.chat.id, message.text + " event stopped")

# start bot polling
bot.polling()