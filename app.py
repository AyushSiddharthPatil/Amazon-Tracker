from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# DataBase Creation

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///amazon.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Amazon(db.Model):
    email = db.Column(db.String, primary_key=True, nullable=False)
    url = db.Column(db.String(5000), nullable=False)
    title = db.Column(db.String(500))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.email} - {self.title}"


def create_tables():
    db.create_all()


    if 
@app.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email = request.form['email']
        url = request.form['url']
        print(f"Received email: {email}, url: {url}")
        existing = Amazon.query.get(email)
        if not existing:
            new_entry = Amazon(email=email, url=url)
            db.session.add(new_entry)
            db.session.commit()
        return redirect('/home')

    all_products = Amazon.query.all()
    print(all_products)
    return render_template("index.html", all_products=all_products)


# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     pass

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
