from azure.storage.file import FileService

from configparser import ConfigParser
from msrestazure.azure_exceptions import CloudError

def fileProgress(start,size):
        print start,size
def fileUpload():
        try:

            cfg = ConfigParser()
            cfg.read('application/config/azure_config.ini')

            account_name=cfg.get('file_storage','account_name')
            account_key = cfg.get('file_storage','key')
            print account_key,account_name
            file_service = FileService(account_name=account_name, account_key=account_key)
            print 'file account ok'
            #file_service.create_share('haasfiles')
            print 'file service share ok'
            #file_service.create_directory('haasfiles', 'sampledir')

            print 'file directory ok'
            try:
                file_service.create_file_from_path(share_name='haasfiles',
                                                   directory_name='sampledir',
                                                   file_name='agent_configfile100.py',
                                                   local_file_path='/home/sbv4/Documents/charm.log',progress_callback=fileProgress)

            except Exception as e:
                print e


                access_signature=file_service.generate_file_shared_access_signature(share_name='haasfiles',
                                                                                    directory_name='sampledir',
                                                                                    file_name='agent_configfile100.py',
                                                                                    permission='read',
                                                                                    expiry='2018-10-29 03:00:00')

                print access_signature



                return "SS"

        except CloudError as e:
            print(e.__str__())
        except Exception as e:

            print e.__str__()
        finally:
            print "Geot "


