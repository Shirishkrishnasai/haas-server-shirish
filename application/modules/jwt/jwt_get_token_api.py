from flask import jsonify,Blueprint
import datetime,pytz
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblJwtToken
from application.modules.jwt.jwt_token_generation_func import jwtTokenGeneration

jwtapi = Blueprint('jwtapi', __name__)
@jwtapi.route("/jwtapi/token/<customerid>", methods=['GET'])

def getJwtToken(customerid):
    #try:
        jwt_session = scoped_session(session_factory)
        token_data = jwt_session.query(TblJwtToken.txt_token,
                                       TblJwtToken.ts_valid_datetime).first()
        print token_data,'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj'


        utc = pytz.UTC
        datetime_start = datetime.datetime.now()

        start_time = datetime_start.replace(tzinfo=utc)
        print start_time,'111111111111111111111111111111111111'
        ending_time = token_data[1].replace(tzinfo=utc)
        print ending_time,'22222222222222222222222222222222222222222'
        #if token_data != None and token_data[1] <= datetime.datetime.now() :
        if token_data != None and start_time<=ending_time:

            return jsonify(token_value = str(token_data[0]),message="laters baby")

        elif token_data == None:
            first_token = jwtTokenGeneration(customerid)
            token_expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
            adding_to_db = TblJwtToken(txt_token=first_token,
                                       ts_valid_datetime=token_expiry_time,
                                       ts_created_datetime=datetime.datetime.now(),
                                       uid_customer_id=customerid)
            jwt_session.add(adding_to_db)
            jwt_session.commit()
            return jsonify(token_value = first_token,message="bae")


        else:
            #call a function that generates token
            returned_token_value = jwtTokenGeneration(customerid)
            token_expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
            token_update_statement = jwt_session.query(TblJwtToken.txt_token,
                                                       TblJwtToken.ts_valid_datetime,
                                                       TblJwtToken.ts_created_datetime,
                                                       TblJwtToken.uid_customer_id)

            token_update_statement.update({"txt_token":returned_token_value,
                                           "ts_valid_datetime": token_expiry_time,
                                           "ts_created_datetime" : datetime.datetime.now(),
                                           "uid_customer_id" : customerid})
            jwt_session.commit()
            return jsonify(token_value = returned_token_value,message = "expiry soon for ya")

