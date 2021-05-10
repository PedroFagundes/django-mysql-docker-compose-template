from django.core.mail import send_mail as _send_mail


class Mail(object):
    '''
    Email Mediator Class
    '''

    def send_email(subject, recipient_list, message=None,
                   from_email="team@helloteam.io",
                   fail_silently=False, auth_user=None, auth_password=None,
                   connection=None, html_message=None):
        _send_mail(subject, message, from_email, recipient_list,
                   fail_silently, auth_user, auth_password,
                   connection, html_message)
