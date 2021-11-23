"""For development helpers, in their own module to avoid circular imports and keep things organized."""
from datetime import datetime


def get_dummy_dict(oospec_len_meters,
                   template_str='At {timestamp}\nthere were {len_meters} meters oospec!',
                   msg_count=5):
    return {'messages': [{'title': 'Out of spec!',
                          'msg_txt': {'template': template_str,
                                      'timestamp': datetime.now().isoformat(),
                                      'length_in_meters': oospec_len_meters},
                          'buttons': ['removed!', 'oops!'],
                          'toggle_count_guess': mnum + 1,
                          'msg_id': msg_id
                          }
                         for mnum, msg_id in
                         enumerate(('msg123', 'msg456', 'msg789', 'msg987', 'msg654'))],
            'main_win': {'title': 'Messages received!', 'timestamp_display_format': r'%I:%M %d-%b'}
            }