from datetime import datetime

from acceptance_tests.utilities.database_helper import purge_data
from acceptance_tests.utilities.rabbit_helper import purge_queues


def before_scenario(context, _):
    context.test_start_local_datetime = datetime.now()
    purge_queues()
    purge_data()


def after_all(_context):
    purge_queues()
