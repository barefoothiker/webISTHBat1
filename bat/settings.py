import os
# Django settings for webKlincis project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Siddhartha Mitra', 'smitra@rockefeller.edu'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'batwebapp',
        'USER': 'root',
        'PASSWORD': 'admin',   
        'HOST': 'localhost',
        'PORT': '3306',        
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        }
    }
}

# table prefix name
DB_PREFIX = 'bat'
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/Users/mitras/projects/webISTHBat/static/img'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'idmm)d5h)kwxcopo%0rirfk@^88xcki4dx#slgp5_v#0)lt7gd'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
ROOT_URLCONF = 'urls'

STATIC_DOC_ROOT = '/Users/mitras/projects/webISTHBat/static'

STATIC_URL = '/Users/mitras/projects/webISTHBat/static/'

STATIC_ROOT = '/Users/mitras/projects/webISTHBat/static/'

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

TEMPLATE_DIRS = (
#    PROJECT_PATH + '/templates/',
    '/Users/mitras/projects/webISTHBat/templates/',
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'bat',
    'registration',
)

#SELECT Concat('ALTER TABLE ', TABLE_NAME, ' RENAME TO osc_', TABLE_NAME, ';') FROM INFORMATION_SCHEMA.TABLES where table_schema='db_name';

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.

TEMPLATE_CONTEXT_PROCESSORS =(
'django.contrib.auth.context_processors.auth',
'django.core.context_processors.debug',
'django.core.context_processors.i18n',
'django.core.context_processors.media',
'django.contrib.messages.context_processors.messages'
)

FILE_UPLOAD_HANDLERS = (
"django.core.files.uploadhandler.MemoryFileUploadHandler",
"django.core.files.uploadhandler.TemporaryFileUploadHandler",)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
#LOGGING = {
    #'version': 1,
    #'disable_existing_loggers': False,
    #'filters': {
        #'require_debug_false': {
            #'()': 'django.utils.log.RequireDebugFalse'
        #}
        #},
    #'handlers': {
        #'mail_admins': {
            #'level': 'ERROR',
            #'class': 'django.utils.log.AdminEmailHandler'
            #},
        #'stream_to_console': {
            #'level': 'DEBUG',
            #'class': 'logging.StreamHandler'
            #},
        #'file': {
            #'level': 'DEBUG',
            #'class': 'logging.FileHandler',
            #'filename': 'batreports_log.log',
            #},
        #},
    #'loggers': {
        #'django.request': {
            #'handlers': ['mail_admins', 'stream_to_console'],
            #'level': 'ERROR',
            #'propagate': True,
            #},
        #'batreports_logger': {
            #'handlers': ['file'],
            #'level': 'DEBUG',
            #'propagate': True,
            #},
    #}
#}
