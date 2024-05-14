from flask import Flask, render_template, request, redirect, url_for, jsonify
from flasgger import Swagger, swag_from
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Todo API',
    'uiversion': 3,
    'openapi': '3.0.2'
}
swagger = Swagger(app, template=app.config['SWAGGER'])
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean) 

@app.route('/', methods=['GET'])
def index():
    todo_list = Todo.query.all()
    print(todo_list)
    return render_template('base.html', todo_list=todo_list)

@app.route('/add', methods=["POST"])
@swag_from({
    'responses': {
        302: {
            'description': 'Redirects to the main page after adding a new todo item.',
        }
    },
    'parameters': [
        {
            'name': 'title',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Title of the new todo item'
        }
    ]
})
def add():
    title = request.form.get('title')
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/update/<int:todo_id>')
@swag_from({
    'responses': {
        302: {
            'description': 'Redirects to the main page after toggling the completion status of a todo item.',
        }
    },
    'parameters': [
        {
            'name': 'todo_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the todo item to update'
        }
    ]
})
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:todo_id>')
@swag_from({
    'responses': {
        302: {
            'description': 'Redirects to the main page after deleting a todo item.',
        }
    },
    'parameters': [
        {
            'name': 'todo_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the todo item to delete'
        }
    ]
})
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # new_todo = Todo(title="Todo 1", complete=False)
        # db.session.add(new_todo)
        # db.session.commit()
    app.run(debug=True)