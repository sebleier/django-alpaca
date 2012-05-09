class BaseRemover(object):
    def remove_obj(self, obj):
        raise NotImplemented


class NullRemover(BaseRemover):
    def remove_obj(self, obj):
        pass


class NormalRemover(BaseRemover):
    def remove_obj(self, obj):
        pk = obj.object.pk
        model = type(obj.object)
        try:
            model.objects.get(pk=pk).delete()
        except model.DoesNotExist:
            pass
