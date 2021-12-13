import tkinter


def upsert_subscriber(self, subscriber, update_method):
    for sub_num, subr in enumerate(self._length_subscribers):
        if subr['subscriber'] is subscriber:
            self._length_subscribers[sub_num] = {'subscriber': subscriber, 'update_method': update_method}
            return 'subscriber updated'
    self._length_subscribers.append({'subscriber': subscriber, 'update_method': update_method})
    return 'subscriber added'


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
            :param update_method: method, method or function to be called and passed the new value when the string is
            set.
            :return: str, either 'subscriber added' or 'subscriber updated' if the subscriber was already subscribed.
            """
            return upsert_subscriber(self, subscriber, update_method)

        def set(self, value):
            """Sets the string value like a normal tkinter.StringVar then publishes to the subscriber list the new
            value.

            :param value: str, the new value.
            """
            super().set(value)
            for subscriber in self._string_subscribers:
                subscriber['update_method'](value)

    return PublishingVar(*fn_args, **fn_kwargs)


class MetaWrap(type):
    """A metaclass that wraps the generated class' methods with a publish wrapper function."""

    def __new__(cls, name, base_classes, dct):
        wrapped_class = super().__new__(cls, name, base_classes, dct)
        wrap_methods = 'append', 'insert', 'pop', 'remove', 'extend', 'clear'#, '__add__'

        def __add__(self, other):
            return PublishingLengthList(list.__add__(self, other))


        # some specific additions
        setattr(wrapped_class, '_length_subscribers', [])
        # setattr(wrapped_class, '__add__', )

        # the wrapper function
        def wrap_publish(method):
            """get the method wrapped in the update function."""
            def update_function(*args, **kwargs):
                """Update any subscribers the new length after performing the original method, then return its return.

                :param args: positional arguments to pass to the original method.
                :param kwargs: keyword arguments to pass to the original method.
                :return: any, the return value of the original method.
                """
                return_val = method(*args, **kwargs)
                # print(f'{return_val=} - {args=}, {kwargs=}, {wrapped_class=}')
                for subr in wrapped_class._length_subscribers:
                    wc_self = args[0]
                    subr['update_method'](wc_self.__len__())
                return return_val
            return update_function

        # this is only intended for one base class (list), this would check all base classes, could be good or bad
        for base_class in base_classes:
            for field_name, field in base_class.__dict__.items():
                if callable(field):
                    if field_name in wrap_methods:
                        setattr(wrapped_class, field_name, wrap_publish(field))  # replace with the wrapped method
        return wrapped_class


class PublishingLengthList(list, metaclass=MetaWrap):
    """A list with the subscriber pattern for the length.

    If a method is called that may change the list length any subscribers will have their methods run with the new
    length used as the parameter.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def subscribe(self, subscriber, update_method):
        """Subscribe an object to the list length.

        Note:
        The update_method doesn't have to have anything to do with the subscriber, though it is a good idea. The
        subscriber is used to prevent multiple subscription and allow for changing the update_method.

        :param subscriber: object
        :param update_method: method, method or function to be called and passed the new value when the string is set.
        :return: str, either 'subscriber added' or 'subscriber updated' if the subscriber was already subscribed.
        """
        try:
            getattr(self, '_length_subscribers')
        except AttributeError:
            self._length_subscribers = []
        return upsert_subscriber(self, subscriber, update_method)

    def __add__(self, other):
        return PublishingLengthList(list.__add__(self, other))


if __name__ == '__main__':
    a_list = PublishingLengthList((1, 2, 3))
    a_list.subscribe(27, lambda x: print(f'updated to length: {x}'))
    print(a_list)
    a_list.append(4)
    a_list.append(5)
    print(a_list)
    print('The list appended correctly', a_list == [1, 2, 3, 4, 5])
    b_list = a_list + [6, 7, 8]
    print(b_list)

