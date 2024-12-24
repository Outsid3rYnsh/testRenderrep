from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies

app = Flask(__name__)

# PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change to a secure key

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='author', cascade="all, delete-orphan")

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

# Create tables when the app starts
with app.app_context():
    db.create_all()

# Routes
# 1. Insert models
@app.route('/authors', methods=['POST'])
@jwt_required()
def add_author():
    data = request.get_json()
    new_author = Author(name=data['name'])
    db.session.add(new_author)
    db.session.commit()
    return jsonify({'message': 'Author added successfully', 'author': {'id': new_author.id, 'name': new_author.name}})

@app.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    data = request.get_json()
    new_book = Book(title=data['title'], author_id=data['author_id'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully', 'book': {'id': new_book.id, 'title': new_book.title}})

# 2. Get models by ID
@app.route('/authors/<int:id>', methods=['GET'])
@jwt_required()
def get_author(id):
    author = Author.query.get_or_404(id)
    return jsonify({'id': author.id, 'name': author.name, 'books': [{'id': book.id, 'title': book.title} for book in author.books]})

# 3. Update models
@app.route('/authors/<int:id>', methods=['PUT'])
@jwt_required()
def update_author(id):
    data = request.get_json()
    author = Author.query.get_or_404(id)
    author.name = data.get('name', author.name)
    db.session.commit()
    return jsonify({'message': 'Author updated successfully', 'author': {'id': author.id, 'name': author.name}})

# 4. Retrieve all models
@app.route('/authors', methods=['GET'])
@jwt_required()
def get_all_authors():
    authors = Author.query.all()
    return jsonify([{'id': author.id, 'name': author.name} for author in authors])

# 5. Delete models
@app.route('/authors/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_author(id):
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    return jsonify({'message': 'Author deleted successfully'})

# 6. Delete models with relationships (handled via cascade)
@app.route('/books/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

# 7. Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    if username == 'test' and password == 'test':  # Replace with real user validation
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    return jsonify({'message': 'Invalid credentials'}), 401

# 8. Logout endpoint
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({'message': 'Successfully logged out'})
    unset_jwt_cookies(response)
    return response

if __name__ == '__main__':
    app.run(debug=True)
