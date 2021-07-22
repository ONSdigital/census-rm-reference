from datetime import datetime
import uuid

from behave import step
from tenacity import retry, retry_if_exception_type, stop_after_delay, wait_fixed

from acceptance_tests.utilities.database_helper import open_cursor
from acceptance_tests.utilities.sftp_helper import SftpUtility
from config import Config


@retry(retry=retry_if_exception_type(FileNotFoundError), wait=wait_fixed(1), stop=stop_after_delay(120))
def get_print_file_rows_from_sftp(after_datetime, pack_code):
    with SftpUtility() as sftp_utility:
        supplier = Config.SUPPLIERS_CONFIG['SUPPLIER_A'].get('sftpDirectory')
        files = sftp_utility.get_all_files_after_time(after_datetime, pack_code, supplier, 'csv.gpg')
        print_file_rows = sftp_utility.get_files_content_as_list(files, pack_code, supplier)
        if not print_file_rows:
            raise FileNotFoundError
        return print_file_rows


@step("a print action rule has been created")
def create_print_action_rule(context):
    with open_cursor() as cur:
        add_trigger_query = """INSERT INTO cases.action_rule (id, classifiers, has_triggered, trigger_date_time)
                               VALUES(%s,'','f',%s)"""
        trigger_vars = (str(uuid.uuid4()), datetime.utcnow())
        cur.execute(add_trigger_query, vars=trigger_vars)


@step("a print file is created with correct rows")
def check_print_file(context):
    actual_print_file_rows = get_print_file_rows_from_sftp(context.test_start_local_datetime, 'TEST_PACK')
    assert(actual_print_file_rows[0] == "666 Long Lane SW1 1ST")
