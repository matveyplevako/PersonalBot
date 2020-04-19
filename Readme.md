# Python telegram bot
Currently up on @PersonalGodBot
 
## What this bot can do?
1. Track attendance in sport complex
2. Receive quotes from book
3. Receive emails from different addresses on the same account
    - view content of email
    - supported email servers:
        - e.mail.ru
        - mail.google.com
        - mail.rambler.ru
        - imap.yandex.ru
        - mail.innopolis.ru





## Languages, frameworks and DB used:
- Python 3 <img src="https://i.imgur.com/y7tcFgi.png" width="20" height="20"> Language that was used to write this project
- python-telegram-bot <img src="https://i.imgur.com/UKJsJr4.png" width="22" height="20"> Library for communicating with Telegram API
- Postgres db <img src="https://i.imgur.com/ecH4YUr.png" width="20" height="20"> To store user related data
- Redis db <img src="https://i.imgur.com/lffb06o.png" width="22" height="25"> Used as cache and key-value storage

## Demo

### Attendance part
#### Functions
- input new attendanc
- fetch attendance for current term
- fetch attendance for specified period

![](https://i.imgur.com/41aezAY.gif)

### Stoic part
#### Description
quotes were taken from **[The Daily Stoic](https://www.ozon.ru/context/detail/id/141024625/)** book
In stoic/ folder you can find script that parsed book for quotes, merged them with russian descriptions from **[tg channel](https://t.me/modern_stoicism)** and uploaded to imgur.
#### Functions
- get quote for specified day
- switch between representations
- get quote for cuurent day 
    - managed in subscription and increments every day
- manage subscription
    - select hour and minutes to receive quotes
    - select from what day receive quotes
    - cancel subscription

![](https://i.imgur.com/5IWNEkN.gif)

### Email part
#### Functions
- Input email details
- When new email arrives bot will send you content
    - example at the end of the gif

![](https://i.imgur.com/K6HlP3B.gif)

### Example of received email
![](https://i.imgur.com/RdQUovH.png)

## How it works

### Attendance part
- Postgres is used to store all information about participation
- add attendance insert new record into this db
- fetching attendance use select with conditions

### Stoic part
- User can specify hour and day from what to start receiving quotes. This information is stored in Postgres
- All quote related information (eng/ru text and photo links) is stored in json file for faster access
- swithcing between representations is done by CallbackQueryHandler and message editing
- notifications at the specific time are sent by Job_Queue

### Email part 
- User related information is stored in Postgres
- fetching emails are done by imaplib
- wkhtmltoimage is used for rendering image from html
- then it is uploaded to imgur and sent to user
- message is formated using markdown
- Pulling is done by Job_Queue

## How to start bot 
### Locally
1. Set env variables
    - BOT_TOKEN - token for bot, you can get it from @BotFather
    - DATABASE_URL - url for connection
    - DEV_CHANNEL - id of channel where bot is admin to send error reports that are not handled by except handlers.
    - IMGUR_API_ID - imgur id
    - IMGUR_API_SECRET - imgur secret key
    - REDISCLOUD_URL - url for connection
    - WKHTMLTOIMAGE_BIN - path to wkhtmltoimage
2. run bot by `python3 bot.py`
### On Heroku
1. Attach Heroku Postgres
2. Attach Redis Cloud
3. Attach Sumo logic (for logging)
4. Set env variables 
    - same as locally, excluding DATABASE_URL and REDISCLOUD_URL
5. Activate worker in resources
