from azure.storage.file import FileService,FilePermissions
from application.models.models import TblFileUpload,TblFileDownload
from sqlalchemy.orm import scoped_session
from application import session_factory
from configparser import ConfigParser
from application.common.loggerfile import my_logger

def bigsizefiledownload(uploadid):
    cfg = ConfigParser()
    cfg.read('application/config/azure_config.ini')
    account_name = cfg.get('file_storage', 'account_name')
    account_key = cfg.get('file_storage', 'key')
    print account_name
    print account_key
    file_service = FileService(account_name=account_name, account_key=account_key)
    db_session = scoped_session(session_factory)
    file_values = db_session.query(TblFileUpload.var_share_name,
                                   TblFileUpload.var_directory_name,
                                       TblFileUpload.var_file_name).filter(TblFileUpload.uid_upload_id == uploadid).first()
    startrange = 0
    endrange=0
    print file_values[0]
    print file_values[1]
    print file_values[2]
    while startrange<=55000:
        startrange=startrange+1000
        filedownloaded=file_service.get_file_to_bytes(share_name=file_values[0], directory_name=file_values[1], file_name=file_values[2], start_range=startrange, end_range=endrange, validate_content=False, progress_callback=None, max_connections=2, timeout=None)
        endrange=startrange
       # print filedownloaded.content
#def fileProgress(start, size):
 #   my_logger.debug("%d%d", start, size)