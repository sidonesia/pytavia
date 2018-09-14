import boto
import json

from pytavia_core import config

class s3aws:

    _g_s3_region_baseurl = config.G_AWS_BASE_URL
    _g_s3_region         = config.G_AWS_REGION # us-east-1

    def __init__(self):
        pass

    """
        Set the region for the file so this is like SG or US etc
    """
    def _set_region(self, params):
        # https://s3.amazonaws.com,https://s3-sg.amazonaws.com
        # us-east-1
        self._g_s3_region_baseurl = params["region_baseurl"]
        self._g_s3_region         = params["region_string" ]

    """
        Save the file by giving the data , file type and setting the permissions
            Also set the path for the file within s3
    """
    def _save(self, params):
        data         = params["data"     ] # this is the bianry content of the file
        content_type = params["type"     ] # this is the content type like image/jpg
        bucket_name  = params["bucket"   ] # this is the bucket name
        file_path    = params["file_path"] # this is the file path we want to save it into
        s3Conn       = boto.s3.connect_to_region(
                self._g_s3_region,
                aws_access_key_id=config.G_AWS_KEY    ,
                aws_secret_access_key=config.G_AWS_SECRET ,
                is_secure=True
        )
        bucket           = s3Conn.get_bucket( bucket_name )
        key              = boto.s3.key.Key(bucket, file_path)
        key.content_type = content_type
        key.set_contents_from_file(data, policy='public-read')
        image_path       = self._g_s3_region_baseurl + "/" + bucket_name + "/" + file_path
        return image_path

