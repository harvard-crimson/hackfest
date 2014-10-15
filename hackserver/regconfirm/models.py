import uuid

from django.db import models

class Registrant(models.Model):
    name = models.CharField(max_length=50, blank=True, null=False, default='')
    email = models.CharField(max_length=100, blank=False, null=False, default='',
                             db_index=True, unique=True)

    # for confirmation
    confirmed = models.BooleanField(null=False, default=False)
    secret = models.CharField(max_length=32, null=False, default='')

    def confirm(self, given_secret):
        if given_secret == self.secret:
            if not self.confirmed:
                self.confirmed = True
                self.save()
            return True
        else:
            return False

    def __unicode__(self):
        return unicode("%s: <%s>" % (self.name, self.email))

    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = uuid.uuid4().hex

        super(Registrant, self).save(*args, **kwargs)
