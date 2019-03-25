from flask import  jsonify,  Blueprint
from application.models.models import TblUsers
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.common.loggerfile import my_logger
import os,sys

customerusers = Blueprint('users', __name__)
@customerusers.route("/users/<customer_id>", methods=['GET'])
def users(customer_id):
    try:
        session = scoped_session(session_factory)
        customer_users = session.query(TblUsers.var_user_name, TblUsers.bool_active, TblUsers.uid_customer_id).filter(
            TblUsers.uid_customer_id == customer_id).all()
        users_list = []
        for users in customer_users:
            users_list.append({"user_name": users[0], "bool_active": users[1], "customer_id": users[2]})
        return jsonify(user_data=users_list)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        session.close()