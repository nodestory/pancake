DEBUG = True
SECRET_KEY = 'my dirty secret'
LOGGER_NAME = 'pancake'
API_NAME = 'Pancake'
#--------------#
# EVE SETTINGS #
#--------------#
DOMAIN = {}
RESOURCE_METHODS = ('GET ', 'POST', 'DELETE')

#------------------#
# MONGODB SETTINGS #
#------------------#
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
# MONGO_USERNAME = ''
# MONGO_PASSWORD = ''
MONGO_DBNAME = 'pancake'


#----------------#
# REDIS SETTINGS #
#----------------#
REDIS_URL = 'redis://localhost:6379/0'
# other settings like connection pool go here


NOTIFICATION_SERVICE_URL = 'http://localhost:8081'
