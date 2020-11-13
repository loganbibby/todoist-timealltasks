# Todoist-TimeAllTasks

Todoist is a really great todo list keeper, but it's missing one little feature: the ability to have a default time for tasks that have a date.

## Installation and Setup

The script requires Python 3.7 or greater. 

### Setup Todoist App credentials
1. Go to the [Todoist App Console](https://developer.todoist.com/appconsole.html)
1. Create a new app
1. Name it whatever you'd like and use `http://localhost:5000` as your app service URL
1. Set the OAuth Redirect URL to `http://localhost:5000/todoist_auth/redirect`
1. Note your client ID and client secret because you'll need them later

### Setup Todoist-TimeAllTasks
1. Clone this repository and go into the directory.
1. Setup your virtual environment (`python -m venv venv`) and source it. 
1. Install the required libraries (`pip install -r requirements.txt`).
1. Copy the settings template to `settings.py`.
1. Update your settings file with your specifics. 

### Get your Todoist token
1. Set the environemnt variable `FLASK_APP` to `todoist_timealltasks.py` (Win: `set NAME = VAL` - Linux/Mac: `export NAME = VAL`)
1. Start the Flask server: `flask run`
1. Open your browser and go to `http://localhost:5000/todoist_auth/`. It will take you to a Todoist page to authorize your app.
1. If everything works, you should see "Authorized" and have a new file called `todoist.token`

## Add a time to your tasks
In the same terminal or command prompt from the earlier commands, simply run `flask time_all_tasks`. 

## Disclosures
To be in compliance with Todist's brand guidelines, this is not created by, affiliated with, or supported by Doist.
