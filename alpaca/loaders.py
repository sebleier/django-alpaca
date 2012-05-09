class BaseLoader(object):
    def save_obj(self, obj):
        raise NotImplemented


class PoliteLoader(BaseLoader):
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
    def save_obj(self, obj):
        obj.save()
