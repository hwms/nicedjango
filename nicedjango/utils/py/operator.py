
__all__ = ['item_in', 'item_eq']


def item_in(index, container):
    def item_in_(values):
        return values[index] in container
    return item_in_


def item_eq(index, equal_value):
    def item_eq_(values):
        return values[index] == equal_value
    return item_eq_
