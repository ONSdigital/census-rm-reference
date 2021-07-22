import datetime
from json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return f'{obj.isoformat()}Z'

        return super(CustomJSONEncoder, self).default(obj)
