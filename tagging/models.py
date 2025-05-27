from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ProfileA(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()


class ProfileB(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

class ProfileBExtra(models.Model):
    info = models.TextField()
    profile_b = models.OneToOneField(ProfileB, on_delete=models.CASCADE, related_name='extra_data')

class ProfileC(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()

class ProfileD(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

class TagGFK(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

class TagExplicit(models.Model):
    profile_a = models.ForeignKey(ProfileA, null=True, blank=True, on_delete=models.CASCADE)
    profile_b = models.ForeignKey(ProfileB, null=True, blank=True, on_delete=models.CASCADE)
    profile_c = models.ForeignKey(ProfileC, null=True, blank=True, on_delete=models.CASCADE)
    profile_d = models.ForeignKey(ProfileD, null=True, blank=True, on_delete=models.CASCADE)
