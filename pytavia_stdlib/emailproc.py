import smtplib
import string
from   email.mime.multipart   import MIMEMultipart
from   email.mime.text        import MIMEText
from   email.mime.application import MIMEApplication

def send(params):
    to_email = params["to"     ]
    subject  = params["subject"]
    message  = params["html"   ]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['To'     ] = to_email
    msg['From'   ] = "noreply@lakuemas.com"

    html_email = MIMEText(message, 'html')
    msg.attach( html_email )

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login   ("noreply@lakuemas.com", "noreplylakuemas2018@)!*")
    server.sendmail("noreply@lakuemas.com", to_email , msg.as_string())
    server.quit()
# end def

def attach_send(params):
    to_email   = params["to"       ]
    subject    = params["subject"  ]
    filename   = params["filename" ]
    attachment = params["pdf"      ]
    message    = params["html"     ]

    pdfAttachment = MIMEApplication(attachment, _subtype = 'pdf')
    pdfAttachment.add_header('content-disposition', 'attachment',
        filename=(filename))

    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['To'     ] = to_email
    msg['From'   ] = "noreply@lakuemas.com"

    html_email    = MIMEText(message, 'html')
    msg.attach( html_email )
    msg.attach( pdfAttachment )

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login   ("noreply@lakuemas.com", "noreplylakuemas2018@)!*")
    server.sendmail("noreply@lakuemas.com", to_email , msg.as_string())
    server.quit()
# end def
