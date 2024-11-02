# sportpropa/backends.py
from django.core.mail.backends.smtp import EmailBackend
import ssl

class CustomEmailBackend(EmailBackend):
    def _get_ssl_context(self):
        context = super()._get_ssl_context()
        context.check_hostname = False  # Disable hostname verification
        return context
