import json
import urllib
import ssl
import requests
import sys

def call_wms(params):

    print( "-----------------------" , file=sys.stderr)
    print( params , file=sys.stderr)
    print( "-----------------------" , file=sys.stderr)

    route           = params["route"]
    params          = params["param"]
    host            = "wms-lb-v1"
    scheme          = "http://"

    params["token"    ] = "5f28b739bd6a225ea84dcdf8a36db8efd6966fb75b5cd0e6197932bc94d418d7"
    params["h2h_label"] = "DEALOKA"
    params["dlk_code" ] = "DLK_123456_ID"

    uri_string      = urllib.parse.urlencode(params)
    call_url        = host + "/" + route + "?" + uri_string

    call_url_final  = scheme + call_url
    print( "-----------------------" , file=sys.stderr)
    print( call_url_final , file=sys.stderr)
    print( "-----------------------" , file=sys.stderr)

    response        = urllib.request.urlopen( call_url_final )
    response_string = response.read()
    json_resp       = json.loads( response_string )
    return json_resp
#end def

def call(params):
    scheme          = params["scheme"]
    host            = params["host"  ]
    route           = params["route" ]
    params          = params["param" ]

    uri_string      = urllib.urlencode(params)
    call_url        = host + "/" + route + "?" + uri_string
    response        = urllib2.urlopen( scheme + "://" + call_url )
    response_string = response.read()
    json_resp       = json.loads( response_string )
    return json_resp
#end def

def call_rmt(params):
    http_method      = params["method"]
    scheme           = params["scheme"]
    host             = params["host"  ]
    route            = params["route" ]
    data             = params["param" ]
    request_obj = None
    if http_method == "POST":
        call_url        = scheme + "://" + host + route
        request_obj     = urllib2.Request(
                call_url, data=json.dumps(data)
        )
        if params.has_key("headers"):
            header_param = params["headers"]
            for key,value in header_param.iteritems():
                request_obj.add_header( key , value)
            # end for
        # end if
        response        = urllib2.urlopen( request_obj )
        response_string = response.read()
        json_resp       = json.loads( response_string )
        return json_resp
    elif http_method == "GET":
        call_url     = ""
        request_obj  = None
        if data == "":
            call_url    = scheme + "://" + host + route
            request_obj = urllib2.Request( call_url )
            if params.has_key("headers"):
                header_param = params["headers"]
                for key,value in header_param.iteritems():
                    request_obj.add_header( key , value)
                # end for
            # end if
        else:
            uri_string  = urllib.urlencode(data)
            call_url = scheme + "://" + host + route + "?" + uri_string
            request_obj = urllib2.Request( call_url )
            if params.has_key("headers"):
                header_param = params["headers"]
                for key,value in header_param.iteritems():
                    request_obj.add_header( key , value)
                # end for
            # end if
        # end if
        response        = urllib2.urlopen( request_obj )
        response_string = response.read()
        json_resp       = json.loads( response_string )
        return json_resp
    # end if
    return json_resp
#end def

def call_req(params):
    scheme      = params["scheme" ]
    host        = params["host"   ]
    route       = params["route"  ]
    data        = params["param"  ]
    req_message = requests.post(
        scheme + "://" + host + route,
        data=data
    )
    resp_json = json.loads(req_message.text)
    return resp_json
# end def

