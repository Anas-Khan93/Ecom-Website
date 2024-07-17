import datetime
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text


class ExpiringPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    
    def make_token(self,user):
        #Add timestamp
        timestamp = int((datetime.datetime.now() + datetime.timedelta(minutes=10)).timestamp())
        return super().make_token(user) + urlsafe_base64_encode(force_bytes(timestamp))