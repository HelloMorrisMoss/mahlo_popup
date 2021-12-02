import logging
import os
import sqlite3
from pprint import pformat, pprint

# from retry import retry
#
# from __init__ import lg, settings_dict
# from helpers import try_date

# db_file_path = './database/db_file.sqlite3'
from pgdb import DatabaseConnection

lg = logging.getLogger('mds_popup_window')
logging.basicConfig()
lg.setLevel(logging.DEBUG)

db_file_path = settings_dict['file_paths']['database']

tables_dict = {
            'records': {'sql': """
                        CREATE TABLE records (
                            batch text PRIMARY KEY,
                            average float NOT NULL,
                            tstamp timestamp NOT NULL

                            );
                            """},
            'results': {'sql': """
                         CREATE TABLE results (
                            id integer PRIMARY KEY,
                            batch_ID integer NOT NULL,
                            result float
                            );
                            """}
        }


def create_a_table(ct_con, ct_crs, table_name):
    sql_code = tables_dict[table_name]['sql']
    lg.info(f'Creating table {table_name} using {sql_code}')
    ct_crs.execute(sql_code)


def peek_table(table_name):  # prt_connection, prt_cursor):
    """NOT SAFE, FOR DEVELOPMENT ONLY."""
    prt_string = f"""
    SELECT * FROM {table_name};
    """
    for rn, row in enumerate(crs.execute(prt_string).fetchall()):
        lg.debug(f'{rn} on {table_name}: {row}')


def add_results(ar_con, ar_cur, batch_id, results):
    res_sql = """INSERT INTO results (batch_id, result) VALUES (?, ?)"""
    for resl in results:
        ar_cur.execute(res_sql, (batch_id, resl))


@retry(sqlite3.OperationalError, tries=2, delay=2)
def averages_to_db(avg_dictionary):
    dbc, crs = get_con_crs()
    for key, val_dict in avg_dictionary.items():
        temp_dict = {'batch': key, **val_dict}
        results = temp_dict.pop('vals')
        lg.debug(temp_dict)
        lg.debug(results)
        try:
            record_id = add_record(dbc, crs, temp_dict)
            add_results(dbc, crs, record_id, results)
        except sqlite3.IntegrityError:
            lg.debug(f'entry exists for {key}')

    dbc.commit()


def upload_to_oee_db(destination='records'):
    lg.info('Uploading recent results to remote db.')
    oee_db = DatabaseConnection(destination)
    oee_db.batch_insert_records(get_todays_records_for_oee())


def add_record(ar_con, ar_cur, entry):
    add_sql = """INSERT INTO records (batch, average, tstamp) VALUES (?, ?, ?)"""

    # in case a table is missing somehow
    tries = 3
    while tries:
        tries -= 1
        try:
            ar_cur.execute(add_sql, (entry['batch'], entry['average'], entry['tstamp']))
        except sqlite3.OperationalError as table_er:
            # catch that a table is missing, make sure it doesn't exist, then try to recreate it
            er_on_table = table_er.message.split('no such table: ')[-1]  # get the table name
            if not check_for_table(er_on_table):  # check if it actually exists
                lg.warning('''sqlite3 table %s doesn't exist, creating.''', er_on_table)
                create_a_table(er_on_table)  # if it doesn't create it

        lg.debug(f'new entry id {ar_cur.lastrowid}')
        return ar_cur.lastrowid


def drop_a_table(drc_con, drc_crs, table_name):
    dt_sql = f"""DROP TABLE {table_name}"""
    lg.info(f'Dropping {table_name} using sql: {dt_sql}')
    drc_crs.execute(dt_sql)


def reset_db():  # rd_con, rd_cur):
    dbc, crs = get_con_crs()
    for table in tables_dict.keys():
        try:
            drop_a_table(dbc, crs, table)
        except sqlite3.OperationalError:
            lg.warning(f'No table named {table}.')
        lg.info(f'creating {table} table.')
        create_a_table(dbc, crs, table)


def get_todays_records_for_oee(crs=None):
    if crs is None:
        dbc, crs = get_con_crs()
    rec_sql = """
    SELECT batch, average, tstamp "[timestamp]" FROM records WHERE tstamp > (SELECT date('now', '-19 day'));
    """
    crs.execute(rec_sql)
    return crs.fetchall()


def recent_records(crs=None):
    if crs is None:
        dbc, crs = get_con_crs()
    rec_sql = """
    SELECT tstamp "[timestamp]", average FROM records WHERE tstamp > (SELECT datetime('now', '-1 day'));
    """  # TODO: set this back to 1 day

    # rec_sql = """
    #     SELECT tstamp "[timestamp]", average FROM records WHERE tstamp > (SELECT date('now', '-14 day'));
    #     """
    crs.execute(rec_sql)
    return crs.fetchall()


def rec_res_nestlist():
    """Get the records for the last day as nested lists rows: [[col_1], [col_2]..]

    :return:
    """
    dbc, crs = get_con_crs()
    nested_lists = [[try_date(col) for col in row] for row in recent_records(crs)]
    # print(nested_lists[10])
    return nested_lists


def get_con_crs():
    lg.debug(db_file_path)
    with sqlite3.connect(db_file_path) as dbc:
        crs = dbc.cursor()
        return dbc, crs


def delete_future_records():
    dbc, crs = get_con_crs()
    delete_sql = """DELETE FROM records WHERE tstamp >= datetime('now')"""
    crs.execute(delete_sql)
    dbc.commit()
    # lg.debug(pformat(crs.fetchall()))


def when_is_now_db():
    dbc, crs = get_con_crs()
    now_sql = """SELECT datetime('now');"""
    lg.debug(f'Sqlite now: {crs.execute(now_sql).fetchall()}')


def check_for_table(table_name):
    dbc, crs = get_con_crs()
    if table_name == 'records':
        query = """SELECT name FROM sqlite_master WHERE type='table' AND name='records';"""
    elif table_name == 'results':
        query = """SELECT name FROM sqlite_master WHERE type='table' AND name='results';"""
    else:
        raise ValueError('Invalid table name.')

    return crs.execute(query)


if __name__ == '__main__':

    dbc, crs = get_con_crs()

    # create table
    # create_records_table(dbc, crs)

    # drop_a_table(dbc, crs, 'records')
    # create_a_table(dbc, crs, 'records')

    # when_is_now_db()
    delete_future_records()
    pprint(recent_records())
    # # drop and recreate empty tables
    # reset_db(dbc, crs)
    # peek_table('records')  # dbc, crs)
    # peek_table('results')
    lg.debug('prepeek over')



    # # look at recent data (last day)
    # rec_res = recent_records(crs)
    # lg.debug(f'There are {len(rec_res)} rows.')
    # overflow_limit = 3000
    # overflow_counter = 0
    # for row in rec_res:
    #     lg.debug(f'{row} {type(row[0])} for {row[0]}')
    #     if overflow_counter > overflow_limit:
    #         break
    #     overflow_counter += 1

    # to look at the schemas
    # for tbl in crs.execute("""SELECT * FROM sqlite_master WHERE type='table'""").fetchall():
    #     lg.debug(pformat(tbl))
    # drop_records_table(dbc, crs)
    # peek_records_table(dbc, crs)

    # dbc.close()
