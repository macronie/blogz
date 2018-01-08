from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    completed = db.Column(db.Boolean)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.completed = False

#use this part to add new blog list

@app.route('/', methods=['POST', 'GET'])
def index():
    title_name = "" 
    if request.method == 'POST':
        title_name = request.form['title']
        blog_content = request.form['blog-content']
        
        new_blog = Blog(title_name, blog_content)
        db.session.add(new_blog )
        db.session.commit()

        tasks = Blog.query.filter_by(completed=False).all()
        #completed_tasks = Blog.query.filter_by(completed=True).all()
        return render_template('blog-listing.html', tasks=tasks)

    if request.method == 'GET':
        tasks = Blog.query.filter_by(completed=False).all()
        #completed_tasks = Blog.query.filter_by(completed=True).all()
        return render_template('blog-listing.html', tasks=tasks)

@app.route('/new_blog', methods=['POST', 'GET'])
def new_blog():
    title_name = "" 
    if request.method == 'POST':
        title_name = request.form['title']
        blog_content = request.form['blog-content']
        
        new_blog = Blog(title_name, blog_content)
        db.session.add(new_blog )
        db.session.commit()

        tasks = Blog.query.filter_by(completed=False).all()
        #completed_tasks = Blog.query.filter_by(completed=True).all()
        return render_template('blog-listing.html', tasks=tasks)
    if request.method == 'GET':
        
        #completed_tasks = Blog.query.filter_by(completed=True).all()
        return render_template('new_post.html')

@app.route('/blogcontent/<int:blog_id>', methods=['GET', 'POST'])
def blogcontent(blog_id):
    #return 'User %s' % blog_id
    #blog_id = int(request.GET.get('task.id')) 
    #return '404 - Template not found'
    if request.method == 'GET':
        #blogId = blog_id#request.POST.get('val')
        #task = Blog.query.get(blog_id)
        tasks = Blog.query.filter_by(id = blog_id).all()
        #return '404 - hI Template not found'
        return render_template('/blogcontent.html', tasks=tasks)

@app.route('/blog-listing', methods=['GET', 'POST'])
def bloglisting():
    return redirect('/blog-listing')

@app.route('/bloglistinglink', methods=['GET', 'POST'])
def bloglistinglink():
    tasks = Blog.query.filter_by(completed=False).all()
    return render_template('/blog-listing.html', tasks=tasks)


# @app.route('/delete-task', methods=['POST'])
# def delete_task():

#     task_id = int(request.form['task-id'])
#     task = Task.query.get(task_id)
#     task.completed = True
#     db.session.add(task)
#     db.session.commit()

#     return redirect('/')

if __name__ == '__main__':
    app.run() 