import datetime
import sys

from psycopg2 import connect, sql
from psycopg2.extras import execute_values
from pprint import pprint, pformat

from __init__ import lg, settings_dict


# ## TODO: enable ssl for the oee postgres server

## this one works for the OEE db
# cnn = psycopg2.connect(
#     dbname='Timescale',
#     user='postgres',
#     password=settings_dict['production_db_pw'],
#     host='10.155.0.21',
#     port='5432'
#     # ,
#     # sslmode='require'
# )


tables_dict = {
            'records': {'sql': """
                        CREATE TABLE IF NOT EXISTS records (
                            batch text PRIMARY KEY,
                            average float NOT NULL,
                            tstamp timestamp NOT NULL

                            );
                            """},
            'results': {'sql': """
                         CREATE TABLE  IF NOT EXISTS results (
                            id integer PRIMARY KEY,
                            batch_ID integer NOT NULL,
                            result float
                            );
                            """}
        }


class DatabaseConnection:
    def __init__(self, active_table_name: str = ''):
        # self.cnn = connect(
        #     dbname='postgres',
        #     user='postgres',
        #     password=settings_dict['production_db_pw'],
        #     host='localhost',
        #     port='5432'
        #     # ,
        #     # sslmode='require'
        # )
        self.cnn = connect(
            dbname='postgres',
            user='postgres',
            password=settings_dict['production_db_pw'],
            host='10.155.0.21',
            port='5432'
            # ,
            # sslmode='require'
        )
        self.cnn.autocommit = True
        self.crs = self.cnn.cursor()
        self._active_table = active_table_name
        self.atbl = active_table_name

        # try:
        #     self.cnn = psycopg2.connect(
        #                                 dbname='Timescale',
        #                                 user='postgres',
        #                                 password='',
        #                                 host='localhost',
        #                                 port='5432'
        #                                 # ,
        #                                 # sslmode='require'
        #                                 )
        #     self.cnn.autocommit = True
        #     self.crs = self.cnn.cursor()
        # except:
        #     lg.error(pformat(f'Cannot connect to database.'))

    def create_demo_table(self):
        demo_sql = """CREATE TABLE demo_table(id serial PRIMARY KEY, intval integer, strval varchar(20));"""
        self.crs.execute(demo_sql)

    def drop_demo_table(self):
        demo_sql = """DROP TABLE demo_table;"""
        self.crs.execute(demo_sql)

    def batch_insert_records(self, records_to_insert):
        insert_code = sql.SQL("""INSERT INTO records (batch, average, tstamp) VALUES %s ON CONFLICT DO NOTHING;""")
        insert_code = sql.SQL("""INSERT INTO records (batch, average, tstamp) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;""")
        values_template = """(%s, %s, %s)"""
        # lg.info(pformat(records_to_insert))
        # execute_values(self.crs, insert_code, records_to_insert, template=values_template)
        for row in records_to_insert:
            lg.debug(f"row {row}")
            # lg.debug(insert_code.format(row))
            self.crs.execute(insert_code, row)

    def get_todays_graph_data(self):
        select_sql = sql.SQL("""SELECT tstamp, average
                                FROM records
                                WHERE tstamp > now() - interval '48' hour
                                ORDER BY tstamp ASC;""")
        self.crs.execute(select_sql)
        return self.crs.fetchall()

    def insert_record(self, the_record):
        """Insert a single record into the records table.

        :param the_record: iterable of (str, float, datetime)
        """
        lg.debug(f'Attempting to insert a record {the_record}')
        raw_str = """INSERT INTO records (batch, average, tstamp) VALUES (%s, %s, %s) @@ROWCOUNT"""
        insert_sql = sql.SQL(raw_str).format(table_name=sql.Identifier('records'))
        self.crs.execute(insert_sql, the_record)
        lg.info(f'Inserted? {self.crs.fetchall()}')

    def peek_table(self, table_name=None):
        """Print the headers and ten rows from a table.

        :param table_name:
        """
        peek_sql = sql.SQL("""SELECT * FROM {table} LIMIT 10;""").format(table=sql.Identifier(table_name))
        self.crs.execute(peek_sql)
        lg.info([col.name for col in self.crs.description])
        pprint(self.crs.fetchall())

    def table_schema(self, table_name):
        raw_sql = """SELECT table_name, column_name, data_type
        FROM information_schema.columns WHERE table_name = '{table_name}';"""
        sql_code = sql.SQL(raw_sql).format(table_name=sql.Identifier(table_name))
        self.crs.execute(sql_code)
        pprint(self.crs.fetchall())

    def list_tables(self):
        sql_code = """SELECT *
            FROM pg_catalog.pg_tables
            WHERE schemaname != 'pg_catalog' AND 
                schemaname != 'information_schema';"""
        self.crs.execute(sql_code)
        lg.info([col.name for col in self.crs.description])
        lg.info(pformat(self.crs.fetchall()))

    @property
    def atbl(self):
        return self._active_table

    @atbl.setter
    def atbl(self, active_table_name: str):
        self._active_table = active_table_name

    def __str__(self):
        return pformat(str(self.__dict__))

    def create_database(self, tables_sql_dict: dict):
        for tbl, _val in tables_sql_dict.items():
            self.crs.execute(_val['sql'])


if __name__ == '__main__':
    # lg.debug(pformat(dir(conn)))
    cnt = DatabaseConnection('records')

    tgd = cnt.get_todays_graph_data()
    for row in tgd:
        print(row[0].day)

    # fake_records = [[str(123456 + i), 0.132 * i, datetime.timedelta(seconds=i) + datetime.datetime.now()] for i in range(10)]
    # # cnt.insert_record(fake_records[0])
    # lg.info(fake_records)
    # cnt.batch_insert_records(fake_records)
    # cnt.peek_table('records')

    # lg.info(cnt.atbl)
    # cnt.atbl = 'not a table'
    # lg.info(cnt.atbl)
    # lg.info(cnt)
    # cnt.insert_record([3, 'three'])
    # cnt.peek_table('demo_table')

    # cnt.create_database(tables_dict)
    # cnt.list_tables()
    # cnt.table_schema('records')

    # cnt.create_demo_table()
