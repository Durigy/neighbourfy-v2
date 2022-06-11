from datetime import date
import secrets
import os
from PIL import Image
from flask import url_for, redirect
from . import app, db, bcrypt
from .models import Message, MessageThread, Tool, User, UserRole, ToolSwap, ToolStatus, ToolCondition, UserReview
from .forms import LoginForm, MessageForm, RegistrationForm, UpdateAccountForm, ToolForm, UserReviewForm, SearchForm, AddFundsForm, ReturnDateForm, ReturnToolForm #, HelpRequestReplyFrom
from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, url_for, request, redirect, flash, abort
from difflib import SequenceMatcher

#################################
#                               #
#           Site Stuff          #
#                               #
#################################

# Reference: https://stackoverflow.com/questions/32237379/python-flask-redirect-to-https-from-http
@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


@app.route("/")
def index():
    # posts = Post.query.all()
    return render_template(
        'index.html',
        title='Home'
    )

# when '/home' or '/index' are typed in the URL or redirected, it will the redirect to the url without anything after the /
@app.route("/index")
@app.route("/home")
def home_redirect():
    return redirect(url_for('index'))


# Reference: https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', title='Page Not Found'), 404

#Passing stuff to searchform on navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route("/about")
def about():
    return render_template(
        'about.html',
        title='about'
    )


#################################
#                               #
#           User Stuff          #
#                               #
#################################

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit() and request.method == "POST":
        user_id = generate_id()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(
            id = user_id, 
            displayname = form.displayname.data,
            firstname = form.firstname.data,
            lastname = form.lastname.data,
            email = form.email.data,
            postcode =form.postcode.data,
            password = hashed_password
        )

        db.session.add(user)
        db.session.commit()
        flash('Account Created - You can now Login in')
        return redirect(url_for('login'))
    return render_template(
        'user/register.html',
        title='Register',
        form=form
    )


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit() and request.method == "POST":
        user = ''
        if User.query.filter_by(displayname = form.displayname_email.data).first():
            user = User.query.filter_by(displayname = form.displayname_email.data).first()
        elif User.query.filter_by(email = form.displayname_email.data).first():
            user = User.query.filter_by(email = form.displayname_email.data).first()

        # user = User.query.filter_by(displayname = form.displayname.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for("index"))
        else:
            flash('Login Unsuccessful. Check displayname/email and Password')

    return render_template(
        'user/login.html',
        title = 'Login',
        form = form
    )

@app.route("/logout")
def logout():
    logout_user()
    return redirect(request.referrer)

def generate_id():
    id = secrets.token_hex(10)
    return id


#################################
#                               #
#         Account Stuff         #
#                               #
#################################
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    lending_page = request.args.get('lending_page', 1, type=int)
    borrowing_page = request.args.get('borrowing_page', 1, type=int)
    
    # lending_message_threads = MessageThread.query.filter(MessageThread.tool_swap.lender_id == current_user.id).all()
    lending_message_threads = MessageThread.query.outerjoin(ToolSwap, MessageThread.tool_swap_id == ToolSwap.id).filter(ToolSwap.lender_id == current_user.id).order_by(MessageThread.is_active.desc(), MessageThread.date_created.desc()).paginate(page=lending_page, per_page=3)
    borrowing_message_threads = MessageThread.query.outerjoin(ToolSwap, MessageThread.tool_swap_id == ToolSwap.id).filter(ToolSwap.borrower_id == current_user.id).order_by(MessageThread.is_active.desc(), MessageThread.date_created.desc()).paginate(page=borrowing_page, per_page=3)
    
    # page = request.args.get('page', 1, type=int)
    # tool_posts = Tool.query.order_by(Tool.listed_date.desc()).paginate(page=page, per_page=3)

    form = UpdateAccountForm()
    if form.validate_on_submit() and request.method == "POST":
        if form.image.data:
            form_picture = save_account_pic(form.image.data)
            current_user.profile_pic = form_picture

        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.displayname = form.displayname.data
        current_user.email = form.email.data
        current_user.first_line = form.first_line.data
        current_user.second_line = form.second_line.data
        current_user.city = form.city.data
        current_user.postcode = form.postcode.data
        db.session.commit()
        flash('Your account was updated')

        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.displayname.data = current_user.displayname
        form.email.data = current_user.email
        form.first_line.data = current_user.first_line
        form.second_line.data = current_user.second_line
        form.city.data = current_user.city
        form.postcode.data = current_user.postcode

    profile_image = url_for('static', filename='img/' + current_user.profile_pic + '.jpg')
    # print(profile_image)

    return render_template(
        'user/account.html',
        title='Account',
        profile_image=profile_image,
        form=form,
        lending_message_threads = lending_message_threads,
        borrowing_message_threads = borrowing_message_threads
    )

@app.route("/account_public/<user_id>", methods=['GET', 'POST'])
#@login_required
def account_public(user_id):
    user = User.query.get_or_404(user_id)
    form = UserReviewForm()
    reviews = UserReview.query.filter(UserReview.reviewed_user_id==user_id).all()
    
    if current_user.is_authenticated:
        if user_id == current_user.id:
            tools = Tool.query.filter(Tool.user_id==user_id).all()
        else:
            tools = Tool.query.filter((Tool.user_id==user_id) & (Tool.is_draft == False)).all()
    else:
        tools = Tool.query.filter((Tool.user_id==user_id) & (Tool.is_draft == False)).all()

    # reviews.sort(key=lambda review: -review.date)
    reviews.sort(key=lambda review: review.date)
    reviews = reviews[::-1]
    error = ''

    total_ratings = []
    total_reviews = 0
    average_rating = 0

    for review in reviews:
        total_ratings.append(review.rating)

    if len(total_ratings) != 0:
        average_rating = f'{(sum(total_ratings)/len(total_ratings)):.1f}'
        total_reviews = len(total_ratings)
    else:
        average_rating = "No reviews yet."
        total_reviews = 0

    # CHECK IF THE LOGGED IN USER HAS DONE A TOOLSWAP WITH THE PERSON WHOSE PROFILE THEY ARE VIEWING
    #IF YES ALLOW THEM TO POST REVIEW, IF NOT THEN DON'T (add parameter has_done_tool_swap below to pass to the html page)

    return render_template(
        'user/account_public.html',
        average_rating=average_rating,
        total_reviews=total_reviews,
        user=user,
        form=form,
        error=error,
        reviews=reviews,
        tools=tools
    )


#################################
#                               #
#      USER REVIEW Stuff        #
#                               #
#################################
@app.route('/account_public/<reviewed_user_id>/review', methods=['POST', 'GET'])
@login_required
def post_user_review(reviewed_user_id):
    form = UserReviewForm() #implement UserReviewForm
    error = None
    if request.method == 'POST':
        # print('TEST TEST TEST')
        # if form.validate_on_submit():
        review = UserReview(
            id = generate_id(), 
            comment = form.comment.data, 
            rating = form.rating.data,
            reviewing_user_id = current_user.id, 
            reviewed_user_id = reviewed_user_id
        )

        db.session.add(review)

        reviewed_user = User.query.filter_by(id = reviewed_user_id).first()
        reviewed_user.num_of_ratings += 1

        db.session.commit()
        return redirect(f'/account_public/{reviewed_user_id}')
    
    if request.method == 'GET': # this means redirected from login() using request.referrer which uses 'GET'

        # ADD THE COMMENT TO THE URL TO AUTOMATICALLY POST IT WHEN LOGGING BACK IN

        if reviewed_user_id == current_user.id:
            return redirect('/home')
        else:
            return redirect(f'/account_public/{reviewed_user_id}')

@app.route('/account_public/<review_id>/remove_review')
def remove_review(review_id):
    # reviews = Review.query.all()
    review = UserReview.query.get_or_404(review_id)
    reviewed_user = User.query.filter_by(id = review.reviewed_user_id).first()
    reviewed_user.num_of_ratings -= 1
    
    db.session.delete(review)
    db.session.commit()
    # i = 0
    # for review in reviews:
    #     review.id = i
    #     i += 1
    # db.session.commit()
    return redirect(f'/account_public/{review.reviewed_user_id}')

def save_account_pic(form_picture):
    random_hex = generate_id()
    pic_file_name = random_hex + '.jpg'
    picture_path = os.path.join(app.root_path, 'static/img', pic_file_name)

    output_size = (400, 400)
    processed_image = Image.open(form_picture)
    processed_image.thumbnail(output_size)
    processed_image.save(picture_path)

    return random_hex


#################################
#                               #
#        Tool-Post Stuff        #
#                               #
#################################
# @app.route("/tool/<int:post_id>") # change from int to string
# def single_tool(post_id):
#     tool = Post.query.get_or_404(post_id)


#     # tool_posts = Post.query.filter_by(smth) # recomended tools to show

#     tool_posts = Post.query.filter(Post.id != tool.id).all() # temp for testing only!

# shows the information about a tool on a single page
# @app.route("/tool/<int:post_id>") # change from int to string
# def single_tool(post_id):
@app.route("/tool/<string:tool_id>")
def single_tool(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    current_tool_swap = False
    message_thread_id = ''
    # current_tool_swap = ToolSwap.query.filter(ToolSwap.tool_id == tool_id and ToolSwap.borrower_id == current_user.id ).first() # add more to this to check if the user has non active tool swaps
    if current_user.is_authenticated:
        current_tool_swap2 = ToolSwap.query.filter(ToolSwap.tool_id == tool_id, ToolSwap.borrower_id == current_user.id ).first() 
        # add more to this to check if the user has no active tool swaps
        if current_tool_swap2:
            current_tool_swap = True
            message_thread_id = (MessageThread.query.filter_by(tool_swap_id = current_tool_swap2.id).first()).id

    # tool_posts = Tool.query.filter_by(smth) # recomended tools to show at bottom of page
    
    # shows all tools that are not a draft and are not the current tool being viewed
    tools = Tool.query.filter(Tool.id != tool_id, Tool.is_draft == False).limit(3).all() # temp for testing only!
    
    return render_template(
        'tool/tool_single_page.html',
        title = f'Tool: { tool.title.capitalize() }',
        tool = tool,
        tool_posts = tools, # tool_posts
        tool_id = tool.id,
        current_tool_swap = current_tool_swap,
        message_thread_id = message_thread_id
    )

# shows a list of all relevant tools
@app.route("/tools") # change from int to string
def all_tools():
    page = request.args.get('page', 1, type=int)
    #pagination for all posts exept for draft posts
    tool_posts = Tool.query.filter(Tool.is_draft == False).order_by(Tool.listed_date.desc()).paginate(page=page, per_page=3)
    return render_template(
        'tool/tool_all.html',
        tool_posts = tool_posts
    )

# how to add a new tool
# @app.route("/post/new", methods=['GET', 'POST'])
@app.route("/tool/new", methods=['GET', 'POST'])
@login_required
def new_tool():
    if not not_admin(False): return redirect(url_for('index'))
    
    # form = PostForm()
    # if form.validate_on_submit():
    #     post = Post(
    #         Tool_name=form.Tool_name.data.lower(),
    #         Tool_description=form.Tool_description.data,
    #         author=current_user
    conditions = ToolCondition.query.all()
    statuses = ToolStatus.query.all()
    form = ToolForm()
    if form.validate_on_submit() and request.method == "POST":
        feature_image = save_account_pic(form.feature_image.data) if form.feature_image.data else ''
        image_1 = ''
        image_2 = ''
        image_3 = ''
        image_4 = ''

        tool = Tool(
            id = generate_id(),
            title = form.title.data.lower(),
            deposit = int(form.value.data * 10),
            description = form.description.data,
            lend_duration = int(form.lend_duration.data),
            is_draft = form.is_draft.data,
            author = current_user,
            condition_id = request.form.get('condition'),
            status_id = request.form.get('status'),
            feature_image = feature_image,
            image_1 = image_1,
            image_2 = image_2,
            image_3 = image_3,
            image_4 = image_4

        )

        db.session.add(tool)
        db.session.commit()

        flash('Your Tool has been posted')
        return redirect(url_for('single_tool', tool_id = tool.id))
        # return redirect(url_for('single_tool', post_id)) # for when tool id is a random generated string
    return render_template(
        'tool/tool_create.html',
        Tool_name = 'New Post', 
        form = form, 
        legend = 'Post Tool',
        tool_id = 0, # to be changed
        conditions = conditions,
        statuses = statuses,
        form_cols = 50,
        form_rows = 5,
        update_type = 'new'
    )

# # @app.route("/post/edit/<int:post_id>") # change from int to string
# @app.route("/tool/edit/<string:tool_id>", methods=['GET', 'POST'])
# @login_required
# def edit_tool(tool_id):
#     # post = Post.query.get_or_404(tool_id)
#     tool = Tool.query.get_or_404(tool_id)
#     return render_template(
#         'tool/tool_post.html', 
#         title = tool.Tool_name.capitalize(), 
#         tool = tool,
#         post_id = tool_id
#     )


# how to edit/updtae a specific tool
@app.route("/tool/<string:tool_id>/update", methods=['GET', 'POST'])
@login_required
def update_tool(tool_id):
    tool = Tool.query.get_or_404(tool_id)

    if tool.author != current_user: abort(403)
    
    conditions = ToolCondition.query.all()
    statuses = ToolStatus.query.all()

    form = ToolForm()

    if form.validate_on_submit() and request.method == "POST":
        if form.feature_image.data: tool.feature_image = save_account_pic(form.feature_image.data)

        # print(int(form.value.data*10))
        # print(form.is_draft.data)
        # tool.Tool_name = form.Tool_name.data
        # tool.Tool_description = form.description.data
        tool.title = form.title.data.lower()
        tool.deposit = int(form.value.data*10) #int((form.value.data * 100) * 0.1),
        tool.description = form.description.data
        # print(form.description.data)
        tool.lend_duration = int(form.lend_duration.data)
        tool.is_draft = 1 if form.is_draft.data == True else 0
        tool.condition_id = request.form.get('condition')
        tool.status_id = request.form.get('status')
        db.session.commit()

        flash('Your Tool has been updated.')
        return redirect(url_for('single_tool', tool_id = tool_id))

    elif request.method == 'GET':
        form.title.data = tool.title
        form.description.data = tool.description
        form.value.data = int(tool.deposit * 0.1)
        form.lend_duration.data = tool.lend_duration
        form.is_draft.data = tool.is_draft

    return render_template(
        # 'tool/tool_create.html',
        # Tool_name='Update Post',
        # form=form,
        # post_id=post_id,
        # legend='Update Tool'
        'tool/tool_update.html', 
        Tool_name = 'Update Post', 
        form = form,
        tool = tool,
        tool_id = tool_id,
        legend = 'Update Tool',
        condition_preset = tool.condition_id,
        status_preset = tool.status_id,
        conditions = conditions,
        statuses = statuses,
        form_cols = 50,
        form_rows = 5,
        update_type = 'edit'
    )

# @app.route("/post/new/<int:tool_id>/delete", methods = ['POST'])  # change from int to string
@app.route("/tool/<int:tool_id>/delete", methods = ['POST'])  # change from int to string
@login_required
def delete_tool(tool_id):
    tool = Tool.query.get_or_404(tool_id)

    if tool.author != current_user: abort(403)

    db.session.delete(tool)
    db.session.commit()

    flash('Your Tool has been deleted')
    return redirect(url_for('index'))

# @app.route("/order/<string:tool_id>", methods=['GET', 'POST'])
# @login_required
# def order(tool_id):
#     pass



#################################
#                               #
#         Tool-Swap Stuff       #
#                               #
#################################
@app.route("/order/<string:tool_id>", methods=['GET', 'POST'])
@login_required
def create_tool_swap(tool_id):
    if not not_admin(False): return redirect(url_for('index'))
    tool = Tool.query.get_or_404(tool_id)

    # needs to create a tool swap entry
    swap_id = generate_id()

    tool_swap = ToolSwap(
        id = swap_id,
        deposit = tool.deposit,
        lender_id = tool.user_id,
        borrower_id = current_user.id,
        borrowed_tool_condition_id = tool.condition_id,
        borrowed_tool_status_id = tool.status_id,
        tool_id = tool_id
    )

    db.session.add(tool_swap)
    db.session.commit()
    # flash('Account Created - You can now Login in')
    
    thread_id = generate_id()

    message_thread = MessageThread(
        id = thread_id,
        # lender_id = tool.user_id,
        # borrower_id = current_user,
        tool_swap_id = swap_id
    )

    db.session.add(message_thread)
    db.session.commit()
    flash('tool swap process started')
    # return redirect(url_for('index'))
    return redirect(url_for('message', thread_id = thread_id))


@app.route("/confirm_date/<string:thread_id>", methods=['GET', 'POST'])
@login_required
def confirm_tool_swap(thread_id):
    thread = MessageThread.query.filter_by(id = thread_id).first()
    tool_swap = ToolSwap.query.filter_by(id = thread.tool_swap_id).first()
    
    if current_user.id != tool_swap.lender.id:
        print(current_user.id)
        print(tool_swap.lender.id)
        flash('you can\'t access that')
        return redirect(url_for('account'))

    form = ReturnDateForm()
    if form.validate_on_submit() and request.method == "POST":
        

        tool_swap.return_date = form.date.data

        db.session.commit()
        flash('Date Confirmed')
        return redirect(url_for('message', thread_id = thread_id))
    return render_template(
        'deposit/confirm_date.html',
        title = 'Message',
        form = form,
        tool_swap = tool_swap
    )

@app.route("/pay_deposit/<string:tool_id>", methods=['GET', 'POST'])
@login_required
def pay_deposit(tool_id):

    tool_swap = ToolSwap.query.get_or_404(tool_id)

    if tool_swap.deposit < current_user.balance:
        print('here')
        current_user.balance -= tool_swap.deposit
        tool_swap.is_paid += 1
        
        db.session.commit()

        flash('Deposit Paid')
    else:
        flash('Not enough funds')
        return redirect(url_for('add_funds'))

    return redirect(url_for('account'))

@app.route("/message/<string:thread_id>", methods=['GET', 'POST'])
@login_required
def message(thread_id):
    message_thread = MessageThread.query.get_or_404(thread_id)

    if not_admin(False):
        if not (current_user.id == message_thread.tool_swap.lender_id or current_user.id == message_thread.tool_swap.borrower_id):
            # flash('You do not have permission to access that')
            # return redirect(url_for('page_not_found', e=404))
            abort(404)

    the_tool_swap = ToolSwap.query.filter_by(id = message_thread.tool_swap_id).first()

    messages = Message.query.filter(Message.message_thread_id == thread_id).order_by(Message.date_sent).all()

    form = MessageForm()
    if form.validate_on_submit() and request.method == "POST":
        
        message = Message(
            id = generate_id(),
            message = form.message.data,
            sender_id = current_user.id,
            message_thread_id = thread_id
        )

        db.session.add(message)
        
        message_thread.message_count += 1

        db.session.commit()
        flash('message sent')
        return redirect(url_for('message', thread_id = thread_id))
    return render_template(
        'message/message_thread.html',
        title='Message',
        form=form,
        messages = messages,
        the_tool_swap = the_tool_swap,
        thread_id = thread_id
    )

@app.route("/return/<string:swap_id>", methods=['GET', 'POST'])
@login_required
def return_tool(swap_id):
    tool_swap = ToolSwap.query.filter_by(id = swap_id).first()

    if tool_swap.lender == current_user: 
        flash('you can\'t do that')
        return redirect(url_for('account'))
    conditions = ToolCondition.query.all()
    statuses = ToolStatus.query.all()

    form = ReturnToolForm()
    if form.validate_on_submit() and request.method == "POST":
        if form.image.data:
            form_picture = save_account_pic(form.image.data)
            tool_swap.return_photo = form_picture

        tool_swap.returned_tool_condition_id = request.form.get('condition')
        tool_swap.returned_tool_status_id = request.form.get('status')
        current_user.balance += tool_swap.deposit

        message = MessageThread.query.filter(MessageThread.tool_swap_id == swap_id).first()
        print(message.id)
        message.is_active = 0

        db.session.commit()

        flash('Tool Return in pregress')
        return redirect(url_for('account'))

    return render_template(
        'deposit/return_tool.html', 
        Tool_name = 'Return Tool', 
        form = form,
        tool_swap = tool_swap,
        legend = 'Return Tool',
        condition_preset = tool_swap.borrowed_tool_condition_id,
        status_preset = tool_swap.borrowed_tool_status_id,
        conditions = conditions,
        statuses = statuses,
        form_cols = 50,
        form_rows = 5
    )


#################################
#                               #
#         Deposit Stuff         #
#                               #
#################################
@app.route("/add_funds", methods=['GET', 'POST'])
@login_required
def add_funds():
    if not not_admin(False): return redirect(url_for('index'))
    
    form = AddFundsForm()

    if form.validate_on_submit():
        # print(form.ammount.data)
        if (
            form.card_name.data.lower() == current_user.displayname.lower()
            and form.card_num.data == 1234123412341234
            and form.card_cvv.data == 123
            and str(form.expire_date.data) == '2022-05-07'
        ):
            current_user.balance += (int(form.ammount.data) * 100)
            
            db.session.commit()
            flash('Funds added')
            # print('complete')
            return redirect(url_for('account'))
        else:
            flash('Card details are not valid')
            return redirect(url_for('add_funds'))


    return render_template(
        'deposit/deposit_add_funds.html',
        title='Add Funds',
        form = form,
        legend = 'Add Funds'
    )


#################################
#                               #
#     Tool-Search Stuff         #
#                               #
#################################

# #######  --> to be updated
# @app.route('/search', methods=['POST'])
# def search():
#     form = SearchForm()
#     posts = Post.query
#     if form.validate_on_submit():
#         post.searched = form.searched.data
#         posts = posts.filter(Post.Tool_name.like('%' + post.searched + '%'))
#         posts = posts.order_by(Post.Tool_name).all()
#         return render_template('tool/search.html', form=form, searched=post.searched, posts = posts)

#######  --> to be updated
# @app.route('/search', methods=['POST'])
# def search():
#     form = SearchForm()
#     posts = Tool.query
#     if form.validate_on_submit():
#         searched = form.searched.data.lower()
#         posts = posts.filter(Tool.title.like('%' + searched + '%'))
#         posts = posts.order_by(Tool.title).all()
#         return render_template(
#             'tool/search.html', 
#             form = form, 
#             searched = searched, 
#             posts = posts
#         )
#     else:
#         return redirect(url_for('all_tools'))

#######  --> to be updated
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data.lower()
        # posts = posts.filter(Tool.title.like('%' + searched + '%'))
        tools = Tool.query.filter(Tool.is_draft == False).all()
        posts = []
        for tool in tools:
            if SequenceMatcher(None, searched, tool.title.lower()).ratio() > 0.7:
                posts.append(tool)

        # posts = posts.order_by(Tool.title).all()
        return render_template(
            'tool/search.html', 
            form = form, 
            searched = searched, 
            posts = posts
        )
    else:
        return redirect(url_for('all_tools'))

@app.route("/deposit/<string:tool_id>", methods=['GET', 'POST'])
@login_required
def deposit():
    pass


#################################
#                               #
#           Admin Stuff         #
#                               #
#################################
def not_admin(show_flash = True, message = 'You do not have permission to access that'):
    if current_user.user_role_id == 2: return False # Admin role
    if show_flash: flash(message)
    return True


@app.route("/admin")
@login_required
def admin():
    if not_admin(): return redirect(url_for('index'))

    # admin_stat = AdminStat.query.filter_by(id = 1).first()
    # reviews = UserReview.query.filter_by(is_inappropriate = False).order_by(UserReview.date.desc()).limit(5).all()
    # messages = HelpRequest.query.filter_by(is_closed = False).order_by(HelpRequest.date.desc()).limit(5).all()
    # num_of_users = admin_stat.user_count
    # num_of_active_tools = admin_stat.tool_count
    # num_of_loan_tools = admin_stat.tool_loan_count
    # num_of_pending_messages = admin_stat.pending_message_count

    return render_template(
        'admin/admin_home.html',
        title = 'Admin Dashboard' #,
        # admin_stat = admin_stat,
        # reviews = reviews,
        # messages = messages
    )

@app.route("/admin/user-roles")
@login_required
def admin_user_roles():
    if not_admin(): return redirect(url_for('index'))

    list_display = User.query.filter(User.id != current_user.id).join(UserRole).all()
    return render_template(
        'admin/admin_user_roles.html',
        title='Admin Dashboard - Roles',
        list_display=list_display
    )

@app.route("/admin/user-roles/edit/<string:user_id>", methods = ['GET', 'POST'])
@login_required
def admin_edit_user_role(user_id):
    if not_admin(): return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    roles = UserRole.query.all()
    current_role = str(user.user_role_id)

    if request.method == "POST":
        new_role = request.form.get('role')
        if not current_role == new_role:
            user.user_role_id = new_role
            db.session.commit()

            flash(user.displayname + "'s Role was updated")

        return redirect(url_for('admin_user_roles'))

    list_display = db.session.query(User).join(UserRole).all()
    return render_template(
        'admin/admin_user_roles_edit.html',
        title = 'Admin Dashboard - Edit Roles',
        roles = roles,
        current_role = current_role,
        user = user
    )

# @app.route("/admin/help-forms")
# @login_required
# def admin_messages():
#     if not_admin(): return redirect(url_for('index'))

#     messages = HelpRequest.query.filter_by(answered = False)

#     return render_template(
#         'admin/admin_messages.html',
#         title='Admin Dashboard - Messages',
#         messages=messages
#     )

# @app.route("/admin/help-forms/<string:help_form_id>", methods=['GET', 'POST'])
# @login_required
# def admin_view_message(help_form_id):
#     if not_admin(): return redirect(url_for('index'))

#     message = HelpRequest.query.get_or_404(help_form_id)
#     tool_swap = ToolSwap.query.filter_by(id = message.tool_swap_id).first()
#     user = User.query.filter_by(id = message.user_id).first()

#     form = HelpRequestReplyFrom()
#     gen_id = generate_id()
#     if form.validate_on_submit():
#         reply_form = HelpRequest(
#             id = gen_id,
#             title = f"RE: { str(message.title) }",
#             message = form.message.data,
#             reply_message_id = True, # might not be needed
#             user_id = current_user.id,
#             tool_swap_id = tool_swap.id,
#             # for_admin = False -> set automatically
#             # seen = False -> set automatically
#             # date = date -> set automatically
#             parent_message = help_form_id # ? this should be the last message in the thread not the first request
#         )
#         db.session.add(reply_form)
#         db.session.commit()
#         flash('Your account was updated')

#         return redirect(url_for('admin_view_message', 'help_form_id'))

#     return render_template(
#         'admin/admin_home.html',
#         title='Admin Dashboard',eate.html',
        # Tool_name='Update Post',
        # form=form,
        # post_id=post_id,
        # legend='Update Tool'
        # 'too
#         user = user
#     )

# @app.route("/admin/money")
# @login_required
# def admin_money():
#     if not_admin(): return redirect(url_for('index'))

#     return render_template(
#         'admin/admin_home.html',
#         title = 'Admin Dashboard'
#     )

# @app.route("/admin/recent-reviews")
# @login_required
# def admin_recent_reviews():
#     if not_admin(): return redirect(url_for('index'))

#     return render_template(
#         'admin/admin_home.html',
#         title = 'Admin Dashboard'
#     )
