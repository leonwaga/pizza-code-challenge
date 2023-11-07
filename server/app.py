from flask import Flask, jsonify, request, make_response
from flask_migrate import migrate
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound

from models import db, Pizza, Restaurant, RestaurantPizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Home(Resource):
    def get(self):
        response_message = {
            "message": "WELCOME TO THE PIZZA RESTAURANT API."
        }
        return make_response(response_message, 200)
    
api.add_resource(Home, '/')

class Pizzas(Resource):
    def get(self):
        pizzas = []
        for pizza in Pizza.query.all():
            pizza_dict={
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            }
            pizzas.append(pizza_dict)
        return make_response(jsonify(Pizzas), 200)
    
api.add_resource(Pizzas, '/pizzas')

class Restaurants(Resource):
    def get(self):
        restaurants = []
        for restaurant in Restaurant.query.all():
            restaurant_dict={
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
            restaurant.append(restaurant)
        return make_response(jsonify(restaurants), 200)
    
api.add_resource(Restaurants, '/restaurants')

class RestaurantById(Resource):

    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            restaurant_dict ={
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "pizzas":[
                    {
                        "id": restaurant.pizza.id,
                        "name": restaurant.pizza.name,
                        "ingredient": restaurant.pizza.ingredients
                    }
                    for restaurant_pizza in restaurant.pizzas
                ]
            }
            return make_response(jsonify(restaurant_dict), 200)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        

    def delete(self,id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        
api.add_resource(RestaurantById, '/restaurants/<int:id>')

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        if not all(key in data for key in ("price", "pizza_id", "restaurant_id")):
            return make_response(jsonify({"errors": ["validation errors.include all keys"]}), 400)
        
        price = data["price"]
        pizza_id = data["pizza_id"]
        restaurant_id = data["restaurant_id"]

        pizza = pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            return make_response(jsonify({"errors": ["validation errors pizza and restaurant dont exist"]}), 400)

        restaurant_pizza = RestaurantPizza(
            price = data["price"],
            pizza_id = data["pizza_id"],
            restaurant_id = data["restaurant_id"]
        )
        
        db.session.add(restaurant_pizza)
        db.session.commit()

        pizza_data = {
        "id": pizza.id,
        "name": pizza.name,
        "ingredient": pizza.ingredients
        }

        return make_response(jsonify(pizza_data), 201)
    
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

@app.errorhandler(NotFound)

def handle_not_found(e):
    response = make_response(
        "Not Found: The requested resource does not exist!",
        404
    )
    return response
if __name__ == "__main__":
    app.run(port=5555, debug=True)