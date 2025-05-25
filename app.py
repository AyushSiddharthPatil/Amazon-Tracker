import pytz
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
from main import GetPrice, SendEmail
from apscheduler.schedulers.background import BackgroundScheduler


def indian_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz)


def check_prices():
    with app.app_context():
        print("Running Scheduler price checks...")
        price_checker = GetPrice()
        email_sender = SendEmail()
        products = Amazon.query.filter_by(notified=False).all()
        for product in products:
            try:
                current_price = price_checker.get_price(product.url)
                current_price = float(current_price.replace(",", ""))

                if current_price <= product.target:
                    email_sender.send_email(product.email)
                    product.notified = True
                    db.session.commit()
                    print(f"Email Sent to {product.email} for {product.title}")
            except Exception as e:
                print(f"Error checking price for {product.title}: {e}")


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
    date_created = db.Column(db.DateTime, default=indian_time)
    notified = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"{self.email} - {self.title}"


def create_tables():
    db.create_all()


@app.route("/", methods=['GET', 'POST'])
def home():
    title = None
    message = None
    if request.method == 'POST':
        email = request.form['email']
        url = request.form['url']
        target = request.form['target']

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        price_checker = GetPrice()
        try:
            price, title = price_checker.get_price(url)
        except Exception as e:
            print("The title didn't fetched", e)
            title = "N/A"

        print(f"Received email: {email}, url: {url}, title: {title}, Target_Price = {target}")
        existing = Amazon.query.get(email)
        message = None
        if target:
            try:
                target = int(target)
                if float(price.replace(",", "")) <= target:
                    message = f"📈 Price ₹{price} is still above your target ₹{target}"

                    send_email = SendEmail()
                    send_email.send_email(email)

                else:
                    message = f"📈 Price ₹{price} is still above your target ₹{target}"

            except Exception as target_price_exception:
                message = f"⚠️ Invalid price format or conversion issue: {target_price_exception}"

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

scheduler = BackgroundScheduler()
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        scheduler = BackgroundScheduler()
        scheduler.add_job(check_prices, 'interval', hours=1)
        scheduler.start()

    app.run(debug=True, port=8000)
