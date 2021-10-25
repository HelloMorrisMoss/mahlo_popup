"""To add a popup window to the Mahlo HMI PC at the laminators. Designed to be called from the command line over ssl."""

import argparse
import json
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from pprint import pprint  # for dev


class Popup:
    """A popup window with messages to respond to. Creats the window and messages based on a provided dictionary.

    """

    def __init__(me, input_dict):
        # set things up for the main window
        me._defdic = input_dict
        me.root = tk.Tk()
        me.root.title(me._defdic['main_win']['title'])
        me.root.geometry('800x500')
        me._wgts = {}
        me.styling()

        # dev_frame = tk.ttk.LabelFrame(me.root, text='Test frame')
        # dev_frame.grid(row=0, column=0)
        # dev_label = tk.ttk.Label(dev_frame, text='for dev')
        # dev_label.grid(row=0, column=0)
        #
        # me._wgts['dev_label'] = dev_label

        me.main_frm = tk.ttk.Frame(me.root)
        me.main_frm.grid(row=1, column=0, sticky='nesw', columnspan=3)
        setattr(me.main_frm, 'wgts', {})
        # me.hover_enter_factory(me.main_frm)
        me._wgts['main_frame'] = me.main_frm

        # add the frames for the messages and the widgets therein
        for mnum, message in enumerate(me._defdic['messages']):
            message['msg_txt']['timestamp'] = datetime.fromisoformat(message['msg_txt']['timestamp'])
            mlf = tk.ttk.LabelFrame(me.main_frm, text=message['title'])  #, style='Card.TFrame')
            me.main_frm.wgts[message['msg_id']] = mlf
            setattr(mlf, 'wgts', {})
            me.add_message_display(mlf, message)
            mlf.grid(column=0, row=mnum, padx=me.pad['x'], pady=me.pad['y'], sticky="nesw")
            me.add_buttons(mlf, message)
        me.recurse_hover(me._wgts['main_frame'].wgts)

        me.root.mainloop()

    def recurse_hover(me, wgts_dict):
        for wname, wgt in wgts_dict.items():
            if 'frame' not in wname:
                print(f'I am not a frame {wname}!')
                me.hover_enter_factory(wgt)
            else:
                print(f'I am a frame {wname}!')
            try:
                sub_wgts = getattr(wgt, 'wgts')
                if sub_wgts is not None:
                    me.recurse_hover(sub_wgts)
            except AttributeError:
                pass

    def hover_enter_factory(self, this_widget):
        print(this_widget)
        this_widget = this_widget
        winfo = this_widget.grid_info()

        def set_loc_label(event, this_widget):
            event_widget = event.widget
            # self._wgts['dev_label'].config(text=f'{winfo}')
            print(this_widget, event_widget, winfo)
        import functools

        this_fn = functools.partial(set_loc_label, this_widget=this_widget)

        this_widget.bind("<Enter>", this_fn)

    def styling(me):
        """Set the styling elements of the window.

        """
        me.root.tk.call("source", "Azure-ttk-theme-main/Azure-ttk-theme-main/azure.tcl")
        me.root.tk.call("set_theme", "dark")
        # frame padding
        me.pad = dict(
            x=5,
            y=3
        )
        me._wgt_styles = {'toggle': 'Switch.TCheckbutton', 'labelframe': ''}

        # looking at hiding the titlebar, no luck
        # me.root.wm_attributes('-fullscreen', 'True')  # fullscreen no titlebar
        # me.root.attributes('-fullscreen', 'True')  # same as with wm_
        # me.root.wm_attributes('-type', 'splash')  # linux specific
        # me.root.overrideredirect(1)  # this hides the titlebar, but it's placing the window in the corner

    def add_message_display(me, parent, message):
        msg = message['msg_txt']
        message_text = msg['template'].format(timestamp=msg['timestamp'], len_meters=msg['length_in_meters'])
        label = tk.ttk.Label(parent, text=message_text)
        label.grid(column=0, row=0, padx=me.pad['x'], pady=me.pad['y'], sticky="w")
        parent.wgts['msg_box'] = label

    def button_command(self):
        pass

    def add_toggle(me, button, side):
        # add a state tracker on the button, a side metadata-label, and add a side state tracker to the message frame
        setattr(button, 'active', True)
        setattr(button, 'side', side)
        setattr(button.master.master, side, True)

        def toggle_me(*args, **kwargs):
            print('args', args)
            print('kwargs', kwargs)
            # button = button
            button = args[0].widget
            print(f'button background was {button.cget("background")}')
            if button.active:
                print(f'{button.side} button was active, now setting to inactive')
                button.active = False
                setattr(button.master.master, button.side, False)
                button.config(background='SystemButtonFace')
            else:
                print(f'{button.side} button was inactive, now setting to active')
                button.active = True
                setattr(button.master.master, button.side, True)
                button.config(background='blue')
        button.bind("<Button-1>", toggle_me)
        # return toggle_me

    def add_buttons(me, parent, message):
        btn_frame = tk.ttk.Frame(parent, style='Card.TFrame')
        btn_frame.grid(column=1, row=0, padx=me.pad['x'], pady=me.pad['y'], sticky="nesw")
        button_dict = {'all_removed_button': {'params':
                                                  {'text': 'All of this length was removed.',
                                                   'command': lambda: print('You press my buttons!')},
                                              'grid_params': {'column': 0, 'row': 0, 'columnspan': 3}
                                              }}

        side_button_dict = {side: {'params':
                                       {'text': f'{side} was removed.'},
                                   'command': me.add_toggle,
                                   'grid_params': {'column': n, 'row': 1}
                                   } for n, side in enumerate(('Operator\nSide', 'Center\n', 'Foamline\nSide'))}

        button_dict.update(side_button_dict)
        for bnum, (btn, btndef) in enumerate(button_dict.items()):
            btn_frm = tk.ttk.Frame(parent)
            btn_frm.grid(**btndef['grid_params'])
            # btn_wgt = tk.Button(btn_frame, **btndef['params'])
            btn_wgt = ttk.Checkbutton(parent, style='Toggle.TButton', **btndef['params'])
            # btn_wgt = ttk.Checkbutton(parent, style='Switch.TCheckbutton', **btndef['params'])
            # btn_wgt.grid(row=0, column=0)
            # switch = ttk.Checkbutton(root, text='Switch', style='Switch.TCheckbutton', variable=var)
            btn_wgt.grid(**btndef['grid_params'])
            # my_command = btndef.get('command')
            # if my_command:
            #     btn_wgt.config(command=my_command(btn_wgt, btn))
            parent.wgts[btn] = btn_wgt

# TODO: buttons need to do something
#  perhaps the buttons should have predefined setups
#  all button, left, right center toggles of some sort
#  need to talk to some operators about how long until it makes sense to popup
#  doing it too soon they wouldn't have a chance and could be disruptive
#  respond (send it to a database?)
#  cbeck that this will work over ssl (opening in the normal session) otherwise probably flask


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pup_json', help='A json string defining the popups to display.')
    args = parser.parse_args()
    json_str = args.pup_json
    if json_str is None:
        oospec_len_meters = 4
        template_str = 'At {timestamp}\n there were {len_meters} meters oospec!'
        test_json_dict = {'messages': [{'title': 'Out of spec!',
                                        'msg_txt': {'template': template_str,
                                                    'timestamp': datetime.now().isoformat(),
                                                    'length_in_meters': oospec_len_meters},
                                        'buttons': ['removed!', 'oops!'],
                                        'msg_id': msg_id
                                        }
                                       for msg_id in ('msg123', 'msg456', 'msg789')],
                          'main_win': {'title': 'Messages received!'}
                          }
        json_str = json.dumps(test_json_dict)

    pup_dict = json.loads(json_str)

    pup = Popup(pup_dict)
