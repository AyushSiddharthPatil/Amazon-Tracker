from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from main import GetPrice, SendEmail

app = Flask(__name__)

# DataBase Creation

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///amazon.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Amazon(db.Model):
    email = db.Column(db.String, primary_key=True, nullable=False)
    url = db.Column(db.String(5000), nullable=False)
    title = db.Column(db.String(500))
    target = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.email} - {self.title}"


def create_tables():
    db.create_all()


@app.route("/home", methods=['GET', 'POST'])
def home():
    title = None
    if request.method == 'POST':
        email = request.form['email']
        url = request.form['url']
        target = request.form['target']

        if not url.startswith("http: //") and not url.startswith("https://"):
            url = "https://" + url

        price_checker = GetPrice()
        try:
            price, title = price_checker.get_price(url)
        except Exception as e:
            print("The title didn't fetched", e)
            title = "N/A"

        print(f"Received email: {email}, url: {url}, title: {title}, Target_Price = {target}")
        existing = Amazon.query.get(email)

        if target:
            try:
                target = int(target)
                if float(price.replace(",", "")) <= target:
                    message = f"🎯 Target Price Hit! Price = ₹{price}, Title: {title}"
                    send_email = SendEmail()
                    email = send_email.send_email(email)
                else:
                    message = f"📈 Price ₹{price} is still above your target ₹{target}"

            except Exception as target_price_exception:
                message = f"⚠️ Invalid price format or conversion issue: {target_price_exception}"

            redirect("/home")
        if not existing:
            new_entry = Amazon(email=email, url=url, title=title, target=target)
            db.session.add(new_entry)
            db.session.commit()

    all_products = Amazon.query.all()
    # print(all_products)
    return render_template("index.html", all_products=all_products, title=title, message=message)


# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     pass

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
