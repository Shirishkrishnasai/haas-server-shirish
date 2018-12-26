from flask import Blueprint,jsonify
from application.models.models import TblCustomerJobRequest,TblMetaMrRequestStatus
from sqlalchemy.orm import scoped_session
from application import session_factory

mrjobstatus=Blueprint('mrjobstatus',__name__)
@mrjobstatus.route("/clusterlocation/cloudtype",methods=['GET'])
def mrJobStatus():
    session = scoped_session(session_factory)
