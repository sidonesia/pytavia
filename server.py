import json
import time
import pymongo
import sys
import urllib.parse
import base64

sys.path.append("pytavia_core"    ) 
sys.path.append("pytavia_settings") 
sys.path.append("pytavia_stdlib"  ) 
sys.path.append("pytavia_storage" ) 
sys.path.append("pytavia_modules" ) 

# adding comments
from pytavia_stdlib  import utils
from pytavia_core    import database 
from pytavia_core    import config 
from pytavia_stdlib  import idgen 


##########################################################

from flask import request
from flask import render_template
from flask import Flask
from flask import session
from flask import make_response
from flask import redirect
from flask import url_for
from flask import flash


from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import CSRFError
#
# Main app configurations
#
app             = Flask( __name__, config.G_STATIC_URL_PATH )
app.secret_key  = config.G_FLASK_SECRET

########################## CALLBACK API ###################################

@app.route("/v1/api/api-v1", methods=["GET"])
def register():
    fk_user_id   = request.args.get("fk_user_id"  )
    params       = {
        "fk_user_id" : fk_user_id
    }
    response = module1.module1(app).process( params )
    return response.stringify_v1()
# end def
