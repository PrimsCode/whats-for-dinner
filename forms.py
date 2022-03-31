from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import InputRequired

class SignUpForm(FlaskForm):

    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class LoginForm(FlaskForm):

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

# class DinnerForm(FlaskForm):
#     appetizer = ("Appetizer")
#     main_course = ("Main Course", validators=[InputRequired()])
#     side_dish = ("Side Dish")
#     dessert = ("Dessert")

# class RecipeForm(FlaskForm):
#     title = StringField("Title", validators=[InputRequired()])
#     dish_type = Choice-("Title", validators=[InputRequired()])
#     servings = IntegerField("Serving Size", validators=[InputRequired()])    
#     cook_time = Time("Cook Time", validators=[InputRequired()])
#     ingredients = Array("Description", validators=[InputRequired()])
#     instructions = Array("Description", validators=[InputRequired()])
#     summary = StringField("Description", validators=[InputRequired()])
#     image_url = StringField("Image", validators=[InputRequired()]) 

