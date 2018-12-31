from flask import Flask,jsonify,request,Blueprint
from application.models.models import TblUsers
from sqlalchemy.orm import scoped_session
from application import session_factory

metaclusterist=Blueprint('',__name__)

@metaclusterist.route("/users/<customer_id>", methods=['GET'])