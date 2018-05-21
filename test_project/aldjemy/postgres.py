"""Field types specific to postgres"""


def array_type(data_types, field):
    """
    Allows conversion of Django ArrayField to SQLAlchemy Array.
    Takes care of mapping the type of the array element.
    """
    from sqlalchemy.dialects import postgresql

    internal_type = field.base_field.get_internal_type()

    # currently no support for multi-dimensional arrays
    if internal_type in data_types and internal_type != 'ArrayField':
        sub_type = data_types[internal_type](field)
        if not isinstance(sub_type, (list, tuple)):
            sub_type = [sub_type]
    else:
        raise RuntimeError('Unsupported array element type')

    return postgresql.ARRAY(sub_type)
