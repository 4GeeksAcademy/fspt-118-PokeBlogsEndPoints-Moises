"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Pokemon,Item,Favorites
from sqlalchemy import select
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)





#------User--------
@app.route('/user', methods=['GET'])
def get_all_user():
    try:
        query=select(User)
        data=db.session.execute(query).scalars().all()

        if not data:
            return jsonify({'success':False, 'data':'No users'}),200
        data= [u.serialize() for u in data]

        return jsonify({'success': True, 'data':data}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})
    

@app.route('/user/<int:id>', methods=['GET'])
def get_one_user(id):
    try:
       
        data= db.session.get(User,id)

        if not data:
            return jsonify({'success':False, 'data':'No users found'}),200

        return jsonify({'success': True, 'data':data.serialize()}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})
    

@app.route('/user', methods=['POST'])
def create_user():
    try:
        body = request.json

        if body['username'] is '' or body['password'] is '':
            return jsonify({'success':False, 'data':'username and password are required'})
        
        if len(body['username'])< 3 or len(body['password'])< 5:
            return jsonify({'success':False, 'data':'username and/or password do not meet the requirements'})
        
        query = select(User).where(User.username == body['username'])
        existing_user = db.session.execute(query)
        if existing_user:
            return jsonify({'success':False, 'data':'User already exist'})



        new_user= User(
            username = body['username'],
            password=body['password'],
            is_active = True
        )
        db.session.add(new_user)
        db.session.commit()
    
        return jsonify({'success': True, 'data':new_user.serialize()}),200
    except Exception as error:
        db.session.rollback()
        return jsonify({'success': False, 'error':error})



@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        body = request.json

        user = db.session.get(User,id)
        if not user:
            return jsonify({'success':False, 'data':'User not Found'})
        
        user.username = body.get('username') or user.username
        user.password = body.get('password') or user.password
        user.is_active = body.get('is_active') or user.is_active
        user.role = body.get('role') or user.role

     
        db.session.commit()
    
        return jsonify({'success': True, 'data':user.serialize()}),200
    except Exception as error:
        db.session.rollback()
        return jsonify({'success': False, 'error':error})
    

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
       
        user= db.session.get(User,id)

        if user is None:
            return jsonify({'success':False, 'user':'No users'}),200
        
        db.session.delete(user)
        db.session.commit()

        return jsonify({'success': True, 'data':'user delete'}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})


#---------Pokemon----------------------


@app.route('/pokemon', methods=['GET'])
def get_all_pokemon():
    try:
        query=select(Pokemon)
        data=db.session.execute(query).scalars().all()

        if not data:
            return jsonify({'success':False, 'data':'No pokemon'}),200
        data= [p.serialize() for p in data]

        return jsonify({'success': True, 'data':data}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})
    

@app.route('/pokemon/<string:name>', methods=['GET'])
def get_one_pokemon_by_name(name):
    try:
        query=select(Pokemon).where(Pokemon.name == name)
        pokemon=db.session.execute(query).scalars().all()
        pokemon=[p.serialize() for p in pokemon]

        if not pokemon:
            return jsonify({'success': False, 'data': 'No pokemon found'}), 200

        return jsonify({'success': True, 'data': pokemon}), 200
    except Exception as error:
        return jsonify({'success': False, 'error':error}), 500
    

@app.route('/pokemon/<int:id>', methods=['GET'])
def get_one_pokemon(id):
    try:
       
        pokemon= db.session.get(Pokemon,id)

        if not pokemon:
            return jsonify({'success':False, 'data':'No pokemon found'}),200

        return jsonify({'success': True, 'data':pokemon.serialize()}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})



@app.route('/pokemon', methods=['POST'])
def create_pokemon():
    try:
        body = request.json

        if body['name'] is '' or body['type'] is '':
            return jsonify({'success':False, 'data':'name and type are required'})
        
        if len(body['name'])< 1 or len(body['type'])< 1:
            return jsonify({'success':False, 'data':'name and/or type do not meet the requirements'})

        new_pokemon= Pokemon(
            name = body['name'],
            type=body['type'],
            user_id=body['user_id']
        )
        db.session.add(new_pokemon)
        db.session.commit()
    
        return jsonify({'success': True, 'data':new_pokemon.serialize()}),200
    except Exception as error:
        db.session.rollback()
        return jsonify({'success': False, 'error':error})
    


@app.route('/pokemon/<int:id>', methods=['PUT'])
def update_pokemon(id):
    try:
        body = request.json

        pokemon = db.session.get(Pokemon,id)
        if not pokemon:
            return jsonify({'success':False, 'data':'pokemon not Found'})
        
        pokemon.name = body.get('name') or pokemon.name
        pokemon.type = body.get('type') or pokemon.type
        

     
        db.session.commit()
    
        return jsonify({'success': True, 'data':pokemon.serialize()}),200
    except Exception as error:
        db.session.rollback()
        return jsonify({'success': False, 'error':error})
    

@app.route('/pokemon/<int:id>', methods=['DELETE'])
def delete_pokemon(id):
    try:
       
        pokemon= db.session.get(Pokemon,id)

        if not pokemon:
            return jsonify({'success':False, 'user':'No pokemon found'}),200
        
        db.session.delete(pokemon)
        db.session.commit()

        return jsonify({'success': True, 'data':'pokemon delete'}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})
    

#------item---------------------------------------------

@app.route('/item', methods=['GET'])
def get_all_item():
    try:
        query=select(Item)
        data=db.session.execute(query).scalars().all()

        if not data:
            return jsonify({'success':False, 'data':'No item'}),200
        data= [i.serialize() for i in data]

        return jsonify({'success': True, 'data':data}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})
    

@app.route('/item/<string:name>', methods=['GET'])
def get_one_item_by_name(name):
    try:
        query=select(Item).where(Item.name == name)
        item=db.session.execute(query).scalars().all()
        item=[i.serialize() for i in item]

        if not item:
            return jsonify({'success': False, 'data': 'No item found'}), 200

        return jsonify({'success': True, 'data': item}), 200
    except Exception as error:
        return jsonify({'success': False, 'error':error}), 500
    

@app.route('/item/<int:id>', methods=['GET'])
def get_one_item(id):
    try:
       
        item= db.session.get(Item,id)

        if not item:
            return jsonify({'success':False, 'data':'No item found'}),200

        return jsonify({'success': True, 'data':item.serialize()}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})
    

@app.route('/item', methods=['POST'])
def create_item():
    try:
        body = request.json

        if body['name'] is '' or body['categories'] is '':
            return jsonify({'success':False, 'data':'name and categories are required'})
        
        if len(body['name'])< 1 or len(body['categories'])< 1:
            return jsonify({'success':False, 'data':'name and/or categories do not meet the requirements'})

        new_item= Item(
            name = body['name'],
            categories=body['categories'],
            user_id=body['user_id']
        )
        db.session.add(new_item)
        db.session.commit()
    
        return jsonify({'success': True, 'data':new_item.serialize()}),200
    except Exception as error:
        db.session.rollback()
        return jsonify({'success': False, 'error':error})
    


@app.route('/item/<int:id>', methods=['DELETE'])
def delete_item(id):
    try:
       
        item= db.session.get(Item,id)

        if not item:
            return jsonify({'success':False, 'user':'No item found'}),200
        
        db.session.delete(item)
        db.session.commit()

        return jsonify({'success': True, 'data':'item delete'}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})



#------------------favorites-----------------------------------------------------------------


@app.route('/favorites', methods=['GET'])
def get_all_favorites():
    try:
        query=select(Favorites)
        data=db.session.execute(query).scalars().all()

        if not data:
            return jsonify({'success':False, 'data':'No favorites'}),200
        data= [f.serialize() for f in data]

        return jsonify({'success': True, 'data':data}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})
    

@app.route('/favorites/<int:id>', methods=['GET'])
def get_one_favorites(id):
    try:
       
        favorites= db.session.get(Favorites,id)

        if not favorites:
            return jsonify({'success':False, 'data':'No favorites found'}),200

        return jsonify({'success': True, 'data':favorites.serialize()}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})



@app.route('/favorites', methods=['POST'])
def create_favorites():
    try:
        body = request.json

    
        new_favorites= Favorites(
            user_id=body['user_id'],
            pokemon_id=body['pokemon_id'],
            item_id=body['item_id']
        )
        db.session.add(new_favorites)
        db.session.commit()
    
        return jsonify({'success': True, 'data':new_favorites.serialize()}),200
    except Exception as error:
        db.session.rollback()
        return jsonify({'success': False, 'error':error})
    

@app.route('/favorites/<int:id>', methods=['DELETE'])
def delete_favorites(id):
    try:
       
        favorites= db.session.get(Favorites,id)

        if not favorites:
            return jsonify({'success':False, 'user':'No favorites found'}),200
        
        db.session.delete(favorites)
        db.session.commit()

        return jsonify({'success': True, 'data':'favorites delete'}),200
    except Exception as error:
        return jsonify({'success': False, 'error':error})
    


    








































# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
