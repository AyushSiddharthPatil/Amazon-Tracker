import pytz
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from main import GetPrice, SendEmail
from apscheduler.schedulers.background import BackgroundScheduler


def indian_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz)


app = Flask(__name__)

# Configure the SQLite database
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

    def __repr__(self):
        return f"{self.email} - {self.title}"


def check_prices():
    with app.app_context():
        print("🔄 Running scheduler price checks...")
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
                    print(f"✅ Email sent to {product.email} for {product.title}")
            except Exception as e:
                print(f"❌ Error checking price for {product.title}: {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    title = None
    message = None

    if request.method == "POST":
        email = request.form["email"]
        url = request.form["url"]
        target = request.form["target"]

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        price_checker = GetPrice()
        try:
            price, title = price_checker.get_price(url)
        except Exception as e:
            print("❌ Could not fetch product title or price:", e)
            title = "N/A"
            price = "0"

        print(f"📩 Received: {email}, URL: {url}, Title: {title}, Target: {target}")
        existing = Amazon.query.get(email)

        try:
            target = int(target)
            if float(price.replace(",", "")) <= target:
                message = f"✅ Price ₹{price} is below or equal to your target ₹{target}."
                SendEmail().send_email(email)
            else:
                message = f"📈 Price ₹{price} is still above your target ₹{target}."
        except Exception as e:
            message = f"⚠️ Invalid target price: {e}"

        if not existing:
            new_entry = Amazon(email=email, url=url, title=title, target=target)
            db.session.add(new_entry)
            db.session.commit()

    all_products = Amazon.query.all()
    return render_template("index.html", all_products=all_products, title=title, message=message)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        scheduler = BackgroundScheduler()
        scheduler.add_job(check_prices, 'interval', hours=1)
        scheduler.start()

    app.run(debug=True, port=8000)
