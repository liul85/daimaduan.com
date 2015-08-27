#-*-encoding:utf-8-*-
from bootstrap import app
from bottle import run, request, redirect, abort
from bottle import jinja2_view
from bottle import static_file

from beaker.middleware import SessionMiddleware

from models import SigninForm
from models import SignupForm
from models import CodeForm
from models import User
from models import Paste


@app.route('/')
@jinja2_view('index.html')
def index():
    return {'pastes': Code.objects()}


@app.get('/create')
@jinja2_view('create.html')
def create_get():
    return {'form': CodeForm()}


@app.post('/create')
def create():
    form = CodeForm(request.POST)
    if form.validate():
        user = User.objects(username=request.session['username']).first()
        code = Code(title=form.title.data,
                    content=form.content.data,
                    user=user)
        code.save()
    return redirect('/')


@app.route('/code/<hash_id>')
@jinja2_view('view.html')
def view(hash_id):
    code = Code.objects(hash_id=hash_id).first()
    if not code:
        abort(404)
    return {'code': code}


@app.get('/signup')
@jinja2_view('signup.html')
def signup_get():
    return {'form': SignupForm()}


@app.post('/signup')
def signup_post():
    form = SignupForm(request.POST)
    if form.validate():
        user = User()
        user.email = form.email.data
        user.username = form.username.data
        user.password = form.password.data
        user.save()
        return redirect('/signin')


@app.get('/signin')
@jinja2_view('signin.html')
def signin_get():
    return {'form': SigninForm()}


@app.post('/signin')
def signin_post():
    form = SignupForm(request.POST)
    user = User.objects(email=form.email.data).first()
    if user.generate_password(form.password.data) == user.password:
        request.session['username'] = user.username
        redirect('/')


session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 7 * 24 * 3600,
    'session.data_dir': './sessions',
    'session.auto': True
}
application = SessionMiddleware(app, session_opts)


if __name__ == '__main__':
    @app.route('/static/<filepath:path>')
    def server_static(filepath):
        return static_file(filepath, root='./static')

    run(application, host='0.0.0.0', server='paste', port=8080, reloader=True, debug=True)
