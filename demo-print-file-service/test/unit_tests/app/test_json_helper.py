import datetime
import json

from app.json_helper import CustomJSONEncoder


def test_custom_json_encoder():
    time = {'time': datetime.datetime(2019, 11, 18, 10, 59, 42)}
    expected_time = '{"time": "2019-11-18T10:59:42Z"}'
    encoded_time = json.dumps(time, cls=CustomJSONEncoder)
    assert encoded_time == expected_time
