import json
import time
import pymongo
import sys

sys.path.append("pytavia_core"    ) 
sys.path.append("pytavia_settings") 
sys.path.append("pytavia_stdlib"  ) 
sys.path.append("pytavia_storage" ) 
sys.path.append("pytavia_modules" ) 
sys.path.append("pytavia_modules/module1"  ) 
sys.path.append("pytavia_modules/module2"  ) 

# adding comments

from pytavia_core    import database 
from pytavia_core    import config 
from pytavia_stdlib  import idgen 

# from module1       import module1_proc 
# from module2       import module2_proc


from flask import request
from flask import render_template
from flask import Flask
from flask import session
from flask import make_response
from flask import redirect
from flask import url_for

from flask_wtf.csrf import CSRFProtect

#
# Main app configurations
#
app            = Flask( __name__, config.G_STATIC_URL_PATH )
app.secret_key = config.G_FLASK_SECRET
csrf           = CSRFProtect(app)

#
# All public urls below
#
@app.route("/user/login")
def login():
    params = request.form.to_dict()
    html   = module1_proc.module1_proc().html( params )
    return html
# end def


##################################################################################

@app.route("/auth/login", methods=["POST"])
def auth_login():
    params   = request.form.to_dict()
    response = module1.module1(app).login( params )
    m_action = response["message_action"]
    if m_action == "LOGIN_SUCCESS":
        return redirect("/console/dashboard")
    else:
        return redirect("/error/page")
    # end if
# end def


