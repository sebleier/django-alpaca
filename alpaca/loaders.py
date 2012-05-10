class BaseLoader(object):
    def save_obj(self, obj):
        raise NotImplemented


class DeferLoader(BaseLoader):
    """
    Loader class that will defer to an object with the same primary key
    in the database.
    """
    def save_obj(self, obj):
        pk = obj.object.pk
        model = type(obj.object)
        try:
            model.objects.get(pk=pk)
        except model.DoesNotExist:
            obj.save()
        else:
            pass


class OverrideLoader(BaseLoader):
    """
    Loader class that overrides any data that exists in the database
    with the same fields.
    """
    def save_obj(self, obj):
        obj.save()
