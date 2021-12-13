import tkinter


def upsert_subscriber(self, subscriber, update_method):
    """Add or update a subscriber.

    :param self: type, the class instance whose subscriber list will be updated.
    :param subscriber: any, the subscriber to add or update.
    :param update_method: callable, the method or function to call using when publishing the new value.
    :return: str, 'subscriber updated' or 'subscriber added'
    """
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


def create_wrapper_for_class_methods(the_wrapped_class):
    """Get a method wrapper factory function for the class.

    :param the_wrapped_class: type, the class to get a method wrapper factory function for.
    :return: callable, the method wrapping factory function.
    """

    # the method wrapper factory function
    def method_publish_wrapper(method):
        """get the method wrapped in the update function."""

        # the method wrapper function
        def update_function(*args, **kwargs):
            """Update any subscribers the new length after performing the original method, then return its return.

            :param args: positional arguments to pass to the original method.
            :param kwargs: keyword arguments to pass to the original method.
            :return: any, the return value of the original method.
            """

            return_val = method(*args, **kwargs)  # the value returned be the original method
            self = args[0]  # calling this out of the class scope, self isn't automatically handed to the publish method
            the_wrapped_class.publish(self)  # so we borrow it from the method call that was in the class scope
            return return_val
        return update_function
    return method_publish_wrapper


class PublishListMetaWrap(type):
    """A metaclass that wraps the generated class' methods with a publish wrapper function."""

    def __new__(cls, name, base_classes, dct):
        wrapped_class = super().__new__(cls, name, base_classes, dct)
        wrap_methods = ['append', 'insert', 'pop', 'remove', 'extend', 'clear', '__delitem__']

        # add needs to return a publishing list or the publishing functionality would be lost, for: +=
        def __iadd__(self, other):
            return_value = PublishingLengthList(list.__add__(self, other))
            return_value._length_subscribers = self._length_subscribers
            return_value.publish()
            return return_value

        setattr(wrapped_class, '__iadd__', __iadd__)  # replace with the wrapped method

        # get a wrapping factory function for this class' methods
        wrap_publish = create_wrapper_for_class_methods(wrapped_class)

        # this is only intended for one base class (list), this would iterate all base classes, could be good or bad
        for base_class in base_classes:
            for attribute_name, attribute in base_class.__dict__.items():
                if callable(attribute):
                    if attribute_name in wrap_methods:
                        setattr(wrapped_class, attribute_name,
                                wrap_publish(attribute))  # replace with the wrapped method

        wrap_methods += ['__iadd__',]
        setattr(wrapped_class, '_publishing_methods', wrap_methods)  # to make this accessible if needed
        return wrapped_class


class PublishingLengthList(list, metaclass=PublishListMetaWrap):
    """A list with the subscriber/publisher design pattern for the length.

    If a method is called that may change the list length any subscribers will have their methods run with the new
    length used as the parameter. There are some important design choices regarding what will retain publishing and
    what will not. The goal being to prevent unintentionally creating multiple competing publishers.

    The consuming method should take the length, an int, and be prepared to be updated when the value isn't different.
    An example of why this could happen is adding an empty list (see below).

    ex:
        > items = 1, 2, 3
        > plist = PublishingLengthList(items)
        > plist._publishing_methods  # this will return the names of the methods that will publish to subscribers
        'append', 'insert', 'pop', 'remove', 'extend', 'clear', '__delitem__'  # * see slices below *

        # add a subscriber
        > plist.subscribe('any subscriber object, lambda x: print(f'updated to length: {x}'))
        > plist.publish()  # this can be used to publish the initial state, or at any time to update subscribers
        updated to length: 3

        # plist methods - below are examples of a few of the publishing methods using the subscriber above
        > plist.append(4)  # the publishing methods will call the update_method with the length as a parameter
        updated to length: 4
        > b_list = plist + [6, 7, 8]  # b_list will not update, it is a normal list * PUBLISHING LOST *
        > plist +=  [6, 7, 8]  # iadd will retain publishing and update the subscribers
        updated to length: 7
        > plist += []  # adding an empty list will update subscribers with the same length as before
        updated to length: 7
        > plist.pop(2)
        updated to length: 6

        # slices
        > s_list = plist[1:3]  # by default slicing will not retain publishing (normal list) * PUBLISHING LOST *
        > s_list.append(12)
        > plist.slices_publish = True  # slices retaining publishing can be enabled for uses such sd this:
        > plist = plist[1:3]
        updated to length: 2
        > plist._publishing_methods  # with slices_publish enabled, 'slice' will be added to _publishing_methods
        ['append', 'insert', 'pop', 'remove', 'extend', 'clear', '__delitem__', '__iadd__', 'slice']
        # note: the method overridden is actually __getitem__, ._publishing_methods was intended for ease of reference

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._length_subscribers = []
        self._slices_publish = False  # whether slices should publish their size (default False)

    @property
    def slices_publish(self):
        """Whether slices should inherit publishing functionality and subscribers list, True/False (default: False)"""
        return self._slices_publish

    @slices_publish.setter
    def slices_publish(self, new_value):
        self._slices_publish = new_value
        try:
            if new_value:
                self._publishing_methods.append('slice')
            else:
                self._publishing_methods.pop(self._publishing_methods.index('slice'))
        except AttributeError:
            pass  # this is just informational, if it's missing, not much of a problem

    def subscribe(self, subscriber, update_method):
        """Subscribe to the list length, receiving updates when it changes.

        Note:
        The update_method doesn't have to have anything to do with the subscriber, though it is a good idea. The
        subscriber is used to prevent multiple subscription and allow for changing the update_method.

        :param subscriber: object
        :param update_method: method, method or function to be called and passed the new length when it changes.
        :return: str, either 'subscriber added' or 'subscriber updated' if the subscriber was already subscribed.
        """
        try:
            getattr(self, '_length_subscribers')
        except AttributeError:
            self._length_subscribers = []
        return upsert_subscriber(self, subscriber, update_method)

    def unsubscribe(self, subscriber):
        """Remove a subscriber from the subscriber list.

        :param subscriber: any, the subscriber to remove.
        :return: bool, if the subscriber was found will return True, if they were not found False
        """
        for sub_num, subr in enumerate(self._length_subscribers):
            if subr == subscriber:
                del self._length_subscribers[sub_num]
                return True
        return False

    def publish(self):
        """Update the subscribers with what the length is now."""
        for subr in self._length_subscribers:
            subr['update_method'](self.__len__())

    def __getitem__(self, item):
        """If self.slices_publish is set to True, then slices returned will publish their length as the original.

            If self.slices_publish is False or the item is not a slice, behaves as list.__getitem__.
        :param item: any, the item to get (such as a slice) or self.__dict__ key.
        :return: any
        """
        gotitem = super().__getitem__(item)
        if isinstance(item, slice) and self.slices_publish:
            new_plist = PublishingLengthList(gotitem)
            new_plist._length_subscribers = self._length_subscribers
            new_plist.publish()
            return new_plist
        else:
            return gotitem


if __name__ == '__main__':
    # some rough testing
    a_list = PublishingLengthList((1, 2, 3))
    a_list.subscribe('any subscriber object', lambda x: print(f'updated to length: {x}'))
    print(f'check the list {a_list}')
    a_list.append(4)
    a_list.append(5)
    print(f'check the list {a_list}')
    print('The list appended correctly', a_list == [1, 2, 3, 4, 5])
    b_list = a_list + [6, 7, 8]
    print(b_list)
