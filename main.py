from flask import Flask, request, redirect, render_template, url_for, session
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlencode
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    completed = db.Column(db.Boolean)
    #owner_id = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user_id):
        self.owner_id = user_id
        self.body = body
        self.title = title
        self.completed = False
        #self.owner = owner
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(50))
    #user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    #blogs = db.Column(db.Integer)
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
   
    
    @app.before_request
    def require_login():
        allowed_routes = ['login', 'signup', 'index', 'allpost', 'blog']
        if request.endpoint not in allowed_routes and 'username' not in session:
            return redirect('/login')
    
    # login function
    @app.route('/login', methods=['POST', 'GET'])
    def login():
        login_error=None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            new_user = User(username, password)
            #db.session.add(new_user)
            #db.session.commit()

            user_datas = User.query.filter_by(username = new_user.username).first()
            #user_datas = User.query.filter_by(username = new_user.username).all()
            
            if user_datas != None:
                #username_db = User.query.filter_by(username=username).first()
                #password_db = User.query.filter_by(password=password).first()
                username_db = user_datas.username
                password_db = user_datas.password
                user_side_username = username
                user_side_password = password
                user_name_error=False
                login_error=None
                #return '<h>DB error</h1>'
                #return render_template('login.html', var=username_db, var1=password_db)
                if (password_db == user_side_password) and (username_db == user_side_username):
                    session['username'] = user_side_username
                    session['userid'] = user_datas.id
                    return redirect(url_for('new_blog'))
                else:
                    if (password_db != user_side_password):
                        login_error='Invalid password'
                    else:
                        login_error = 'Invalid User'
                    return render_template('login.html', login_error=login_error)
            else:
                return render_template('login.html',login_error='Invalid User')
        if request.method == 'GET':
            #return '<h1>login error</h1>'
            return render_template('login.html', login_error=login_error)


    # new usersignup
    @app.route('/signup', methods=['POST', 'GET'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            verify_password = request.form['ver_pwd']
            

            #new_user = User(username, password)
            #validate all 
            error_text = validate_user_signup(username, password, verify_password)
            if error_text == None:
                existing_user = User.query.filter_by(username=username).first()
                if not existing_user:
                    new_user = User(username, password)
                    db.session.add(new_user)
                    db.session.commit()
                    session['username'] = username
                    return redirect(url_for('new_blog'))
                else:
                    return render_template('signup.html',error = 'Username exist')

            return render_template('signup.html',error = error_text)

        if request.method == 'GET':
            return render_template('signup.html')
#step1     
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        users = User.query.all()
        return render_template('users.html', users=users)

    # @app.route('/', methods=['POST', 'GET'])
    # def index():
    #     title_name = "" 
    #     if request.method == 'POST':
    #         title_name = request.form['title']
    #         blog_content = request.form['blog-content']
                
    #         new_blog = Blog(title_name, blog_content)
    #         db.session.add(new_blog )
    #         db.session.commit()

    #         tasks = Blog.query.filter_by(completed=False).all()
    #             #completed_tasks = Blog.query.filter_by(completed=True).all()
    #         return render_template('allpost.html', tasks=tasks)

    #     if request.method == 'GET':
    #         tasks = Blog.query.filter_by(completed=False).all()
    #             #completed_tasks = Blog.query.filter_by(completed=True).all()
    #         return render_template('allpost.html', tasks=tasks)

#add new post function
@app.route('/new_post', methods=['POST', 'GET'])
def new_blog():
    title_name = "" 
    title_name = cgi.escape(title_name, quote=True)
    add_error=""
    add_error = cgi.escape(add_error, quote=True)
    blog_content=""
    blog_content = cgi.escape(blog_content, quote=True) 
    if request.method == 'POST':
        title_name = request.form['title']
        blog_content = request.form['blog-content']
        if title_name and blog_content:
            new_blog = Blog(title_name, blog_content, session['userid'])
            db.session.add(new_blog)
            db.session.commit()

            tasks = Blog.query.filter_by(completed=False).all()
            #completed_tasks = Blog.query.filter_by(completed=True).all()
                    #return render_template('allpost.html', tasks=tasks)
            obj = Blog.query.order_by(Blog.id.desc()).first()
        
            most_recent_idx=obj.id
            return redirect(url_for('blog',id=most_recent_idx))
        else:
            if(title_name):
                add_error = 'Body cannot be blank'
            else:
                add_error = 'Title cannot be blank'
            return render_template('new_post.html', title=request.form['title'], blog=request.form['blog-content'], error=add_error)
    
    if request.method == 'GET':
        
        #completed_tasks = Blog.query.filter_by(completed=True).all()
        return render_template('new_post.html')

#step2(gets username/user id from the link)    
@app.route('/blog')
def blog():
    #handles username part
    username = request.args.get('username')
    if username != None:
        user_tasks = User.query.filter_by(username = username).first()
        user_id = user_tasks.id
        tasks = Blog.query.filter_by(owner_id = user_id).all()
        
        #completed_tasks = Blog.query.filter_by(completed=True).all()
        return render_template('/userbloglist.html', tasks=tasks, username =username)  
    
    #handles id part
    blog_id = request.args.get('id')
    tasks = Blog.query.filter_by(id = blog_id).all()
    users = User.query.all()
    #return '404 - hI Template not found'
    #url_text = urlencode("/blogcontent.html?blogid=")
    return render_template('/blogcontent.html', tasks=tasks, users=users)

#step3 Displays all post by all users
@app.route('/allpost', methods=['GET', 'POST'])
def allpost():
    if request.method == 'GET':
        tasks = Blog.query.filter_by(completed=False).all()
        users = User.query.all()
        return render_template('/allpost.html', tasks=tasks, users=users)
#-------------------------------------------------------------------

#logout function
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/allpost')

#helper functions
def validate_user_signup(username, password, verify_password):
    username_error = validate_username(username)
    password_error = validate_password(password)
    pwd_mismatch_error = password_mismatch(password, verify_password)

#donno how to proceed after this.
#errors = {'username_error': username_error,'password_error': password_error, 'pwd_mismatch_error': pwd_mismatch_error,'email_error': email_error}
    if username_error:
        return username_error
    elif password_error:
         return password_error
    elif pwd_mismatch_error:
         return pwd_mismatch_error
    else:
        None



def validate_username(username):
    len_username = len(username)
    if space_in_text(username):
        username_space_error = "Please select a username without space."
        error = username_space_error
    #error = True?
        return error
    if is_left_blank(username):
        username_blank_error ="Please donot leave this field blank."
        error = username_blank_error
    #error = True
        return error
    if check_str_length(len_username):
        min_str_length_error = "Please choose a username with length >3 and <20."
        error = min_str_length_error
        return error

    return None

def validate_password(password):
    
    len_of_password = len(password)
    
    if check_str_length(len_of_password):
        password_len_error = "Please choose a password with length >3 and <20."
        error = password_len_error
        #error = True
        return error
    
    if is_left_blank(password):
        password_blank_error ="Please donot leave this field blank."
        error = password_blank_error
        #error = True
        return error
    return None

def password_mismatch(password,verify_password ):
    if not ( sorted(list(password)) == sorted(list(verify_password)) ):
        verify_mismatch_error ="Typed passwords donot match. Please try again."
        error = verify_mismatch_error
        return error
    
    if is_left_blank(verify_password):
        verify_blank_error ="Please donot leave this field blank."
        error = verify_blank_error
        return error
    return None


#helper functions

def is_left_blank(text):
    if not text:
        return True;
    else:
        return False;


def space_in_text(text):
    if " " in text:
        return True;
    else:
        return False;
    

def check_str_length(length):
    if (length <3) or (length > 20):
        return True;
    else:
        return False;

  


if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run() 