import json
import urllib
import urllib2
import ssl
import requests


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
        print call_url
        print data
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
    http_method = params["method" ]
    scheme      = params["scheme" ]
    host        = params["host"   ]
    route       = params["route"  ]
    data        = params["param"  ]
    headers     = params["headers"]
    req_message = requests.post(
        scheme + "://" + host + route,
        data=data,
        headers=headers
    )
    print req_message.status_code
    print req_message.text
    return req_message
# end def

