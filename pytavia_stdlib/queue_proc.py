import boto
import boto.exception
import boto.sqs
import boto.sqs.connection
import re
import json


from boto.sqs.message import Message

from core import config
from core import templating

def conn():
    region = [r for r in boto.sqs.regions() if r.name==config.G_SQS_REGION][0]
    q_conn_handle = boto.sqs.connection.SQSConnection(
        aws_access_key_id=config.G_SQS_KEY,
        aws_secret_access_key=config.G_SQS_ACCESS,
        region=region
    )
    return q_conn_handle
#end def


def read(params):
    msg_wrapper = {
        "message_action" : "READ_Q_SUCCESS",
        "message_data"   : {}
    }
    try:
        queue_name    = params["queue_name"]
        q_conn_handle = conn()
        pay_trans_q   = q_conn_handle.get_queue(queue_name)
        msg_set       = pay_trans_q.get_messages(visibility_timeout=10)
        if len( msg_set ) > 0:
            message_data  = msg_set[0]
            msg_body      = message_data.get_body()
            msg_wrapper["message_data"] = {
                "msg_body" : msg_body,
                "msg_raw"  : message_data
            }
            return msg_wrapper
        #end if
        msg_wrapper["message_action"] = "READ_Q_FAILED"
    except Exception, e:
        msg_wrapper["message_action"] = "READ_Q_FAILED"
    #end try
    return msg_wrapper
#end def

def delete(params):
    queue_name    = params["queue_name"]
    message_rs    = params["message_rs"]
    q_conn_handle = conn()
    pay_trans_q   = q_conn_handle.get_queue(queue_name)
    pay_trans_q.delete_message(message_rs)
#end def

"""
    This will write to the required queue
"""
def write(params):

    queue_name     = params["queue_name"]
    queue_data     = params["data"      ]

    q_conn_handle  = conn()
    pay_trans_q    = q_conn_handle.get_queue(queue_name)
    q_message      = Message()
    queue_data_str = json.dumps( queue_data )
    q_message.set_body( queue_data_str )
    pay_trans_q.write ( q_message  )
#end def

