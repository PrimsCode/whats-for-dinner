from flask import Flask, render_template, redirect, flash, url_for, request, session, jsonify, make_response, json
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, DinnerMenu, Recipe, FavoriteDinnerMenu
from forms import LoginForm, SignUpForm
import os
import re

app = Flask(__name__, static_url_path='', static_folder='static')

app.config['SECRET_KEY']=os.environ.get('SECRET_KEY', '12345')
app.debug = True
# debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:admin@localhost:5432/whats_for_dinner').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

@app.route('/')
def landing_page():
    """Show landing page"""
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def show_home():
    """Redirect to sign up or if logged in will redirect to dinner plan"""

    if "user_id" in session:        
        userid = session['user_id']
        user = User.query.get_or_404(userid)
        redirect(f'/{user.username}/dinner-plan')        

    return redirect('/signup')

@app.route('/signup', methods=['GET', 'POST'])
def show_signup_page():
    """Show sign up form"""

    if "user_id" in session:
        flash('Already logged in')
        userid = session['user_id']
        user = User.query.get_or_404(userid)
        return redirect(f'/{user.username}/dinner-plan')

    form = SignUpForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        password = form.password.data

        if User.query.filer_by(username=username).first():
            form.username.errors = ['username already exists, please try a different one']
        else:
            new_user = User.register(username, password, first_name, last_name)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            flash(f'{new_user.username} has signed up')        
            return redirect(f'/{new_user.username}/dinner-plan')               
    
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def show_login_page():
    """Show login form and autenticate user whene log in"""

    if "user_id" in session:
        flash('Already logged in')
        userid = session['user_id']
        user = User.query.get_or_404(userid)
        return redirect(f'/{user.username}/dinner-plan')
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.autenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.first_name}")
            session['user_id'] = user.id
            return redirect(f'/{user.username}/dinner-plan')
        else:
            form.username.errors = ['Invalid username or password']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Log user out"""

    session.pop('user_id')
    return redirect('/login')

@app.route('/<username>/dinner-plan', methods=['GET'])
def plan_dinner(username):
    """Show page to create dinner menu"""
    db.engine.dispose()
    user = User.query.filter_by(username=username).first()
    if db.session.query(DinnerMenu).order_by(DinnerMenu.id.desc()).first():
        dinner = db.session.query(DinnerMenu).order_by(DinnerMenu.id.desc()).first()
        dinner_id = dinner.id
    else:
        dinner_id = 0     
    
    return render_template('dinner_plan.html', user=user, dinner_id=dinner_id)

@app.route('/processInfo/<string:dinner_menu>', methods=['POST', 'GET'])
def processInfo(dinner_menu):
    """Create dinner menu from JS data"""

    userid = session['user_id']
    user = User.query.get_or_404(userid)
    temp_dinner_menu = json.loads(dinner_menu)
    date = temp_dinner_menu['date']['date']
    main_course = temp_dinner_menu['main_course']
      
    if DinnerMenu.query.filter_by(date=date, user_id=user.id).first():
        flash('Dinner Menu Already Exist! Please select a different date', 'error')
        return redirect(f'{user.username}/dinner-plan') 

    if Recipe.query.filter_by(id=main_course['id']).first():
        found_main_course = Recipe.query.filter_by(id=main_course['id']).first()
        new_menu = DinnerMenu(date=date, user_id=user.id, main_course=found_main_course.id)
        db.session.add(new_menu)
        db.session.commit()
    else:
        new_main_course = Recipe(id = main_course['id'], title = main_course['title'])
        db.session.add(new_main_course)
        db.session.commit()

        found_main_course = Recipe.query.filter_by(id=main_course['id']).first()
        new_menu = DinnerMenu(date=date, user_id=user.id, main_course=found_main_course.id)        
        db.session.add(new_menu)
        db.session.commit()

    new_menu = DinnerMenu.query.filter_by(date=date, user_id=user.id).first()   

    if temp_dinner_menu['appetizer']['id'] != None:
        recipe = temp_dinner_menu['appetizer']
        if Recipe.query.get(recipe['id']):
            exist_recipe = Recipe.query.get(recipe['id'])
            new_menu.appetizer = exist_recipe.id
        else:
            new_recipe = Recipe(id = recipe['id'], title = recipe['title'])
            db.session.add(new_recipe)
            db.session.commit()
            added_recipe = Recipe.query.get(recipe['id'])
            new_menu.appetizer = added_recipe.id

    if temp_dinner_menu['side_dish']['id'] != None:
        recipe = temp_dinner_menu['side_dish']
        if Recipe.query.get(recipe['id']):
            exist_recipe = Recipe.query.get(recipe['id'])
            new_menu.side_dish = exist_recipe.id
        else:
            new_recipe = Recipe(id = recipe['id'], title = recipe['title'])
            db.session.add(new_recipe)
            db.session.commit()
            added_recipe = Recipe.query.get(recipe['id'])
            new_menu.side_dish = added_recipe.id

    if temp_dinner_menu['dessert']['id'] != None:
        recipe = temp_dinner_menu['dessert']
        if Recipe.query.get(recipe['id']):
            exist_recipe = Recipe.query.get(recipe['id'])
            new_menu.dessert = exist_recipe.id
        else:
            new_recipe = Recipe(id = recipe['id'], title = recipe['title'])
            db.session.add(new_recipe)
            db.session.commit()
            added_recipe = Recipe.query.get(recipe['id'])
            new_menu.dessert = added_recipe.id
    
    db.session.commit()    
    
    return 'Dinner Menu Created'

@app.route('/dinner-view/<menu_id>', methods=['GET', 'POST'])
def view_complete_dinner(menu_id):
    """Show edit dinner menu"""
    db.engine.dispose()
   
    userid = session['user_id']
    user = User.query.get_or_404(userid)
    menu = DinnerMenu.query.filter_by(id=menu_id).first()
    menu_user = User.query.get_or_404(menu.user_id)

    return render_template('dinner_view.html', user=user, menu=menu, menu_user=menu_user)


@app.route('/dinner-edit/<menu_id>', methods=['GET', 'POST'])
def edit_dinner_plan(menu_id):
    """Edit dinner menu"""
    db.engine.dispose()

    userid = session['user_id']
    user = User.query.get_or_404(userid)
    menu = DinnerMenu.query.filter_by(id=menu_id).first()

    if userid != menu.user_id:
        flash('You are not authorize to edit this dinner menu')
        userid = session['user_id']
        user = User.query.get_or_404(userid)
        return redirect(f'/{user.username}/profile')

    return render_template('dinner_edit.html', user=user, menu=menu)

@app.route('/editInfo/<string:dinner_menu>', methods=['POST', 'GET'])
def editInfo(dinner_menu):
    """Edit created dinner menu from JS data"""

    temp_dinner_menu = json.loads(dinner_menu)
    menu_id = temp_dinner_menu['id']['id']

    menu = DinnerMenu.query.filter_by(id=menu_id).first()

    if temp_dinner_menu['appetizer']['id'] != None:
        recipe = temp_dinner_menu['appetizer']
        if Recipe.query.get(recipe['id']):
            exist_recipe = Recipe.query.get(recipe['id'])
            menu.appetizer = exist_recipe.id
        else:
            new_recipe = Recipe(id = recipe['id'], title = recipe['title'])
            db.session.add(new_recipe)
            db.session.commit()
            added_recipe = Recipe.query.get(recipe['id'])
            menu.appetizer = added_recipe.id

    if temp_dinner_menu['main_course']['id'] != None:
        recipe = temp_dinner_menu['main_course']
        if Recipe.query.get(recipe['id']):
            exist_recipe = Recipe.query.get(recipe['id'])
            menu.main_course = exist_recipe.id
        else:
            new_recipe = Recipe(id = recipe['id'], title = recipe['title'])
            db.session.add(new_recipe)
            db.session.commit()
            added_recipe = Recipe.query.get(recipe['id'])
            menu.main_course = added_recipe.id

    if temp_dinner_menu['side_dish']['id'] != None:
        recipe = temp_dinner_menu['side_dish']
        if Recipe.query.get(recipe['id']):
            exist_recipe = Recipe.query.get(recipe['id'])
            menu.side_dish = exist_recipe.id
        else:
            new_recipe = Recipe(id = recipe['id'], title = recipe['title'])
            db.session.add(new_recipe)
            db.session.commit()
            added_recipe = Recipe.query.get(recipe['id'])
            menu.side_dish = added_recipe.id

    if temp_dinner_menu['dessert']['id'] != None:
        recipe = temp_dinner_menu['dessert']
        if Recipe.query.get(recipe['id']):
            exist_recipe = Recipe.query.get(recipe['id'])
            menu.dessert = exist_recipe.id
        else:
            new_recipe = Recipe(id = recipe['id'], title = recipe['title'])
            db.session.add(new_recipe)
            db.session.commit()
            added_recipe = Recipe.query.get(recipe['id'])
            menu.dessert = added_recipe.id
    
    db.session.commit()
    
    return 'Dinner Menu Edited'

@app.route('/<username>/profile', methods=['GET'])
def show_user_profile(username):
    """Show user profile"""
    db.engine.dispose()
    user = User.query.filter_by(username=username).first()
    dinners = db.session.query(DinnerMenu).filter_by(user_id=user.id).order_by(DinnerMenu.date.desc()).all()

    return render_template('user_profile.html', user=user, dinners=dinners)

@app.route('/<username>/favorites', methods=['GET'])
def show_favorite_dinners(username):
    """Show user's favorite dinner menus'"""
    db.engine.dispose()
    user = User.query.filter_by(username=username).first()
    dinners = db.session.query(DinnerMenu).filter_by(user_id=user.id).order_by(DinnerMenu.date.desc()).all()

    return render_template('dinner_favorites.html', user=user, dinners=dinners)

@app.route('/processFav/<string:favorite>', methods=['POST', 'GET'])
def processFav(favorite):
    """create favorite dinner menu"""

    db.engine.dispose()

    userid = session['user_id']
    favorite = json.loads(favorite)    

    add_favorite = FavoriteDinnerMenu(dinner_id=favorite['dinner_id'], user_id=userid)
    db.session.add(add_favorite)
    db.session.commit()

    return 'Add Favorite' 

@app.route('/processUnFav/<string:favorite>', methods=['POST', 'GET'])
def processUnFav(favorite):
    """Unfavorite dinner menu"""

    db.engine.dispose()

    userid = session['user_id']
    favorite = json.loads(favorite)
    unfavorite = FavoriteDinnerMenu.query.filter_by(dinner_id=favorite['dinner_id'], user_id=userid).first() 
    db.session.delete(unfavorite)
    db.session.commit()

    return 'Delete Favorite' 

@app.route('/printable/<menu_id>/<recipe_id>', methods=['GET'])
def show_printable_recipe(menu_id, recipe_id):
    """Show printable page for a recipe"""

    db.engine.dispose()

    userid = session['user_id']
    user = User.query.get_or_404(userid)
    menu = DinnerMenu.query.filter_by(id=menu_id).first()
    recipe = Recipe.query.get_or_404(recipe_id)
    
    return render_template('print_recipe.html', user=user, menu=menu, recipe=recipe)

@app.route('/printable/<menu_id>/<recipe_id>/shopping-list', methods=['GET'])
def show_printable_shopping_list(menu_id, recipe_id):
    """Show printable page for a recipe's shopping list"""

    db.engine.dispose()

    userid = session['user_id']
    user = User.query.get_or_404(userid)
    menu = DinnerMenu.query.filter_by(id=menu_id).first()
    recipe = Recipe.query.get_or_404(recipe_id)
    
    return render_template('print_ingredients.html', user=user, menu=menu, recipe=recipe)

@app.route('/printable/<menu_id>', methods=['GET'])
def show_print_all_recipes(menu_id):
    """Show printable page for all recipes in the dinner menu"""

    db.engine.dispose()

    userid = session['user_id']
    user = User.query.get_or_404(userid)
    menu = DinnerMenu.query.filter_by(id=menu_id).first()   
    recipes = []

    if menu.appetizer_recipe != None:
        recipes += [menu.appetizer_recipe.id]

    recipes += [menu.main_course_recipe.id]

    if menu.side_dish_recipe != None:
        recipes += [menu.side_dish_recipe.id]
    if menu.dessert_recipe != None:
        recipes += [menu.dessert_recipe.id] 

    return render_template('print_all_recipes.html', user=user, menu=menu, recipes=recipes)

@app.route('/printable/<menu_id>/shopping-list-all', methods=['GET'])
def show_printable_all_shopping_list(menu_id):
    """Show dinner menu shopping list"""

    db.engine.dispose()

    userid = session['user_id']
    user = User.query.get_or_404(userid)
    menu = DinnerMenu.query.filter_by(id=menu_id).first()
    recipes = []

    if menu.appetizer_recipe != None:
        recipes += [menu.appetizer_recipe.id]

    recipes += [menu.main_course_recipe.id]

    if menu.side_dish_recipe != None:
        recipes += [menu.side_dish_recipe.id]
    if menu.dessert_recipe != None:
        recipes += [menu.dessert_recipe.id]
    
    return render_template('print_all_ingredients.html', user=user, menu=menu, recipes=recipes)
