from django.conf import settings

import sentry_sdk
# from celery import signature


class BaseSender(object):
    name = None
    client = None

    def send(self, message, extra, tags, sentry_data, crash_obj=None):
        pass


class SentrySender(BaseSender):
    name = "Sentry"

    def __init__(self):
        self.client = sentry_sdk.init()

    def send(self, message, extra, tags, sentry_data, crash_obj=None):
        self.client.capture_event(
            message,
            {
                'extra': extra,
                'tags': tags,
                'data': sentry_data,
                'level': 'error'
            }
        )
        # signature("tasks.get_sentry_link", args=(crash_obj.pk, event_id)).apply_async(queue='private', countdown=1)


senders_dict = {
    "Sentry": SentrySender,
}


def get_sender(tracker_name=None):
    if not tracker_name:
        tracker_name = getattr(settings, 'CRASH_TRACKER', 'Sentry')
    try:
        sender_class = senders_dict[tracker_name]
    except KeyError:
        raise KeyError("Unknown tracker, use one of %s" % senders_dict.keys())
    return sender_class()
