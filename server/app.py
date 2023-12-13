#!/usr/bin/env python3

from models import db, Hotel, HotelCustomer, Customer
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

api = Api(app)

class AllHotels(Resource):
    
    def get(self):
        hS = Hotel.query.all()
        rb = [h.to_dict(rules=('-hotel_customers',)) for h in hS]
        return make_response(rb, 200)
    
class HotelById(Resource):
    
    def get(self, id):
        h = Hotel.query.filter(Hotel.id == id).first()
        if h:
            
            rb = h.to_dict(rules=('-hotel_customers.hotel','-hotel_customers.customer.hotel_customers'))
            return make_response(rb, 200)    
        else:
            rb = {
                "error": "Hotel not found"
            }
            return make_response(rb, 404)
        
    def delete(self, id):
        h = Hotel.query.filter(Hotel.id == id).first() 
        if h:
            db.session.delete(h)
            db.session.commit()
            return make_response({}, 204)
        else:
            rb = {
                "error": "Hotel not found"
            }
            return make_response(rb, 404)
class AllCustomers(Resource):
     def get(self):
        hS = Customer.query.all()
        rb = [h.to_dict(rules=('-hotel_customers',)) for h in hS]
        return make_response(rb, 200)

class CreateHotelCustomer(Resource):
    def post(self):
        try:
            new_hc = HotelCustomer(
                rating = request.json.get('rating'),
                hotel_id = request.json.get('hotel_id'),
                customer_id = request.json.get('customer_id')
            )
            db.session.add(new_hc)
            db.session.commit()
            rb = new_hc.to_dict(rules=('-hotel.hotel_customers', '-customer.hotel_customers'))
            return make_response(rb, 201)
        except ValueError:
            rb = {
                "errors": ["validation errors"]
            }
            return make_response(rb, 400)
                
api.add_resource(AllHotels, '/hotels')        
api.add_resource(HotelById, '/hotels/<int:id>')
api.add_resource(AllCustomers, '/customers')
api.add_resource(CreateHotelCustomer, '/hotel_customers')   
@app.route('/')
def index():
    return '<h1>Mock Code challenge</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)
