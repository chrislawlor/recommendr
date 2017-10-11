import os


class ImproperlyConfigured(Exception):
    pass


def get_env_var(varname, default=None):
    try:
        return os.environ[varname]
    except KeyError:
        if default is not None:
            return default
    msg = "You must set the %s environment variable." % varname
    raise ImproperlyConfigured(msg)


REDIS_HOST = get_env_var("REDIS_HOST", 'localhost')
REDIS_PORT = int(get_env_var("REDIS_PORT", 6379))
REDIS_DB = int(get_env_var("REDIS_DB", 1))
