from conf import global_settings

try:
    import settings as local_settings
except:
    raise Exception('You need to create a settings module')


class LazySettings:
    def __getattr__(self, name):
        if hasattr(local_settings, name):
            return getattr(local_settings, name)
        return getattr(global_settings, name)

settings = LazySettings()
