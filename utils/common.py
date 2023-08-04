import datetime
import os

from django.conf import settings
from uuid import uuid4

def upload_file_to_s3(instance, filename):
    """
    This function is used to upload files  to s3 bucket
    """
    year = datetime.date.today().year
    f_name, f_ext = os.path.splitext(filename)

    uuid = str(uuid4())[:4]
    return '{}/{}/{}_{}{}'.format(settings.AWS_STORAGE_BASE_FOLDER_NAME,
                             year,
                             f_name,
                             uuid,
                             f_ext
                             )