from twilio.rest import Client
from core        import config

def send_sms(params):
    to      = params["to"  ]
    body    = params["body"]
    client  = Client(
        config.TWILIO_ACCOUNT_SID,
        config.TWILIO_AUTH_TOKEN
    )
    message = client.messages.create(
        to=to,
        from_=config.TWILIO_FROM,
        body=body
    )
    print "------------------------------------------"
    print message.sid
    print "------------------------------------------"
#end def

