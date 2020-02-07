from starlette.config import Config
from starlette.datastructures import URL

# Parse configuration file here, make some methods to return certain info..

config = Config('.env')

DATABASE_URL = config('DATABASE_URL', cast=URL)
