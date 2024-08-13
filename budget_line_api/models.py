from django.db import models

# Create your models here.

import uuid


class BaseUUIDModel(models.Model):
    """
    Base UUID model that represents a unique identifier for a given model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True, editable=False)
    
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def readByToken(cls, token: str, is_change=False):
        """ take an object by token """
        if is_change is False:
            return cls.objects.get(id=token)
        return cls.objects.select_for_update().get(id=token)