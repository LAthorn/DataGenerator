from django.db import models
from django.contrib.auth.models import AbstractBaseUser


# Create your models here.


class SelfValidatingModel(models.Model):
    """
    This base ensures all saved objects are validated.
    Django does not do this by default!
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Organisation(SelfValidatingModel):
    """An Organisation"""

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # if user deleted this will keep the related field information
    created_by = models.ForeignKey(
        "User",
        on_delete=models.DO_NOTHING,
        related_name="organisation_created_by",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        "User",
        on_delete=models.DO_NOTHING,
        related_name="organisation_updated_by",
    )
    has_consented = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class User(AbstractBaseUser):
    """A User"""

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    created_by = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "username", "display_name"]

    def __str__(self):
        return self.name

    # User is not a SelfValidatingModel so need to override save to call
    # validate (i.e. full_clean)
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Domain(SelfValidatingModel):
    domain = models.CharField(max_length=255)
    # if organisation deleted this will delete it's domains
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)

    def __str__(self):
        return self.domain
