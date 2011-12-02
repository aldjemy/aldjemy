def to_list(qs_or_ilist):
    if hasattr(qs_or_ilist, 'all'):
        return list(qs_or_ilist.all())
    return list(qs_or_ilist)
