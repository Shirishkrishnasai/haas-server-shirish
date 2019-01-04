import uuid
def find_list_in_dictionary(dicttasks, lst_dep_task_types):
        # Generic Function used to search a list of values in a dictionary. it returns keys for the found values as a list
        # Author:  Sreeram Nyshadham
    
        returnlist = []
        for dep_task_type in lst_dep_task_types:
            for key1, value1 in dicttasks.items():
                if dep_task_type == value1:
                    returnlist.append(key1)
        return returnlist
    
    
def find_dep_tasks(dict_tasktypes, dict_tasks):
        # Returns a dictionary of tasks with dependent tasks  for a given input of tasks dictionary and tasktype dictonary
        # Author: Sreeram Nyshadham
        # dict_tasktypes = {'a':[], 'b': [],  'c': ["a"], 'd': ["c","a"], 'e': ['b','c']}
        # dict_tasks = { '1': 'c', '2':'a','3':'e','4':'d','5':'b','6':'c','7':'a','8':'b','9':'a','10':'c'}
    
        dict_output = {}
        for key, value in dict_tasks.items():
            dict_output[key] = find_list_in_dictionary(dict_tasks, dict_tasktypes[value])
        return dict_output
    
    
def generate_tasks(dict_nodes, dict_tasktypes):
        # This function genrates returns a list of tasks with associated task types and server role. Example: [ [UUID1, tasktypeid, role], [UUID1, tasktypeid, role], [UUID1, tasktypeid, role] ]
        # Author: Sreeram Nyshadham
    
        # Agruments
        # nodes - A dictionary of nodes with roles. Example: nodes = {"1":"NN", "2":"DN", "3": "DN"}
        # tasktypeids - A dictionary of tasktypesids associated with a role. Example tasktypes= { "001": "NN", "002": "DN", "003": "NN", "004": "DN", "005": "DN" }
    
        lst_tasklist = []
        total_tasks_count = 0
    
        for node_id, node_role in dict_nodes.items():
            role_tasks_count = 0
            for takstype_id, tasktype_role in dict_tasktypes.items():
                if (node_role == tasktype_role):
                    role_tasks_count = role_tasks_count + 1
                    lst_tasklist.append([node_id, str(uuid.uuid1()), takstype_id, node_role])
    
            total_tasks_count = total_tasks_count + role_tasks_count
    
        return lst_tasklist
def identify_tasks_for_assignment(dict_tasks, lst_completed_tasks):
    # This function helps in identifying the tasks that can be assigned to an agent

    # Author : Sreeram

    # Arguments
    # lst_completed_tasks = ["2","5","7","1","3"] - It is a list of completed tasks

    # dict_tasks = {"1":[] , \ is a list of all tasks associated with a request
    # "2":[], \
    # "3":["2"], \
    # "4":["2"], \
    # "5":["2","1"], \
    # "6":["5"], \
    # "7":["2"], \
    # "8":["2", "7"], \
    # "9":["1","3"], \
    # "10":[], \
    # "11":["2","3","5","7"], \
    # "12":[], \
    # "13":[]}

    lst_assign_tasks = []
    tmp_assign_tasks = []
    set_assign_tasks = ()
    set_completed_tasks = set(lst_completed_tasks)

    for completedtask in lst_completed_tasks:
        del dict_tasks[completedtask]

    for task, dep_tasks in dict_tasks.items():
        if (set(dep_tasks).issubset(set_completed_tasks)):
            tmp_assign_tasks.append(task)

    set_assign_tasks = set(tmp_assign_tasks).difference(set_completed_tasks)
    lst_assign_tasks = list(set_assign_tasks)
    return lst_assign_tasks

def create_azure_share(str_azure_account_name, str_azure_account_key,str_share_name, int_share_quota=100):
    from azure.storage.file import FileService, FilePermissions

    file_service = FileService(account_name=str_azure_account_name, account_key=str_azure_account_key)
    bool_created = file_service.create_share(share_name=str_share_name, quota=int_share_quota)

    return bool_created

def azure_upload_host_slave(cluster_id):
    import io
    from application import app, db, mongo_conn_string, conn_string, session_factory
    from sqlalchemy.orm import scoped_session
    from application.models.models import TblVmCreation

    hostname_ip_details = db.session.query(TblVmCreation.var_ip,TblVmCreation.var_name,TblVmCreation.var_role).filter(TblVmCreation.uid_cluster_id == cluster_id).all()
    print hostname_ip_details,'hhhhhhhhhhhhhhhh'
    hostfile = open('hostfile','w')
    slavefile = open('slavefile', 'w')
    for tups in hostname_ip_details:
        print tups,'tuppppppppppppppp'
        hostfile.write(str(tups[0])+'   '+str(tups[1])+'\n')
        if str(tups[2]).lower() == 'datanode':
            slavefile.write(str(tups[0])+'   '+str(tups[1])+'\n')
    hostfile.close()
    slavefile.close()
    # byte_stream = io.BytesIO(utf_posted_file)
    # file_service = FileService(account_name=account_name, account_key=account_key)
    # file_service.create_file_from_stream(share_name=share_values[0],
    #                                      directory_name=share_values[1],
    #                                      file_name=filename,
    #                                      stream=byte_stream,
    #                                      count=no_of_bytes,
    #                                      progress_callback=fileProgress)

azure_upload_host_slave('c02c6724-0e89-11e9-bb3d-3ca9f49ab2cc')