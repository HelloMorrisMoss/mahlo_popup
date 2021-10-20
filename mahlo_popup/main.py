import argparse
import json
import tkinter as tk
from datetime import datetime

class Popup:
    def __init__(self, input_dict):
        self._definition_dict = input_dict
        self._root = tk.Tk()
        self._wgts = {}
        self._wgts['msg_box'] = tk.Label(self._root, text=self._definition_dict['message'])
        self._wgts['msg_box'].pack()
        for btn in self._definition_dict['buttons']:
            btn_wgt = tk.Button(self._root, text=btn)
            btn_wgt.pack()
            self._wgts[btn] = btn_wgt

        self._root.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pup_json', help='A json string defining the popups to display.')
    args = parser.parse_args()
    json_str = args.pup_json
    if json_str is None:

        oospec_len_meters = 4
        test_json_dict = {'popups': [{'title': 'Out of spec!',
                                     'message': f'At {datetime.now()}\n there were {oospec_len_meters} meters oospec!',
                                     'buttons': ['removed!', 'oops!']
                                     }
                          ]
                          }
        json_str = json.dumps(test_json_dict)

    pup_dict = json.loads(json_str)

    pup = Popup(pup_dict['popups'][0])
