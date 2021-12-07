"""For development helpers, in their own module to avoid circular imports and keep things organized."""
from datetime import datetime


def get_dummy_dict_by_ids(id_list=[1, 2, 3], oospec_len_meters=5.55,
                   template_str='At {timestamp}\nthere were {len_meters} meters oospec!'):
    return {'messages': [get_message_dict(mnum, msg_id, oospec_len_meters, template_str)
                         for mnum, msg_id in
                         enumerate(id_list)],
            'main_win': {'title': 'Messages received!', 'timestamp_display_format': r'%I:%M %d-%b'}
            }


def get_message_dict(mnum, msg_id, oospec_len_meters, template_str):
    return {'title': 'Out of spec!',
            'msg_txt': {'template': template_str,
                        'timestamp': datetime.now().isoformat(),
                        'length_in_meters': oospec_len_meters},
            'buttons': ['removed!', 'oops!'],
            'toggle_count_guess': mnum + 1,
            'msg_id': msg_id
            }


def get_dummy_dict(oospec_len_meters=5.55,
                   template_str='At {timestamp}\nthere were {len_meters} meters oospec!',
                   msg_count=5):
    return {'messages': [create_message_dict(mnum + 1, msg_id, oospec_len_meters, template_str)
                         for mnum, msg_id in
                         enumerate(('msg123', 'msg456', 'msg789', 'msg987', 'msg654'))],
            'main_win': {'title': 'Messages received!', 'timestamp_display_format': r'%I:%M %d-%b'}
            }


def create_message_dict(rolls_count_guess, msg_id, oospec_len_meters, template_str):
    return {'title': 'Out of spec!',
            'msg_txt': {'template': template_str,
                        'timestamp': datetime.now().isoformat(),
                        'length_in_meters': oospec_len_meters},
            'buttons': ['removed!', 'oops!'],
            'toggle_count_guess': rolls_count_guess,
            'msg_id': msg_id
            }


def get_empty_dict(oospec_len_meters,
                   template_str='At {timestamp}\nthere were {len_meters} meters oospec!',
                   msg_count=5):
    # return {'messages': [create_message_dict(0, 0, 0, 'No new defects detected.')],
    empty_message_dict = create_message_dict(0, 0, 0, 'No new defects detected.')
    empty_message_dict['empty'] = True
    return {'messages': [empty_message_dict],
            'main_win': {'title': 'Messages received!', 'timestamp_display_format': r'%I:%M %d-%b'}
            }