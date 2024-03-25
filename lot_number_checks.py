import datetime
import re

import requests

# matches a date
# ptn0 = r'^20[0-2][0-9]((0[1-9])|(1[0-2]))([0-2][1-9]|3[0-1])$'
# print(re.match(ptn0, '20240129'))

# # matches a lot number
# ptn1 = r'^20[0-2][0-9]((0[1-9])|(1[0-2]))([0-2][1-9]|3[0-1])([0-9]{4})$'
#
# print('ptn1', re.match(ptn1, '202401290123'))

# ptn_dl = re.compile(r'^(?P<date>(20[0-2][0-9]((0[1-9])|(1[0-2]))([0-2][1-9]|3[0-1])))(?P<lot>[0-9]{4})$')
ptn_dl = re.compile(
    r'^(?P<date>(20[0-2][0-9]((0[1-9])|(1[0-2]))([0-2][1-9]|3[0-1])))(?P<lot>[0-9]{4})(?:-)?(?P<hyp>(\d)?)$')

good_lots = '''202401220534
202401220108
202401220544
202401220486
202401190003
202401220052
202401190039'''.splitlines()

missing_lot_digit = '''20240122088
20240130094'''.splitlines()

missing_date_digit = '''20240220088'''.splitlines()

invalid_date_digits = '''202400220088
202501220088
202201220088
202401000088'''.splitlines()

extra_date_digit = '''202401122088'''.splitlines()

extra_lot_digit = '''202401220888'''.splitlines()

hyphenated = '''202401220088-1'''.splitlines()

# test_lots = \
#			missing_lot_digit +\
#			missing_date_digit + \
#			extra_date_digit + \
#			extra_lot_digit + \
#			hyphenated + \
#			invalid_date_digits + \
#			good_lots

test_lots = missing_date_digit + \
            extra_date_digit + \
            invalid_date_digits

# now = system.date.now()
# today = system.date.getDate(system.date.getYear(now), system.date.getMonth(now), system.date.getDayOfMonth(now))
now = datetime.datetime.now()
today = datetime.date.today()


def days_ago_java(ln):
    #	# this is a bit faster than the Integer version below
    #	theoretical_date = system.date.getDate(int(ln[:4]), int(ln[4:6]), int(ln[6:8]))
    ##	theoretical_date = java.util.Date(Integer(ln[:4]), Integer(ln[4:6]), Integer(ln[6:8]))
    #	return system.date.daysBetween(today, theoretical_date)

    return (today - datetime.date(year=int(ln[:4]), month=int(ln[4:6]), day=int(ln[6:8]))).days


#
# for li, ln in enumerate(test_lots):
#    lmatch = ptn_dl.match(ln)
#    if lmatch is None:
##        theoretical_date = datetime.date(year=int(ln[:4]), month=int(ln[4:6]), day=int(ln[6:8]))
##        days_ago = (today - theoretical_date).days
#        days_ago = days_ago_java(ln)
#        print('{}, {},  Date diff lot from today {} days'.format(li, ln, days_ago))
#    else:
#        print(li, ln, lmatch.groupdict() if lmatch is not None else None)

import re


# from java.io import IOException
# from java.net.http import HttpConnectTimeoutException


class DateError(ValueError):
    def __init__(self, message, error_on=None):
        super(DateError, self).__init__(message)
        self.error_on = error_on


class LotChecker(object):
    def __init__(self, lam_number):
        self.ln_re = re.compile(
            r'^(?P<date>(20[0-2][0-9]((0[1-9])|(1[0-2]))([0-2][1-9]|3[0-1])))(?P<lot>[0-9]{4})(?:-)?(?P<hyp>(\d)?)$')
        self.lam_num = lam_number
        self.reasonable_days_limit = 10  # mention the number of days back in message if it exceeds this
        self.now = datetime.datetime.now()  # todo: this will need to change as the instance can now be persistent
        self.year = self.now.year  # it can't be next year
        self.min_valid_year = self.year - 1  # shelf-life
        self.month_days = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 30, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

    def process_lot_number(self, lot_number):
        cd = self.check_lot(lot_number)

        if not cd['valid_ln']:
            message = self.get_lot_issue_message(cd)
            self.alert_pop_up(message, color_theme=u'warning')

    def get_lot_issue_message(self, check_dict):
        messages = []
        messages_dict = {'valid_date': lambda x: 'date' if not x else '',
                         'valid_length': lambda x: 'length {}'.format(x) if x not in (None, 'good') else '',
                         'days_ago': lambda x: '{} days old'.format(x) if (
                                 x and x > self.reasonable_days_limit) else '',
                         'date_error_on': lambda x: x if x is not None else '',
                         }
        for key_str in ('valid_date', 'valid_length', 'days_ago', 'date_error_on'):
            msg = messages_dict[key_str](check_dict[key_str])
            if msg:
                messages.append(msg)
        return 'Lot#: \n' + ', '.join(messages)

    def check_lot(self, lot_number):
        """Get a dictionary reporting on the vaditity of a lot number.

            The dictionary will contain the following keys; defaulting to None for values that were not available.
                'lot_number': str, lot number as input
                'lam_number': int, the laminator number as input
                'valid_ln': bool, whether it passed all checks and is a valid lot number
                'valid_date': bool, the date portion of the lot number is a valid date
                'valid_length': string, the length of the lot number is within the expected range: 'good', 'short', 'long'
                'days_ago': int, the number of days in the past that the lot number is from; 0 today, 1 yesterday, etc.
                'match_dict': dict, for successful regex re.match group dictionary
                'date_error_on': if the date is invalid, the first portion of the date that wasn't valid
        """
        check_dict = {'lot_number': lot_number,
                      'lam_number': self.lam_num,
                      'valid_ln': None,
                      'valid_date': None,
                      'valid_length': None,
                      'days_ago': None,
                      'match_dict': None,
                      'date_error_on': None
                      }
        match_d = self.ln_re.match(lot_number)

        # check the date portion of the lot number
        self.check_lot_date(lot_number, check_dict)

        if match_d is not None:
            check_dict['match_dict'] = match_d.groupdict()
            if check_dict['valid_date']:
                check_dict['valid_ln'] = True
            else:
                check_dict['valid_ln'] = False

        # check the length of the lot number
        self.check_lot_length(lot_number, check_dict)

        return check_dict

    def check_lot_length(self, lot_number, check_dict):
        llot = len(lot_number)

        if '-' in lot_number:
            check_dict['valid_length'] = llot > 12 and llot <= 14
        else:
            int(lot_number)
            if llot == 12:
                check_dict['valid_length'] = 'good'
            elif llot < 12:
                check_dict['valid_length'] = 'short'
            elif llot > 12:
                check_dict['valid_length'] = 'long'

        check_dict['valid_length'] = check_dict['valid_length'] if check_dict['valid_length'] is not None else False

    def check_lot_date(self, lot_number, check_dict):
        try:
            days_ago, extracted_date = self.days_ago(lot_number)
            check_dict['days_ago'] = days_ago
            check_dict['extracted_date'] = extracted_date
            if abs(days_ago) > self.reasonable_days_limit:
                check_dict['valid_date'] = True
        except DateError as der:
            check_dict['date_error_on'] = der.error_on

    def alert_pop_up(self, message, color_theme=u'warning'):
        # hc = system.net.httpClient(10000)
        # requests.post()

        params = {
            'url': 'http://10.155.1.105:5000/button_msg',  # todo: get ip dynamically
            'json': {
                u'action': u'set_additional_msg',
                u'additional_message_text': message,
                u'color_theme': color_theme,
            }
        }

        # todo: retry? what if they change the lot in the mean time?
        requests.put(**params)
        # try:
        # 	hc.post(**params)
        # except IOException as ioer:
        # 	if isinstance(g_ioer.getCause(), HttpConnectTimeoutException):
        # 		print('Timeout')
        # 	else:
        # 		print(ioer)

    def days_ago(self, ln):
        year = int(ln[:4])
        if (year > self.year) or (year < self.min_valid_year):
            raise DateError('Invalid value for year: {}'.format(year), 'year')

        month = int(ln[4:6])
        if (month < 1) or (month > 12):
            raise DateError('Invalid value for month: {}'.format(month), 'month')

        day = int(ln[6:8])
        if (day < 1) or (day > self.month_days[month]):
            raise DateError('Invalid value for day: {}'.format(day), 'day')
        # java months start at 0
        extracted_date = datetime.date(year, month, day)
        days_ago = (today - extracted_date).days
        return days_ago, extracted_date


# Initialize LotChecker with an example laminator number
checker = LotChecker(lam_number=0)
test_lots = [
    {'test_for': 'invalid_date_digit (year-future)', 'lot': '202501220088', 'message': ['date', 'year'],
     'result_dict': {'lam_number': 0, 'valid_length': 'good', 'valid_ln': False, 'days_ago': None,
                     'lot_number': '202501220088', 'valid_date': None, 'date_error_on': 'year',
                     'match_dict': {'date': '20250122', 'lot': '0088', 'hyp': ''}}},
    {'test_for': 'invalid_date_digit (month)', 'lot': '202400220088', 'message': ['date', 'month'],
     'result_dict': {'lam_number': 0, 'valid_length': 'good', 'valid_ln': None, 'days_ago': None,
                     'lot_number': '202400220088', 'valid_date': None, 'date_error_on': 'month', 'match_dict': None}},
    {'test_for': 'invalid_date_digit (day)', 'lot': '202401000088', 'message': ['date', 'day'],
     'result_dict': {'lam_number': 0, 'valid_length': 'good', 'valid_ln': None, 'days_ago': None,
                     'lot_number': '202401000088', 'valid_date': None, 'date_error_on': 'day', 'match_dict': None}},
    {'test_for': 'missing_date_digit', 'lot': '20240220088', 'message': ['length short', '34 days old'],
     'result_dict': {'lam_number': 0, 'valid_length': 'short', 'valid_ln': None, 'days_ago': 34,
                     'lot_number': '20240220088', 'valid_date': True, 'date_error_on': None,
                     'extracted_date': datetime.date(2024, 2, 20), 'match_dict': None}},
    {'test_for': 'extra_date_digit', 'lot': '202401122088', 'message': ['73 days old'],
     'result_dict': {'lam_number': 0, 'valid_length': 'good', 'valid_ln': True, 'days_ago': 73,
                     'lot_number': '202401122088', 'valid_date': True, 'date_error_on': None,
                     'extracted_date': datetime.date(2024, 1, 12),
                     'match_dict': {'date': '20240112', 'lot': '2088', 'hyp': ''}}},
    {'test_for': 'invalid_date_digit (year- too old)', 'lot': '202201220088', 'message': ['date', 'year'],
     'result_dict': {'lam_number': 0, 'valid_length': 'good', 'valid_ln': False, 'days_ago': None,
                     'lot_number': '202201220088', 'valid_date': None, 'date_error_on': 'year',
                     'match_dict': {'date': '20220122', 'lot': '0088', 'hyp': ''}}},
]


def assertEqual(value_1, value_2, msg):
    if value_1 == value_2:
        return True
    else:
        raise AssertionError(msg)


import sys

for test_lot in test_lots:
    sys.stdout.write('Testing for {}'.format(test_lot['test_for']))  # print without newline

    # Call check_lot and assert the returned dictionary matches the expected result
    result = checker.check_lot(test_lot['lot'])
    assertion_results = []

    # Assert each key in the expected result is equal to the corresponding value in the result
    for key, value in test_lot['result_dict'].items():
        is_equal = assertEqual(result[key], value,
                               msg="Lot: {} - Mismatch in key: {} - og: {} vs {}".format(test_lot['lot'], key, value,
                                                                                         result[key]))
        assertion_results.append(is_equal)

    # check that the message has the important parts
    msg = checker.get_lot_issue_message(result)
    assertion_results.append(all([tag in msg for tag in test_lot['message']]))

    # print result of test
    if all(assertion_results):
        print(': Pass')
    else:
        print(': Fail')

checker.process_lot_number(test_lots[0]['lot'])
