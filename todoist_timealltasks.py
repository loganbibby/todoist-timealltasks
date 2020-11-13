from flask import Flask, redirect, url_for, abort, request, session
import click
import requests
import todoist

app = Flask(__name__)
app.config.from_object('settings.Config')

def get_todoist_token():
    with open(app.config['TOKENFILE'], 'r') as fh:
        app.logger.debug('Read token file: {}'.format(app.config['TOKENFILE']))
        token = fh.readline()
        app.logger.debug('Todoist token: {}'.format(token))
      
    return token

def get_todoist_api():
    token = get_todoist_token()
    return todoist.TodoistAPI(token)

@app.route('/todoist_auth/')
def todoist_auth():
    todoist_auth_state = "wammabunga"
    session['todoist_auth_state'] = todoist_auth_state
    
    url = "{}?client_id={}&scope=data:read_write&state={}".format(
        app.config['TODOIST_API_AUTHURL'],
        app.config['TODOIST_API_CLIENTID'],
        todoist_auth_state
    )
    
    app.logger.debug('Redirecting to initial auth: {}'.format(url))
    
    return redirect()

@app.route('/todoist_auth/redirect')
def todoist_auth_redirect():
    code = request.args['code']
    state = request.args['state']
    
    app.logger.debug('Received second stage auth code: {}'.format(code))
    
    if str(state) != str(session['todoist_auth_state']):
        app.logger.error('State returned by API does not match: "{}" != "{}"'.format(
            state, session['todoist_auth_state']
        ))
        return 'Unable to continue due to possible cross-side forgery attempt'
        
    app.logger.debug('Getting auth token')
       
    r = requests.post(
        'https://todoist.com/oauth/access_token',
        data={
            'client_id': app.config['TODOIST_API_CLIENTID'],
            'client_secret': app.config['TODOIST_API_SECRET'],
            'code': code
        }
    )
    
    if r.status_code != 200:
        app.logger.error('Unable to get auth token: {}'.format(r.text))
        return r.text
       
    token = r.json()['access_token']
    app.logger.debug('Got auth token: {}'.format(token))
    
    with open(app.config['TOKENFILE'], 'w') as fh:
        fh.write(token)
        app.logger.debug('Wrote token to file: {}'.format(app.config['TOKENFILE']))
       
    app.logger.debug('Redirecting to success page')
    return redirect(url_for('todoist_auth_success'))

@app.route('/todoist_auth/success')
def todoist_auth_success():
    return 'Authorized'

@app.cli.command('time-all-tasks')
def time_all_tasks():
    api = get_todoist_api()
    
    app.logger.debug('Getting Todoist data')
    
    if app.config['RESET_TODOIST_API_BEFORE_SYNC']:
        api.reset_state()
        app.logger.debug('Reset Todoist API state for full sync')
    
    api.items.sync()
    
    app.logger.debug('Sync token: {}'.format(api.sync_token))
    
    tasks = api.items.all()
    app.logger.debug('{} tasks synced'.format(len(tasks)))
    
    tasks_with_date = 0
    tasks_changed = 0
    
    for task in tasks:
        if task['due'] is None:
            continue
        
        app.logger.debug('Processing task #{} with due date {}'.format(task['id'], task['due']['date']))
        tasks_with_date += 1
        
        if 'T' in task['due']['date']:
            app.logger.debug('Task #{} already has a time, so it will not be changed.'.format(task['id']))
            continue
        
        due = task['due']
        due['date'] = '{}T{}'.format(due['date'], app.config['DEFAULT_DUE_TIME'])
        task.update(due=due)
        app.logger.debug('Updated task #{} with due date: {}'.format(task['id'], due))
           
        tasks_changed += 1
    
    app.logger.debug('Committing {} changes to tasks'.format(len(api.queue)))
    api.commit()
    app.logger.debug('Commit successful')
    
    app.logger.info('Added time to {} tasks (out of {} tasks with dates) for token {}'.format(
        tasks_changed,
        tasks_with_date,
        api.token
    ))
    