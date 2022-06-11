from datetime import datetime
from email.policy import default
from . import db, login_manager
from flask_login import UserMixin

#############################
#                           #
#       User Stuff          #
#                           #
#############################

class User(UserMixin, db.Model):
    # Datebase Columns #
    id = db.Column(db.String(20), primary_key = True)
    displayname = db.Column(db.String(15), unique = True, nullable = False)
    firstname = db.Column(db.String(15), nullable = False)
    lastname = db.Column(db.String(15), nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(128), nullable = False)
    joined_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    first_line = db.Column(db.String(128), nullable = True)
    second_line = db.Column(db.String(128), nullable = True)
    city = db.Column(db.String(128), nullable = True)
    postcode = db.Column(db.String(10), nullable = True)

    profile_pic = db.Column(db.String(20), nullable = True, default = '') # ADD A DEFAULT USER PIC URI
    balance = db.Column(db.Integer, nullable = True, default = 0) # balance to keep track when a user tops up their account balance
    agv_rating = db.Column(db.Float, nullable = True, default = 0) # this is the average rating of a user based on all their ratings
    num_of_ratings = db.Column(db.Integer, nullable = True, default = 0) # number of rating a user has against them
    
    # Links (ForeignKeys) #
    user_role_id = db.Column(db.Integer, db.ForeignKey('user_role.id'), nullable = False, default = 1)

    # Relationships #
    # so with this relationship we can do: user.tools(.append/.remove/etc.) or tool.user(.etc...)
    tool = db.relationship('Tool', backref = 'author', lazy = True, foreign_keys = 'Tool.user_id')
    # lender_review = db.relationship('UserReview', backref='lender', lazy=True, foreign_keys='UserReview.lender_id')
    # borrower_review = db.relationship('UserReview', backref='borrower', lazy=True, foreign_keys='UserReview.borrower_id')
    reviewed_user = db.relationship('UserReview', backref = 'reviewed_user', lazy = True, foreign_keys = 'UserReview.reviewed_user_id')
    reviewing_user = db.relationship('UserReview', backref = 'reviewing_user', lazy = True, foreign_keys = 'UserReview.reviewing_user_id')
    lender_tool_swap = db.relationship('ToolSwap', backref = 'lender', lazy = True, foreign_keys='ToolSwap.lender_id')
    borrower_tool_swap = db.relationship('ToolSwap', backref = 'borrower', lazy = True, foreign_keys = 'ToolSwap.borrower_id')
    help_request = db.relationship('HelpRequest', backref = 'user', foreign_keys = 'HelpRequest.user_id')
    sender = db.relationship('Message', backref = 'sender', foreign_keys = 'Message.sender_id')
    # recepient = db.relationship('Message', backref = 'recepient', foreign_keys = 'Message.recepient_id')
    # lender_message_thread = db.relationship('MessageThread', backref = 'lender', foreign_keys = 'MessageThread.lender_id')
    # borrower_message_thread = db.relationship('MessageThread', backref = 'borrower', foreign_keys = 'MessageThread.borrower_id')
    desposit_transaction = db.relationship('DespositTransaction', backref = 'user', foreign_keys = 'DespositTransaction.user_id')

    # posts = db.relationship('Post', backref = 'author', lazy = True, foreign_keys = 'Post.user_id') # intergrate from post to tool

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class UserRole(db.Model):
    # Datebase Columns #
    id = db.Column(db.Integer, primary_key = True)
    role = db.Column(db.String(30), unique = True, nullable = False)
    
    # Links (ForeignKeys) #
    # Add here

    # Relationships #
    user = db.relationship('User', backref = 'user_role', lazy = True, foreign_keys = 'User.user_role_id')

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this

class UserReview(UserMixin, db.Model):
    # Datebase Columns #
    id = db.Column(db.String(20), primary_key = True)
    rating = db.Column(db.Float, nullable = False)
    comment = db.Column(db.Text, nullable = False)
    date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    is_inappropriate = db.Column(db.Boolean, nullable = False, default = False)

    # Links (ForeignKeys) #
    # lender_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable=False)
    # borrower_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable=False)
    reviewed_user_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)
    reviewing_user_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)
    # tool_id = db.Column(db.String(20), db.ForeignKey('tool.tool_id'), nullable=False)

    # Relationships #
    # Add here

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this

    
#############################
#                           #
#       Tool Stuff          #
#                           #
#############################        
class Tool(UserMixin, db.Model):
    # Datebase Columns #
    id = db.Column(db.String(20), primary_key = True)
    title = db.Column(db.String(120), nullable = False)
    deposit = db.Column(db.Integer, nullable = False)
    listed_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    feature_image = db.Column(db.String(20), nullable = False, default = 'default')
    image_1 = db.Column(db.String(20), nullable = False)
    image_2 = db.Column(db.String(20), nullable = False)
    image_3 = db.Column(db.String(20), nullable = False)
    image_4 = db.Column(db.String(20), nullable = False)
    description = db.Column(db.Text, nullable = True)
    is_draft = db.Column(db.Boolean, nullable = True, default = False)
    return_date = db.Column(db.DateTime, nullable = True)
    lend_duration = db.Column(db.Integer, nullable = False)

    # Links (ForeignKeys) #
    user_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)
    
    # status/condition of the tool before the tool swap
    condition_id = db.Column(db.Integer, db.ForeignKey('tool_condition.id'), nullable = False)
    status_id = db.Column(db.Integer, db.ForeignKey('tool_status.id'), nullable = False)

    # Relationships #
    tool_swap = db.relationship('ToolSwap', backref = 'tool', lazy = True, foreign_keys = 'ToolSwap.tool_id')

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this

# ---- This has had a good run, but tool will take it from here ---- #
# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     Tool_name = db.Column(db.String(120), nullable = False)
#     date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
#     Tool_description = db.Column(db.Text, nullable = False)

#     # Links (ForeignKeys) #
#     user_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)

#     # Relationships #
#     # Add here

#     # def __repr__(self):
#     #     return f"Post('{self.Tool_name}, {self.Tool_description}, {self.date_posted}')" # add this to all table if time -> good practice 
# ---- This has had a good run, but tool will take it from here ---- #

class ToolCondition(UserMixin, db.Model):
    # Datebase Columns #
    id = db.Column(db.Integer, primary_key = True)
    condition = db.Column(db.String(120), nullable = True)
    
    # Links (ForeignKeys) #
    # Add here

    # Relationships #
    tool = db.relationship('Tool', backref = 'tool_condition', lazy = True, foreign_keys = 'Tool.condition_id')
    borrowed_tool_condition = db.relationship('ToolSwap', backref = 'borrowed_tool_condition', lazy = True, foreign_keys = 'ToolSwap.borrowed_tool_condition_id')
    returned_tool_condition = db.relationship('ToolSwap', backref = 'returned_tool_condition', lazy = True, foreign_keys = 'ToolSwap.returned_tool_condition_id')

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this

class ToolStatus(UserMixin, db.Model):
    # Datebase Columns #
    id = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.String(120), nullable = True)

    # Links (ForeignKeys) #
    # Add here

    # Relationships #
    tool = db.relationship('Tool', backref = 'tool_status', lazy = True, foreign_keys = 'Tool.status_id')
    borrowed_tool_status = db.relationship('ToolSwap', backref = 'borrowed_tool_status', lazy = True, foreign_keys = 'ToolSwap.borrowed_tool_status_id')
    returned_tool_status = db.relationship('ToolSwap', backref = 'returned_tool_status', lazy = True, foreign_keys = 'ToolSwap.returned_tool_status_id')

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this


#############################
#                           #
#       Order Stuff         #
#                           #
#############################
class ToolSwap(UserMixin, db.Model):
    # Datebase Columns #
    id = db.Column(db.String(20), primary_key = True)
    borrow_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable = True)

    deposit = db.Column(db.Integer, nullable=False)

    is_paid = db.Column(db.Boolean, nullable = True, default = False)
    is_refunded = db.Column(db.Boolean, nullable = True, default = False)
    return_photo = db.Column(db.String(20), nullable = False, default = '')

    # Links (ForeignKeys) #
    lender_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)
    borrower_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)

    borrowed_tool_condition_id = db.Column(db.Integer, db.ForeignKey('tool_condition.id'), nullable = False)
    borrowed_tool_status_id = db.Column(db.Integer, db.ForeignKey('tool_status.id'), nullable = False)

    returned_tool_condition_id = db.Column(db.Integer, db.ForeignKey('tool_condition.id'), nullable = True)
    returned_tool_status_id = db.Column(db.Integer, db.ForeignKey('tool_status.id'), nullable = True)
    
    tool_id = db.Column(db.String(20), db.ForeignKey('tool.id'), nullable = False)

    # Relationships #
    help_request = db.relationship('HelpRequest', backref = 'tool_swap', foreign_keys = 'HelpRequest.tool_swap_id')
    message_thread = db.relationship('MessageThread', backref = 'tool_swap', foreign_keys = 'MessageThread.tool_swap_id')
    desposit_transaction = db.relationship('DespositTransaction', backref = 'tool_swap', foreign_keys = 'DespositTransaction.tool_swap_id')

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this


#############################
#                           #
#       Message Stuff       #
#                           #
#############################
class Message(db.Model):
    id = db.Column(db.String(20), primary_key = True)
    message = db.Column(db.Text, nullable = False)
    date_sent = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    # Links (ForeignKeys) #
    sender_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)
    message_thread_id = db.Column(db.String(20), db.ForeignKey('message_thread.id'), nullable = False)

    # Relationships #
    # Add here

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this

class MessageThread(db.Model):
    id = db.Column(db.String(20), primary_key = True)
    message_count = db.Column(db.Integer, nullable = True, default = 0)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable = True, default = True)

    # Links (ForeignKeys) #
    # lender_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)
    # borrower_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)
    tool_swap_id = db.Column(db.String(20), db.ForeignKey('tool_swap.id'), nullable = False)
    
    # Relationships #
    message = db.relationship('Message', backref = 'message_thread', foreign_keys = 'Message.message_thread_id')

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this


#############################
#                           #
#       Desposit Stuff      #
#                           #
#############################
class DespositTransaction(db.Model):  # tracks deposits transactions
    # Datebase Columns #
    id = db.Column(db.String(20), primary_key = True)
    amount = db.Column(db.Integer, nullable = False)
    fee_amount = db.Column(db.Integer, nullable = False)
    transaction_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    is_returned = db.Column(db.Boolean, nullable = True, default = False)
        
    # Links (ForeignKeys) #
    user_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)
    tool_swap_id = db.Column(db.String(20), db.ForeignKey('tool_swap.id'), nullable = False)

    # Relationships #
    # Add here

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this


#############################
#                           #
#       Admin Stuff         #
#                           #
#############################
class AdminStat(db.Model):
    # Datebase Columns #
    id = db.Column(db.String(20), primary_key = True)
    num_of_users = db.Column(db.Integer, nullable = False)
    num_of_active_tools = db.Column(db.Integer, nullable = False)
    num_of_loan_tools = db.Column(db.Integer, nullable = False)
    num_of_pending_messages = db.Column(db.Integer, nullable = False)
    total_of_current_deposits = db.Column(db.Integer, nullable = False)
    
    # Links (ForeignKeys) #
    # Add here

    # Relationships #
    # Add here

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this

class HelpRequest(db.Model):
    id = db.Column(db.String(20), primary_key = True)
    message = db.Column(db.Text, nullable = False)
    date_sent = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    # Links (ForeignKeys) #
    user_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable = False)
    tool_swap_id = db.Column(db.String(20), db.ForeignKey('tool_swap.id'), nullable = False)

    # Relationships #
    # Add here

    # def __repr__(self):
    #     return f"User('{self.name}, {self.description}, {self.date}')" # Update this




#########################################################################


# from user probably not needed

# Functions #
    # @property
    # def password(self):
    #     raise AttributeError('password is not a readable attribute')
    

    #test: r = models.UserReview.query.filter_by(review_id='1').first()
    #r.lender

    # # Set functions #   

    # # def set_first_name(self, n):
    # #     assert n is not None and n != '' and type(n) == str, f'"{n}" is not a valid name.'
    # #     self.firstname = n
    # #     db.session.commit()

    # # def set_last_name(self, n):
    # #     assert n is not None and n != '' and type(n) == str, f'"{n}" is not a valid name.'
    # #     self.lastname = n
    # #     db.session.commit()
    
    # # def set_display_name(self, n):
    # #     assert n is not None and n != '' and type(n) == str, f'"{n}" is not a valid name.'
    # #     self.displayname = n
    # #     db.session.commit()

    # # def set_email(self, n):
    # #     assert n is not None and n != '' and type(n) == str, f'"{n}" is not a valid email.'
    # #     self.email = n
    # #     db.session.commit()

    # # Saves only the name of the file not the file type
    # def set_profile_image(self, uri):
    #     assert type(uri) == str
    #     if uri == None:
    #         uri = ''
    #     self.profile_pic_uri = self.save_account_pic(uri)
    #     db.session.commit()
    
    # # def set_address(self, firstline = None, secondline = None, city = None, postcode = None):
    # #     '''You can pass through as arguments only the values you want changed.
    # #     The rest of the values will remain the same.'''
    # #     if firstline is not None:
    # #         self.first_line = firstline
    # #     if secondline is not None:
    # #         self.second_line = secondline
    # #     if city is not None:
    # #         self.city = city
    # #     if postcode is not None:
    # #         self.postcode = postcode
    # #     db.session.commit()


    # # Get Functions #

    # # # A user will only have one role sorry    
    # # def get_role(self):
    # #     return self.user_role_id
    
    # def get_full_address(self) -> dict:
    #     '''returns dictionary whose keys are components of an address'''
    #     # return {'first_line':self.first_line, 'second_line':self.second_line, 'city':self.city, 'postcode':self.postcode}
    #     return f'{self.first_line}, {self.second_line}, {self.city}, {self.postcode}'
    
    # # def get_first_name(self):
    # #     return self.firstname

    # # def get_last_name(self):
    # #     return self.lastname

    # # def get_display_name(self):
    # #     return self.displayname
    
    # # def get_email(self):
    # #     return self.email

    # def get_profile_image(self):
    #     pic_file_name = self.profile_pic_uri + '.jpg'
    #     return pic_file_name

    # # def get_password(self):
    # #     raise self.password

    # # @staticmethod
    # # def get_user(uid = None, dp = None, em = None):
    # #     '''returns query object of user given id or displayname or email'''
    # #     if uid is not None: return User.query.filter_by(user_id=uid).first()
    # #     if dp is not None: return User.query.filter_by(displayname=dp).first()
    # #     if em is not None: return User.query.filter_by(email=em).first()


    # # Other Functions #

    # # Sets the name of the image to a new random 20 char strin
    # def generate_id(self):        
    #     id = secrets.token_hex(10)
    #     return id

    # def save_account_pic(self, form_picture):
    #     random_hex = self.generate_id()
    #     pic_file_name = random_hex + '.jpg'
    #     picture_path = os.path.join(app.root_path, 'static/img/profile', pic_file_name)

    #     output_size = (125, 125)
    #     processed_image = Image.open(form_picture)
    #     processed_image.thumbnail(output_size)
    #     processed_image.save(picture_path)

    #     return random_hex