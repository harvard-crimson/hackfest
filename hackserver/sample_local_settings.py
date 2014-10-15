import os

DEBUG = True

TEMPLATE_DEBUG = False

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '6a#kq*t83jt8kj3=*035n4b-_w0o+!-k_t12d6dvlmagpq9%v4'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
