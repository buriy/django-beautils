from django.core import mail

class BogusSMTPConnection(object):
    _console = True
    """Instead of sending emails, print them to the console."""

    def __init__(*args, **kwargs):
        print "Initialized bogus SMTP connection"

    def open(self):
        print "Open bogus SMTP connection"

    def close(self):
        print "Clone bogus SMTP connection"

    def send_messages(self, messages):
        print "Sending through bogus SMTP connection:"
        for message in messages:
            print "From: %s" % message.from_email
            print "To: %s" % (", ".join(message.to))
            print "Subject: %s\n\n" % message.subject
            print "%s" % message.body
            print messages
        return len(messages)

if mail.SMTPConnection.__name__ != 'BogusSMTPConnection':
    mail.SMTPConnection = BogusSMTPConnection
    print "Console emails were activated"
