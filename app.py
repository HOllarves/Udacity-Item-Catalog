"""
Application entry point.

Routes and business logic code is handled here.
"""

from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash, make_response, session as login_session
import random
import string
import httplib2
import json
import requests
from sqlalchemy import asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User, engine
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

app = Flask(__name__)
app.static_folder = 'static'

# Loads Google's OAuth credentials
CLIENT_ID = json.loads(
    open('config/client_secret.json', 'r').read())['web']['client_id']

# Starting DB Session
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/gdisconnect')
def gdisconnect():
    """
    Google's logout endpoint.

    Destroys session and removes user information
    """
    access_token = None
    try:
        access_token = login_session['credentials']
        print "Access token! " + access_token
    except FlowExchangeError:
        response = make_response(
            json.dumps(
                'Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if not access_token:
        response = make_response(
            json.dumps(
                'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        flash("{}".format('Current user not connected.'))
        return redirect('/')

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(
            json.dumps(
                'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("{}".format("Successfully disconnected."))
        return redirect('/')
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        flash("{}".format('Failed to revoke token for given user.'))
        return redirect('/')


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Google's OAuth callback endpoint.

    For user authentication.
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Authorization code
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets(
            'config/client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']

    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')

    # If the user is already logged in
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps(
                'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Obtaining user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Retrieving user information
    # Saving it to the login_session
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Saving user id
    user_id = getUserId(login_session['email'])
    if not user_id:
        createUser(login_session)
        login_session['user_id'] = user_id

    return redirect('/')


@app.route('/')
def render_home():
    """
    METHOD=GET.

    Renders Home Page.
    """
    if 'username' not in login_session:
        state = ''.join(
            random.choice(
                string.ascii_uppercase + string.digits) for x in xrange(
                    32))
        login_session['state'] = state
        return render_template('home.html', STATE=state)
    else:
        return render_template('home.html')


@app.route('/categories')
def render_list_categories():
    """
    METHOD=GET.

    Renders Category Page.
    """
    categories = session.query(Category).order_by(asc(Category.name)).all()
    return render_template('categories/list.html', categories=categories)


@app.route('/categories/json')
def render_list_categoires_json():
    """
    METHOD=GET.

    Returns JSON object with the list of available
    categories.
    """
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if categories:
        return jsonify(status=200, data=[i.serialize for i in categories])
    else:
        return jsonify(status=404, message="No categories found")


@app.route('/categories/new', methods=['GET', 'POST'])
def render_new_category():
    """
    METHOD=GET.

    Renders New Category Page.

    METHOD=POST.

    Creates new category
    """
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        user_id = getUserId(login_session['email'])
        if name and user_id:
            new_category = Category(name=name, description=description, user_id=user_id)
            session.add(new_category)
            session.commit()
            return redirect(url_for('render_list_categories'))
    else:
        return render_template('categories/new.html')


@app.route('/categories/show/<int:category_id>')
def render_show_category(category_id):
    """
    METHOD=GET.

    Renders Show Category Page
    """
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    print items
    return render_template(
        '/categories/show.html', category=category, items=items)


@app.route('/categories/show/<int:category_id>/json')
def render_show_category_json(category_id):
    """
    METHOD=GET.

    Returns a JSON object of a specific category
    """
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    if category and items:
        return jsonify(
            status=200,
            category=[category.serialize],
            items=[i.serialize for i in items])
    else:
        return jsonify(status=404, message="Category not found")


@app.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
def render_edit_category(category_id):
    """
    METHOD=GET.

    Renders Edit Category Page.

    METHOD=POST

    Modifies a specific category and saves it to the databse
    """
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == "POST":
        if getUserId(login_session['email']) == category.user_id:
            name = request.form["name"]
            description = request.form["description"]
            if name and description:
                category.name = name
                category.description = description
                session.add(category)
                session.commit()
                return redirect(
                    url_for(
                        "render_show_category", category_id=category.id))
            else:
                flash("No name was provided")
                return redirect(
                    url_for(
                        "render_show_category", category_id=category.id))
        else:
            flash("You cannot modify this item")
            return redirect(
                url_for(
                    "render_show_category", category_id=category.id))
    else:
        return render_template('categories/edit.html', category=category)


@app.route('/categories/delete/<int:category_id>', methods=['GET', 'POST'])
def render_delete_category(category_id):
    """
    METHOD=GET.

    Renders Delete Category confirmation page.

    METHOD=DEL.

    Deletes a specific category
    """
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == "POST":
        if getUserId(login_session['email']) == category.user_id:
            session.delete(category)
            session.commit()
            return redirect(url_for('render_list_categories'))
        else:
            flash("You cannot modify this item")
            return redirect(url_for('render_list_categories'))
    else:
        return render_template(
            'categories/delete.html', category=category)


@app.route('/categories/<int:category_id>/item/<int:item_id>')
def render_item(category_id, item_id):
    """
    METHOD=GET.

    Renders Item Page.
    """
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('items/show.html', item=item, category=category)


@app.route('/categories/<int:category_id>/item/<int:item_id>/json')
def render_item_json(category_id, item_id):
    """
    METHOD=GET.

    Returns a JSON object of a specific item and
    it's category.
    """
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(
        status=200,
        category=category.serialize,
        item=item.serialize)


@app.route('/categories/<int:category_id>/item/new/')
def render_new_item(category_id):
    """
    METHOD=GET.

    Renders New Item Page.

    METHOD=POST

    Creates new Item.
    """
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        user_id = getUserId(login_session['email'])
        category_id = category_id
        if name and price and description and category_id and user_id:
            item = Item(
                user_id=user_id,
                name=name,
                price=price,
                description=description,
                category_id=category_id)
            session.add(item)
            session.commit()
            return redirect(url_for('render_list_categories'))
        else:
            flash("Some values are missing")
            return redirect(url_for('render_new_item', category_id=category_id))
    else:
        return render_template('items/new.html')


@app.route(
    '/categories/<int:category_id>/item/edit/<int:item_id>',
    methods=['GET', 'POST'])
def render_edit_item(category_id, item_id):
    """
    METHOD=GET.

    Renders Edit Item Page.

    METHOD=PUT

    Modifies a specific item and saves it to the databse
    """
    old_item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if getUserId(login_session['email']) == old_item.user_id:
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            category_id = category_id
            if name and price and description and category_id:
                old_item.name = name
                old_item.price = price
                old_item.description = description
                category_id = category_id
                session.add(old_item)
                session.commit()
                return redirect(
                    url_for(
                        'render_show_category', category_id=category_id))
            else:
                flash("Some values are missing")
                url_for(
                    'render_show_category', category_id=category_id)
        else:
            flash("You cannot modify this item")
            return redirect(
                url_for(
                    'render_show_category', category_id=category_id))
    else:
        return render_template(
            'items/edit.html', item=old_item, category_id=category_id)


@app.route(
    '/categories/<int:category_id>/item/delete/<int:item_id>',
    methods=['GET', 'POST'])
def render_delete_item(category_id, item_id):
    """
    METHOD=GET.

    Renders Delete Item Page.

    METHOD=DEL

    Deletes a specific item
    """
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if getUserId(login_session['email']) == item.user_id:
            session.delete(item)
            session.commit()
            return redirect(
                url_for(
                    'render_show_category', category_id=category_id))
        else:
            flash("You cannot modify this item")
            return redirect(
                url_for(
                    'render_show_category', category_id=category_id))
    else:
        return render_template(
            'items/delete.html', item=item, category_id=category_id)


def createUser(login_session):
    """
    Create User function.

    Args:
        login_session: flask login_session object
    Returns:
        id of created user
    """
    new_user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    Get user info function.

    Args:
        user_id: User's ID
    Returns:
        User info.
    """
    return session.query(User).filter_by(id=user_id).one()


def getUserId(email):
    """
    Get user id function.

    Args:
        email: User's email address
    Returns:
        User's ID.
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Firing up our server :D
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
