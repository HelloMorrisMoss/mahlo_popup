import tkinter


def publishing_var(var_type, *fn_args, **fn_kwargs):
    """Get a tkinter.StringVar or IntVar using the parameters provided that has a publisher pattern included.

    :param var_type: str or type, str/'str'/'string/tkinter.StringVar or similar for int.
    :param fn_args: positional arguments to pass along to the tkinter Var superclass.
    :param fn_kwargs: keyword arguments to pass along to the tkinter Var superclass.
    :return: object, a class instance of the Var.
    """
    if var_type in (int, 'int', 'integer', tkinter.IntVar):
        super_type = tkinter.IntVar
    elif var_type in (str, 'str', 'string', tkinter.StringVar):
        super_type = tkinter.StringVar

    class PublishingVar(super_type):
        """A tkinter.StringVar that includes a publisher design pattern. Functions otherwise identically."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._string_subscribers = []

        def subscribe(self, subscriber, update_method):
            """Subscribe an object to the string value, to be updated by passing the new value to the method.

            The update_method doesn't have to have anything to do with the subscriber, though it is a good idea. The
            subscriber is used to prevent multiple subscription and allow for changing the update_method.

            :param subscriber: object
            :param update_method: method, method or function to be called and passed the new value when the string is set.
            :return: str, either 'subscriber added' or 'subscriber updated' if the subscriber was already subscribed.
            """
            for sub_num, subr in enumerate(self._string_subscribers):
                if subr['subscriber'] is subscriber:
                    self._string_subscribers[sub_num] = {'subscriber': subscriber, 'update_method': update_method}
                    return 'subscriber updated'

            self._string_subscribers.append({'subscriber': subscriber, 'update_method': update_method})
            return 'subscriber added'

        def set(self, value):
            """Sets the string value like a normal tkinter.StringVar then publishes to the subscriber list the new value.

            :param value: str, the new value.
            """
            super().set(value)
            for subscriber in self._string_subscribers:
                subscriber['update_method'](value)

    return PublishingVar(*fn_args, **fn_kwargs)
    # @classmethod
    # def __int__(self, *args, **kwargs):
    #     return PublishingVar(tkinter.IntVar)
# class PublishingString(tkinter.StringVar):
#     """A tkinter.StringVar that includes a publisher design pattern. Functions otherwise identically."""
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self._string_subscribers = []
#
#     def subscribe(self, subscriber, update_method):
#         """Subscribe an object to the string value, to be updated by passing the new value to the method.
#
#         The update_method doesn't have to have anything to do with the subscriber, though it is a good idea. The
#         subscriber is used to prevent multiple subscription and allow for changing the update_method.
#
#         :param subscriber: object
#         :param update_method: method, method or function to be called and passed the new value when the string is set.
#         :return: str, either 'subscriber added' or 'subscriber updated' if the subscriber was already subscribed.
#         """
#         for sub_num, subr in enumerate(self._string_subscribers):
#             if subr['subscriber'] is subscriber:
#                 self._string_subscribers[sub_num] = {'subscriber': subscriber, 'update_method': update_method}
#                 return 'subscriber updated'
#
#         self._string_subscribers.append({'subscriber': subscriber, 'update_method': update_method})
#         return 'subscriber added'
#
#     def set(self, value):
#         """Sets the string value like a normal tkinter.StringVar then publishes to the subscriber list the new value.
#
#         :param value: str, the new value.
#         """
#         super().set(value)
#         for subscriber in self._string_subscribers:
#             subscriber['update_method'](value)


class PublishingLengthList(list):
    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)





