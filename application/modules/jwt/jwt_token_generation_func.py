import jwt

from application import app

def jwtTokenGeneration(customerid):
    #try:

        app.config['SECRET_KEY'] = 'kwartile'
        token_dict = {}
        token_dict['customer_id'] = customerid
        jwt_token_generated = jwt.encode(token_dict, app.config['SECRET_KEY'])
        return jwt_token_generated
