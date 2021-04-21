
from pytavia_core   import config
from pytavia_stdlib import wasabi_lib
from pytavia_stdlib import utils
from werkzeug.utils import secure_filename

WASABI = "wasabi"

class Uploader():
    def __init__(self, service):
        self.service = service
        # add other services here
    
    def upload(self, response, file, params={}):
        filename = secure_filename(file.filename)
        if self.service == WASABI:
            timestamp, timestamp_str = utils._get_current_timestamp("%Y-%m-%d")
            bucket = params["bucket"] if "bucket" in params else config.G_WSB_IMAGE_BUCKET
            folder = params["folder"] if "folder" in params else config.G_WSB_MAIN_FOLDER
            full_file_path = folder + timestamp_str + "/" + str(timestamp) + "-" + filename
            file_response = wasabi_lib.store_file({
                "bucket"     : bucket,
                "file_data"  : file,
                "file_name"  : full_file_path
            })

            if file_response["message_action"] != "ADD_WASABI_FILE_SUCCESS":
                response.put("status"       , "ADD_WASABI_FILE_FAILED"                      )
                response.put("desc"         , file_response["message_desc"]                 )
                response.put("status_code"  , config.G_STATUS["WASABI_UPLOAD_ERROR"]['CODE'])
                return None
            
            wasabi_url = config.G_WSB_URL if config.G_WSB_URL.endswith("/") else config.G_WSB_URL + '/'
            file_url = wasabi_url + bucket + '/' + full_file_path

            return file_url