# TUMI-booking-bot
Tumi Events TUM (Technische Universität München) booking tool via scraping.
The tool schedules events by name, date and time (via chat bot).
When the event datetime is approaching, the tool automatically logs into the account and books a spot.

* The tool connects to the Telegram bot TumEvents (created with BotFather).
Once obtained an API Key, add it to the variable API_KEY in  telbot.py file
* USAGE
1. python3 telbot.py
2. on Telegram, add the TumEvents bot and type /start to start the booking process.
