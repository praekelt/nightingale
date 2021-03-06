from django.contrib.postgres.fields import HStoreField
from django.db import models
from accounts.models import Integration
from reports.models import Report
from django.db.models.signals import post_save
from django.dispatch import receiver


class Submission(models.Model):

    integration = models.ForeignKey(Integration,
                                    related_name='submissions',
                                    null=False)
    report = models.ForeignKey(Report,
                               related_name='submissions',
                               null=True)
    content = models.TextField(null=False, blank=False)
    metadata = HStoreField(null=True, blank=True, default={})
    created_at = models.DateTimeField(auto_now_add=True)
    submitted = models.BooleanField(default=False)

    def __str__(self):
        return self.content


# send new submissions
@receiver(post_save, sender=Submission,
          dispatch_uid="ona.post_save.submission")
def fire_subm_action_if_undelivered(sender, instance, created, **kwargs):
    from .tasks import send_submission
    if not instance.submitted:
        send_submission.delay(instance.id)
