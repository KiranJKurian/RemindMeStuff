import logging
import os
import pickle
import cgi
import webapp2
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets
import json

import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2

from apiclient.discovery import build
from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<code>%s</code>
<p>You can find the Client ID and Client secret values
on the API Access tab in the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>

""" % CLIENT_SECRETS

decorator = OAuth2DecoratorFromClientSecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/calendar',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

service = build('calendar', 'v3')


def handle_400(request, response, exception):
    template = JINJA_ENVIRONMENT.get_template('addClass.html')
    response.write(template.render())
    response.write("<center><h3>Congratulations, you have been redirected into the fourth dimension! Jk, but seriously, you're not supposed to be here</h3></center>")
    response.write('<center><img src="/images/404.jpg" alt="Really?"></center>')

def handle_404(request, response, exception):
    template = JINJA_ENVIRONMENT.get_template('addClass.html')
    response.write(template.render())
    response.write("<center><h3>Congratulations, you hacked into the fourth dimension! Jk, but seriously, you're not supposed to be here</h3></center>")
    response.write('<center><img src="/images/404.jpg" alt="Really?"></center>')

def handle_405(request, response, exception):
    template = JINJA_ENVIRONMENT.get_template('addClass.html')
    response.write(template.render())
    response.write("<center><h3>Congratulations, you hacked into the fourth dimension! Jk, but seriously, you're not supposed to be able to <b>get</b> here</h3></center>")
    response.write('<center><img src="/images/404.jpg" alt="Really?"></center>')

def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('A server error occurred!')
    response.set_status(500)

class MainHandler(webapp2.RequestHandler):

    @decorator.oauth_required
    def get(self):
        test = ""
        page_token = None
        newClass=True
        user=users.get_current_user()
        if user:
            hello="Hello %s"%user.nickname()
        else:
            hello=""
        template_values = {
            'hello':hello
        }
        template = JINJA_ENVIRONMENT.get_template('addManual.html')
        self.response.write(template.render(template_values))

class addManualEvent(webapp2.RequestHandler):
    @decorator.oauth_aware
    def post(self):
        template = JINJA_ENVIRONMENT.get_template('addClass.html')
        self.response.write(template.render())
        summary=self.request.get('summary')
        location=self.request.get('location')
        if self.request.get('date'):
          date=self.request.get('date')
        else:
          self.response.write("You didn't enter a date, %s"%('please <a href="/">try again and enter one.</a>'))
          return
        if self.request.get('startHour'):
          startHour=self.request.get('startHour')
        else:
          self.response.write("You didn't select a start hour, %s"%('please <a href="/">try again and select one.</a>'))
          return
        if self.request.get('startMinute').isnumeric():
          startMinute=self.request.get('startMinute')
        else:
          self.response.write("You didn't input a valid start minute, %s"%('please <a href="/">try again and input one.</a>'))
          return
        startTime="%s:%s:00"%(startHour,startMinute)
        try:

          event = {
                    "location": "%s"%(location),
                     "end": {
                         "dateTime": "%sT%s"%(date,startTime),
                        "timeZone": "America/New_York"
                     },
                     "start": {
                         "dateTime": "%sT%s"%(date,startTime),
                        "timeZone": "America/New_York"
                     },
                     "summary": summary,
                     "reminders": {
                        "useDefault":"false",
                        "overrides": [
                        {
                            "method":"popup",
                            "minutes": 20
                         }
                        ]
                      }
                  }
          # if self.request.get('reminder1')=="reminder-none":
          #   event["reminders"]["overrides"].append({
          #         "method":"popup",
          #         "minutes": 40
          #       })
          http = decorator.http()

          service.events().insert(calendarId='primary', body=event).execute(http=http)
          self.response.out.write("<center><h2>Awesome, added %s to your calendar!</h2></center>"%(summary))
        except:
          self.response.out.write('<center>Oops, ran into an error when trying to add your homework to your calendar. <a href="/">Try again</a></center>')
        self.response.out.write("""<div class="row uniform 50%">
            <div class="4u 12u(3)"><center>
              <a href="/" class="button fit">Add More Homework</a><center>
              </center>
            </div>
            <div class="4u 12u(3)"><center>
              <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=RAXLBZE2JHKNJ" class="button fit">Donate</a><center>
            </center></div>
            <div class="4u 12u(3)"><center>
              <a href="https://www.google.com/calendar/" class="button fit">Go to Calendar</a><center>
              </center>
            </div></div>""")
class donate(webapp2.RequestHandler):
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('donate.html')
    self.response.write(template.render())
class clubawesome(webapp2.RequestHandler):
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('clubawesome.html')
    self.response.write(template.render())

application = webapp.WSGIApplication(
  [
   ('/',MainHandler),
   ('/addManualEvent',addManualEvent),
   ('/donate',donate),
   ('/clubawesome',clubawesome),
   (decorator.callback_path, decorator.callback_handler()),
  ],
  debug=True)
run_wsgi_app(application)

application.error_handlers[400] = handle_400
application.error_handlers[404] = handle_404
application.error_handlers[500] = handle_500
application.error_handlers[405] = handle_405