""" Basic two-directional linked list implementation.

@author Provotorov A. <merqcio11@gmail.com>
"""


class LinkedListItem:
    """ Two-directional linked list element.
    """
    def __init__(self, data, prev_item=None, next_item=None):
        self._data = data
        self._prev = prev_item
        self._next = next_item

    def next(self):
        return self._next

    def prev(self):
        return self._prev

    def data(self):
        return self._data


class LinkedList:
    """ Container of linked list element.
    """
    def __init__(self):
        self._items = []
        self._head = None
        self._tail = None

    def append(self, data):
        new = LinkedListItem(data)
        if len(self._items) == 0:
            self._head = new
        else:
            new._prev = self._tail
            self._tail._next = new

        self._tail = new
        self._items.append(new)

    def remove(self, item: LinkedListItem):
        if item:
            prev_one: LinkedListItem = item.prev()
            next_one: LinkedListItem = item.next()
            item._prev = None
            item._next = None

            if prev_one:
                prev_one._next = next_one
            else:
                self._head = next_one
            if next_one:
                next_one._prev = prev_one
            else:
                self._tail = prev_one

    def insert_after(self, item: LinkedListItem, new_item_data):
        if item:
            new_item = LinkedListItem(new_item_data)
            if item in self._items:
                next_item = item.next()
                new_item._prev = item
                new_item._next = next_item
                item._next = new_item

            self._items.append(new_item)
            return new_item

    def insert_before(self, item: LinkedListItem, new_item_data):
        if item:
            new_item = LinkedListItem(new_item_data)
            if item in self._items:
                prev_item = item.prev()
                new_item._prev = prev_item
                new_item._next = item
                item._prev = new_item
                if prev_item:
                    prev_item._next = new_item
                else:
                    self._head = new_item

            self._items.append(new_item)
            return new_item

    def head(self):
        return self._head

    def tail(self):
        if self._head is None:
            return None
        it = self._head
        while True:
            if it.next():
                it = it.next()
            else:
                return it

    def count(self):
        return len(self._items)

    def to_list(self):
        result = []
        linked_list_item = self.head()
        while linked_list_item:
            result.append(linked_list_item.data())
            linked_list_item = linked_list_item.next()
        return result

    @classmethod
    def from_list(cls, items_list):
        result = cls()
        for it in items_list:
            result.append(it)
        return result
