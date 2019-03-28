from django.test import TestCase

from ..senders import get_sender, SentrySender


class GetSenderTest(TestCase):

    def test_default_sender(self):
        sender = get_sender()
        self.assertIsInstance(sender, SentrySender)
