import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail
from app.core.config import configurations

sg = sendgrid.SendGridAPIClient(api_key=configurations.SENDGRID_API_KEY)


def send_grid_mail_send(subject, to_email, content, mime_type="plain"):
    # mime_types: "text/plain" or "text/html" or "text/x-amp-html"
    to_email = To(to_email)
    from_email = Email(configurations.MAIL_FROM)
    content = Content(f"text/{mime_type}", content)
    mail = Mail(from_email, to_email, subject, content)

    response = sg.client.mail.send.post(request_body=mail.get())
    if int(response.status_code) != 202:
        raise Exception("send_grid_mail_send failed to send email")
