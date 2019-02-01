from flask import Flask, jsonify, request, Blueprint
from application.models.models import TblUsers
from sqlalchemy.orm import scoped_session
from application import session_factory

customerusers = Blueprint('users', __name__)


@customerusers.route("/users/<customer_id>", methods=['GET'])
def users(customer_id):
    session = scoped_session(session_factory)
    customer_users = session.query(TblUsers.var_user_name, TblUsers.bool_active, TblUsers.uid_customer_id).filter(
        TblUsers.uid_customer_id == customer_id).all()
    users_list = []
    for users in customer_users:
        users_list.append({"user_name": users[0], "bool_active": users[1], "customer_id": users[2]})
    session.close()
    return jsonify(user_data=users_list)
