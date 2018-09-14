from core import config
from core import templating

"""
    This will send a push notification via SNS to the mobile
        device defined in the arn
"""
def send(arn, message):
    region     = [r for r in boto.sns.regions() if r.name==config.G_SNS_REGION][0]
    sns_handle = boto.sns.SNSConnection(
        aws_access_key_id     = config.G_SNS_KEY,
        aws_secret_access_key = config.G_SNS_ACCESS,
        region                = region
    )
    gcm_string = """
        {"data":{
            "message": "$message" ,
            "title"  : "$title"   ,
            "status" : "$status"  ,
            "action" : "$action"  ,
            "data"   : {}
            }
        }
    """
    apns_string = """
        {"aps":{
            "alert"  : "<message>",
            }
        }
    """
    adm_string = """
        {"data":{
            "message": "<message>",
            }
        }
    """
    adm_json = templating.Templating().render(
        adm_string  , {}
    )
    apns_json = templating.Templating().render(
        apns_string , {}
    )
    gcm_json  = templating.Templating().render(
        gcm_string  , message
    )
    json_data  = {
        "APNS": apns_json, "GCM" : gcm_json , "ADM" : adm_json
    }
    # if we get an error here in the push because the end point is not enabled
    # we need to enable it here
    publish_result = sns_handle.publish(
        target_arn=arn, message=json.dumps(json_data), message_structure='json'
    )
#end def
