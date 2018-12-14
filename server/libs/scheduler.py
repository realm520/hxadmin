from flask_apscheduler import APScheduler


class Scheduler(APScheduler):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance


scheduler = Scheduler()
