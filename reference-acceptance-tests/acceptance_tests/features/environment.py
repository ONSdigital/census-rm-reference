from acceptance_tests.utilities.rabbit_helper import purge_queues


def before_scenario(context, _):
    purge_queues()


def after_all(_context):
    purge_queues()
