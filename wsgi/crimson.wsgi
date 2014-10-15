import os
import sys
import site

os.environ['DJANGO_SETTINGS_MODULE'] = 'crimsononline.settings'
site.addsitedir('/srv/crimson/venv/lib/python2.7/site-packages')
sys.path.append('/srv/crimson/releases/current')
sys.path.append('/srv/crimson/releases/current/crimsononline')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

#from werkzeug.debug import DebuggedApplication
#application = DebuggedApplication(application, evalex=True)

import newrelic.agent
newrelic.agent.initialize('/srv/crimson/newrelic.ini')
application = newrelic.agent.wsgi_application()(application)
