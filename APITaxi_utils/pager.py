from itertools import zip_longest

def pager(iterable, page_size=2):
    args = [iter(iterable)] * page_size
    fillvalue = object()
    for group in zip_longest(fillvalue=fillvalue, *args):
        yield (elem for elem in group if elem is not fillvalue)
