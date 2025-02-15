from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
with app.app_context():
    db.create_all()


# Home page - user view
@app.route('/')
@login_required
def index():
    stocks = Stock.query.all()
    return render_template('index.html', stocks=stocks)


# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Try again.', 'danger')
    return render_template('login.html')


# User logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))


# Admin - Add stock
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        new_stock = Stock(name=name, quantity=quantity)
        db.session.add(new_stock)
        db.session.commit()
        flash(f'{name} added with {quantity} units.', 'success')
    stocks = Stock.query.all()
    return render_template('admin.html', stocks=stocks)


# Admin - Update stock
@app.route('/update_stock/<int:stock_id>', methods=['POST'])
@login_required
def update_stock(stock_id):
    stock = Stock.query.get(stock_id)
    if stock:
        stock.quantity = int(request.form['quantity'])
        db.session.commit()
        flash(f'Stock for {stock.name} updated!', 'success')
    return redirect(url_for('admin'))


# Admin - Delete stock
@app.route('/delete_stock/<int:stock_id>', methods=['POST'])
@login_required
def delete_stock(stock_id):
    stock = Stock.query.get(stock_id)
    if stock:
        db.session.delete(stock)
        db.session.commit()
        flash(f'{stock.name} deleted!', 'warning')
    return redirect(url_for('admin'))


# User - Buy stock
@app.route('/buy/<int:stock_id>', methods=['POST'])
@login_required
def buy(stock_id):
    quantity = int(request.form['quantity'])
    stock = Stock.query.get(stock_id)

    if stock and stock.quantity >= quantity:
        stock.quantity -= quantity
        purchase = Purchase(user_id=current_user.id, stock_id=stock.id, quantity=quantity)
        db.session.add(purchase)
        db.session.commit()

        # Redirect to purchase summary
        return redirect(url_for('purchase_summary', purchase_id=purchase.id))
    else:
        flash('Insufficient stock!', 'danger')
        return redirect(url_for('index'))


@app.route('/purchase_summary/<int:purchase_id>')
@login_required
def purchase_summary(purchase_id):
    purchase = Purchase.query.get(purchase_id)
    stock = Stock.query.get(purchase.stock_id)
    return render_template('purchase_summary.html', stock_name=stock.name, quantity=purchase.quantity)



if __name__ == '__main__':
    app.run(debug=True)
