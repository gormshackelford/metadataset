from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import python_2_unicode_compatible

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.profile.email_is_confirmed)
        )

account_activation_token = AccountActivationTokenGenerator()
