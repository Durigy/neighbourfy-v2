from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Regexp, InputRequired, NumberRange, Email
from .models import User
from flask_login import current_user
from datetime import timedelta, date

#################################
#                               #
#           User Stuff          #
#                               #
#################################
class RegistrationForm(FlaskForm):
    displayname = StringField('Display Name *', validators=[DataRequired(), Length(min=2, max=15)])
    firstname = StringField('First Name *', validators=[DataRequired(), Length(min=2, max=15)])
    lastname = StringField('Last Name *', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email *', validators=[DataRequired(), Email()])
    postcode = StringField('Postcode *', validators=[DataRequired(), Length(min=6, max=10)])
    password = PasswordField('Password *', validators=[DataRequired()]) #, Regexp('^(?=.*\d).{6,8}$', message='Your password should be between 6 and 8 Charaters long and contain at least 1 number')])
    confirm_password = PasswordField('Confirm Password *', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_displayname(self, displayname):
        user = User.query.filter_by(displayname=displayname.data).first()
        if user:
            raise ValidationError('Display Name already Taken. Please choose a different one.')

    def validate_email(self, email):
       email = User.query.filter_by(email=email.data).first()
       if email:
           raise ValidationError('Email already Used. Please Use a different one.')


class LoginForm(FlaskForm):
    displayname_email = StringField('Display Name or Email')
    password = PasswordField('Password', validators=[DataRequired(), ]) # Regexp('^(?=.*\d).{6,8}$', message='Your password should be between 6 and 8 Charaters long and contain at least 1 number')
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    displayname = StringField('Display Name *', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email *', validators=[DataRequired(), Email()])
    image = FileField('Add a Profile Image (.jpg)', validators=[FileAllowed(['jpg'])])
    firstname = StringField('First Name *', validators=[DataRequired(), Length(min=2, max=15)])
    lastname = StringField('Last Name *', validators=[DataRequired(), Length(min=2, max=15)])
    first_line = StringField('First Line', validators=[Length(max=128)])
    second_line = StringField('Second Line', validators=[Length(max=128)])
    city = StringField('City', validators=[Length(max=128)])
    postcode = StringField('Postcode *', validators=[DataRequired(), Length(min=6, max=9)])
    submit = SubmitField('Update Account')

    def validate_displayname(self, displayname):
        if displayname.data.lower() != current_user.displayname.lower():
            user = User.query.filter_by(displayname=displayname.data).first()
            if user:
                raise ValidationError('Display Name already Taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('Email already Used. Please Use a different one.')

class UserReviewForm(FlaskForm):
    comment = TextAreaField('Write your review', validators=[DataRequired()])
    rating = SelectField('Rating', validators=[DataRequired()], choices=[('1', '1 star'), ('2', '2 stars'), ('3', '3 stars'), ('4', '4 stars'),('5', '5 stars')])
    submit = SubmitField('Submit')


#################################
#                               #
#           Tool Stuff          #
#                               #
#################################

# change from PostForm -> ToolPostForm
class PostForm(FlaskForm):
    Tool_name = StringField('Tool Name', validators=[DataRequired()]) # lowercase first letter
    Tool_description = TextAreaField('Tool Description', validators=[DataRequired()]) # lowercase first letter
    submit = SubmitField('Post Your Tool')
    
#Search form
class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()]) # lowercase first letter
    submit = SubmitField('Post Your Tool')
    
class ToolForm(FlaskForm):
    title = StringField('Tool Name *', validators=[DataRequired(), Length(min=5, max=120)]) # lowercase first letter
    value = IntegerField('Rough value to the nearest £ - Deposit will be calculated as 10% of this number *', validators=[DataRequired()])
    feature_image = FileField('Add a Featured Image (.jpg) *', validators=[FileAllowed(['jpg'])])
    # remove_feature_image = BooleanField('remove Featured Image')
    # image_1 = FileField('Add an extra image (1) (.jpg)', validators=[FileAllowed(['jpg'])])
    # remove_image_1 = BooleanField('remove image (1)')
    # image_2 = FileField('Add an extra image (2) (.jpg)', validators=[FileAllowed(['jpg'])])
    # remove_image_2 = BooleanField('remove image (2)')
    # image_3 = FileField('Add an extra image (3) (.jpg)', validators=[FileAllowed(['jpg'])])
    # remove_image_3 = BooleanField('remove image (3)')
    # image_4 = FileField('Add an extra image (4) (.jpg)', validators=[FileAllowed(['jpg'])])
    # remove_image_4 = BooleanField('remove image (4)')
    description = TextAreaField('Any additional information (optional)')
    lend_duration = IntegerField('Number of days your tool can be borrowed* ', validators=[DataRequired()], default=7)
    is_draft = BooleanField('This is a draft')
    submit = SubmitField('Save Tool')

class ReturnToolForm(FlaskForm):
    image = FileField('Add a Return Image (.jpg) *', validators=[DataRequired(), FileAllowed(['jpg'])])
    submit = SubmitField('Send')

#################################
#                               #
#          Message Stuff        #
#                               #
#################################
class MessageForm(FlaskForm):
    message = StringField('message', validators=[DataRequired()])
    submit = SubmitField('Send')

class ReturnDateForm(FlaskForm):
    date = DateField('Return Date', validators=[DataRequired()], default=date.today() + timedelta(days=7))
    submit = SubmitField('Confirm date')

#################################
#                               #
#          Deposit Stuff        #
#                               #
#################################
class AddFundsForm(FlaskForm):
    ammount = IntegerField('Add amount to the nearest £', validators=[DataRequired(), NumberRange(min=5, max=50, message='must be between £5 and £50')], default=10)
    card_name = StringField('Name on card', validators=[DataRequired()])
    card_num = IntegerField('Card number', validators=[DataRequired()])
    card_cvv = IntegerField('CVV number', validators=[DataRequired()])
    expire_date = DateField('Expire date', validators=[DataRequired()])
    submit = SubmitField('Get Tokens')


# #################################
# #                               #
# #           Admin Stuff         #
# #                               #
# #################################
# class HelpRequestReplyFrom(FlaskForm):
#     message = StringField('Type message here')
#     submit = SubmitField('Send')
