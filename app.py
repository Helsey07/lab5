from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User

app = Flask(__name__)
app.secret_key = "123"


user_db = "alexRPP"
host_ip ="127.0.0.1"
host_port = "5432"
database_name = "LAB5"
password = "1234"

# Настройка подключения к базе данных PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'

# Инициализация базы данных и менеджера авторизации
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Эндпоинт для корневой страницы
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', name=current_user.name)
    else:
        return redirect(url_for('login'))

# Эндпоинт для страницы входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Проверка заполнения полей
        if not email or not password:
            flash("Пожалуйста, заполните все поля", "error")
            return redirect(url_for('login'))

        # Поиск пользователя по email
        user = User.get_by_email(email)
        if not user:
            flash("Пользователь не найден", "error")
            return redirect(url_for('login'))

        # Проверка пароля
        if not user.check_password(password):
            flash("Неверный пароль", "error")
            return redirect(url_for('login'))

        # Авторизация пользователя
        login_user(user)
        return redirect(url_for('index'))

    return render_template('login.html')

# Эндпоинт для страницы регистрации
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Проверка заполнения полей
        if not name or not email or not password:
            flash("Пожалуйста, заполните все поля", "error")
            return redirect(url_for('signup'))

        # Проверка на существование пользователя
        if User.get_by_email(email):
            flash("Пользователь с таким email уже существует", "error")
            return redirect(url_for('signup'))

        # Создание нового пользователя
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Регистрация успешна! Войдите, используя свои данные.")
        return redirect(url_for('login'))

    return render_template('signup.html')

# Эндпоинт для выхода
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаёт таблицы в базе данных при первом запуске
    app.run(debug=True)