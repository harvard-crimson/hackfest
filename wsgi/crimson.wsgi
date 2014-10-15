import os
import sys
import site

os.environ['DJANGO_SETTINGS_MODULE'] = 'hackserver.settings'
site.addsitedir('/srv/crimson/venv/lib/python2.7/site-packages')
sys.path.append('/srv/crimson/releases/current')
sys.path.append('/srv/crimson/releases/current/hackserver')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
