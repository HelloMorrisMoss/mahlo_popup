"""To query the Ignition tag history database."""

from psycopg2 import connect, sql

from log_setup import lg
from untracked_config.th_creds import connection_dict


class TagIds:
    """A class to hold tag ids."""

    def __init__(self, tag_set_tids):
        self._tag_set = tag_set_tids
        if tag_set_tids is not None:
            self._tag_set_dict = {
                'lam1': {
                    'lot_number': 'mahlo/lam1/batchid',
                    'length': 'MAHLO/LAM1/MdMeterCount',
                    'shift_number': 'Miscellaneous Tags/Shift',
                    'recipe': 'MAHLO/LAM1/KeyName',
                    'file_name': 'MAHLO/LAM1/FileName',
                    'tabcode': 'MAHLO/LAM1/TiRollCount',
                    },
                'lam2': {
                    'lot_number': 'mahlo/lam2/batchid',
                    'length': 'MAHLO/LAM2/MdMeterCount',
                    'shift_number': 'Miscellaneous Tags/Shift',
                    'recipe': 'MAHLO/LAM2/KeyName',
                    'file_name': 'MAHLO/LAM2/FileName',
                    'tabcode': 'MAHLO/LAM2/TiRollCount',
                    },

                }
            # for development
            self._tag_set_dict['lam0'] = self._tag_set_dict['lam1']

    def process_paths(self, paths_to_id_function):
        """Process the tag ilike string to a tag id using the provided function.

        :param paths_to_id_function: callable, a function that takes an ilike pattern string and returns a tag id int.
        """

        for field, ilike_str in self._tag_set_dict[self._tag_set].items():
            _tag_id = paths_to_id_function(ilike_str)
            lg.debug('setting "%s" field using "%s" - id: %s', field, ilike_str, _tag_id)
            setattr(self, field, _tag_id)


class DatabaseConnection:
    """A database connection template."""

    def __init__(self, connection_dictionary=None, *args, **kwargs):
        """Initialize a new instance.

        :param connection_dictionary: dict, required parameters to pass to psycopg2.connect().
        """

        connection_dictionary = connection_dict if (connection_dictionary is None) else connection_dictionary
        self.cnn = connect(*args, **connection_dictionary, **kwargs)
        self.cnn.autocommit = True
        self.crs = self.cnn.cursor()


class TagHistoryConnector(DatabaseConnection):
    """A database connection for querying Ignition tag history from a postgres/Timescale database for a 'machine'.

    Tag ids are updated when instantiated. If a tag is removed and recreated or renamed (but still matches the ilike
    string) then it will query the new tag after reinstantiation or calling .update_tag_ids().
    """

    def __init__(self, tag_set=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history_table = sql.Identifier('sqlth_1_data')
        self._tag_entry_table = sql.Identifier('sqlt_te')
        self.tag_ids = TagIds(tag_set_tids=tag_set)
        self.update_tag_ids()

    def update_tag_ids(self):
        """Query the tag entry table for the tag ids matching the preset ilike strings."""

        self.tag_ids.process_paths(self.tag_id_query)

    def tag_id_query(self, tag_path_ilike_string):
        """Get the tag id that matches the tag path string.

        :param tag_path_ilike_string: str, a string for use with ilike in the database to match the tag path.
        :return: int, the tag id.
        """

        id_sql_query = r'''SELECT id FROM sqlth_te WHERE tagpath ILIKE %s AND retired IS NULL'''
        self.crs.execute(id_sql_query, (tag_path_ilike_string,))
        results = self.crs.fetchall()
        result_count = len(results)
        if result_count > 1:
            raise Warning('Multiple tags match ilike string pattern (tag_path_ilike_string): %s', tag_path_ilike_string)
        elif result_count == 0:
            raise Warning('No historized tag id found for %s', tag_path_ilike_string)
        return results[0]

    def get_recent_lots(self, lot_count: int = 5):
        """Get lot_count most recent lot numbers in increasing age order.

        :param lot_count: int, the number of lot numbers to get.
        :return: list, of up to lot_count tuples, each containing only the lot number (string).
        """

        results = self.get_recent_values(self.tag_ids.lot_number, lot_count)
        return [row[3] for row in results]

    def get_recent_values(self, tag_id, value_count=5):
        """Get value_count most recent values in increasing age order (most recent first).

        :param tag_id: int, the tag id in the tag history database.
        :param value_count: int, the number of lot numbers to get.
        :return: list, of 0 to lot_count tuples, each containing a row from the tag history.
        """

        lot_query = sql.SQL(r'''SELECT * FROM sqlth_1_data WHERE tagid = %s ORDER BY t_stamp DESC LIMIT %s;''')
        self.crs.execute(lot_query, (tag_id, value_count))
        return self.crs.fetchall()

    def current_lot_number(self):
        """Get the current lot number.

        :return: str, the current lot number.
        """

        return self.get_recent_lots(1)[0]

    def current_mahlo_length(self):
        """Get length from the Mahlo tag history.

        :return: float
        """

        result_row = self.get_recent_values(self.tag_ids.length, 1)
        return result_row[0][2]

    def get_current_shift_number(self):
        result_row = self.get_recent_values(self.tag_ids.shift_number, 1)
        return result_row[0][1]

    def get_current_recipe(self):
        result_row = self.get_recent_values(self.tag_ids.recipe, 1)
        return result_row[0][3]

    def get_current_file_name(self):
        result_row = self.get_recent_values(self.tag_ids.file_name, 1)
        return result_row[0][3]

    def get_current_tabcode(self):
        result_row = self.get_recent_values(self.tag_ids.tabcode, 1)
        return result_row[0][1]


if __name__ == '__main__':
    thist = TagHistoryConnector(f'lam1')
    lg.debug(thist.current_lot_number())
    lg.debug(thist.current_mahlo_length())
    lg.debug(thist.get_current_shift_number())
