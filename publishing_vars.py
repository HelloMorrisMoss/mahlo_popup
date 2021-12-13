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

# from functools import wraps
#
# def wrap_update_length(in_func):
#     print(in_func)
#     # @wraps
#     def inner_wrap(self, *args, **kwargs):
#         print(f'{args=}')
#         print(f'{kwargs=}')
#         print(f'{in_func=}')
#         return_val = in_func(self, *args, **kwargs)
#         new_lenth = self.__len__()
#         for subr in self._length_subscribers:
#             subr['update_method'](new_lenth)
#         print(f'{self._length_subscribers}')
#         return return_val
#     return inner_wrap
#
#
#
#
#
#
# class PublishingLengthList(list):
#     # print('plb start')
#     # _length_subscribers = []
#     # _super = None
#
#     # def __new__(cls, *args, **kwargs):
#     #     print('newing')
#     #     return self.__new__(cls, *args, **kwargs)
#
#     def __int__(self, *args, **kwargs):
#         # self._super = super()
#         print('initializing')
#         super().__init__(*args, **kwargs)
#         self._length_subscribers = []
#
#         self._sub_append = self.append
#         self.append = wrap_update_length(self._sub_append)
#         print(self.append)
#         # for fn_name in ('append,'):
#         #     def this_func(*args, **kwargs):
#         #        return_value = getattr(self, fn_name)(*args, **kwargs)
#         #        new_lenth = self.__len__()
#         #        print(f'internal new length {new_lenth}')
#         #        for subr in self._length_subscribers:
#         #            subr['update_method'](new_lenth)
#         #        return return_value
#         #     setattr(self, fn_name, this_func)
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
#         print(f'adding subscriber')
#         try:
#             getattr(self, '_length_subscribers')
#         except AttributeError:
#             self._length_subscribers = []
#         for sub_num, subr in enumerate(self._length_subscribers):
#             if subr['subscriber'] is subscriber:
#                 self._length_subscribers[sub_num] = {'subscriber': subscriber, 'update_method': update_method}
#                 return 'subscriber updated'
#
#         self._length_subscribers.append({'subscriber': subscriber, 'update_method': update_method})
#         return 'subscriber added'
#
#     # @wrap_update_length
#     # def append(self, *args, **kwargs):  # real signature unknown
#     #     """ Append object to the end of the list. """
#     #     print(f'{self} - {args=} - {kwargs=}')
#     #     # super(self).append(*args, **kwargs)
#     #     # pass
#     #     return wrap_update_length(list.append)
#     #
#     #
#     # def clear(self, *args, **kwargs):  # real signature unknown
#     #     """ Remove all items from list. """
#     #     pass
#     #
#     # def extend(self, *args, **kwargs):  # real signature unknown
#     #     """ Extend list by appending elements from the iterable. """
#     #     pass
#     #
#     #
#     # def insert(self, *args, **kwargs):  # real signature unknown
#     #     """ Insert object before index. """
#     #     pass
#     #
#     # def pop(self, *args, **kwargs):  # real signature unknown
#     #     """
#     #     Remove and return item at index (default last).
#     #
#     #     Raises IndexError if list is empty or index is out of range.
#     #     """
#     #     pass
#     #
#     # def remove(self, *args, **kwargs):  # real signature unknown
#     #     """
#     #     Remove first occurrence of value.
#     #
#     #     Raises ValueError if the value is not present.
#     #     """
#     #     pass
#
#
# # def make_publist(*args, **kwargs):
# #     class PubList(list):
# #         def __init__(self, *args, **kwargs):
# #             super().__init__(*args, **kwargs)
# #
# #     publist = PubList(*args, **kwargs)
# #
# #     def subscribe(self, subscriber, update_method):
# #         """Subscribe an object to the string value, to be updated by passing the new value to the method.
# #
# #         The update_method doesn't have to have anything to do with the subscriber, though it is a good idea. The
# #         subscriber is used to prevent multiple subscription and allow for changing the update_method.
# #
# #         :param subscriber: object
# #         :param update_method: method, method or function to be called and passed the new value when the string is set.
# #         :return: str, either 'subscriber added' or 'subscriber updated' if the subscriber was already subscribed.
# #         """
# #         print(f'adding subscriber')
# #         for sub_num, subr in enumerate(self._length_subscribers):
# #             if subr['subscriber'] is subscriber:
# #                 self._length_subscribers[sub_num] = {'subscriber': subscriber, 'update_method': update_method}
# #                 return 'subscriber updated'
# #
# #         self._length_subscribers.append({'subscriber': subscriber, 'update_method': update_method})
# #         return 'subscriber added'
# #
# #     # setattr(publist, 'subscribe', subscribe)
# #     publist.subscribe = subscribe
# #     publist.append = wrap_update_length(publist.append)
# #     print(dir(publist))
# #     return publist


def wrap_publish(method):
   def inner(*args, **kwargs):
       return_val = method(*args, **kwargs)
       print(f'{return_val=}')
       return return_val
   return inner


class MetaWrap(type):
    """TODOcstring"""
    def __new__(cls, name, bases, dct):
        child = super().__new__(cls, name, bases, dct)
        wrap_methods = 'append', 'insert', 'pop'  # TODO: add the rest
        for base in bases:
            for field_name, field in base.__dict__.items():
                if callable(field):
                    if field_name in wrap_methods:
                        # og_method = getattr()
                        # def wrapped_method
                        setattr(child, field_name, wrap_publish(field))
        return child

class PublishingLengthList(list, metaclass=MetaWrap):

    def subscribe(self, subscriber, update_method):
        """Subscribe an object to the string value, to be updated by passing the new value to the method.

        The update_method doesn't have to have anything to do with the subscriber, though it is a good idea. The
        subscriber is used to prevent multiple subscription and allow for changing the update_method.

        :param subscriber: object
        :param update_method: method, method or function to be called and passed the new value when the string is set.
        :return: str, either 'subscriber added' or 'subscriber updated' if the subscriber was already subscribed.
        """
        print(f'adding subscriber')
        try:
            getattr(self, '_length_subscribers')
        except AttributeError:
            self._length_subscribers = []
        for sub_num, subr in enumerate(self._length_subscribers):
            if subr['subscriber'] is subscriber:
                self._length_subscribers[sub_num] = {'subscriber': subscriber, 'update_method': update_method}
                return 'subscriber updated'

        self._length_subscribers.append({'subscriber': subscriber, 'update_method': update_method})
        return 'subscriber added'


if __name__ == '__main__':
    # a_list = make_publist((1, 2, 3))
    # a_list = PublishingLengthList((1, 2, 3))
    a_list = PublishingLengthList()
    # b_list = PublishingLengthList((5, 6, 7))
    # a_list = MetaWrap.__new__('PublishingLengthList', (list,), {})
    a_list.subscribe(27, lambda x: print(f'updated to length: {x}'))
    print(a_list)
    # print(dir(a_list))
    a_list.append(5)
    a_list.append(5)
    print(a_list)


