import requests

from bs4 import BeautifulSoup
import smtplib


class GetPrice:

    def __init__(self):
        self.price = None
        self.title = None

    def get_price(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Cookie": "PHPSESSID=664040e172239fb249086d15202ad530; _ga=GA1.2.1761659485.1747491214; _gid=GA1.2.1720096750.1747491214; _ga_VL41109FEB=GS2.2.s1747491214$o1$g0$t1747491214$j0$l0$h0",
            "Accept-Encoding": "gzip, deflate, br, zstd"}
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")

        # print(soup.prettify())

        self.price = soup.find(name="span", class_="a-price-whole").getText()
        # print(price.getText())
        self.title = soup.find(id="productTitle", ).getText()
        return self.price, self.title

    def target(self, target_price):
        if target_price is None:
            print("Price not set.")
            return
        if float(self.price.replace(',', '')) <= int(target_price):
            print(f"Target Price Hit !!!, Price = {self.price}, Title: {self.title}")
        else:
            print(f"Price {self.price} is still above your target price {target_price}")


# Sending Email
class SendEmail:

    def send_email(self, email):
        try:
            with smtplib.SMTP("smtp.gmail.com") as connection:
                my_email = "ayush.patil.new007@gmail.com"
                password = "qwnprwdmxogxnyzl"  # created with app passwords and created a new app
                connection.starttls()  # Transport Layer Security, secures our connection by encrypting our message
                connection.login(user=my_email, password=password)
                connection.sendmail(from_addr=my_email,
                                    to_addrs=email,
                                    msg="Subject:Amazon Price Alert\n\nYour product price has been tracked.")
            return True

        except Exception as e:
            print("Email error:", e)
            return False


# username = []
# password = []


# def register():
#     username.append(input("Enter your username"))
#     password.append(input("Enter your password"))


# def login():
#     username = input("Enter your username: ")
#     password = input("Enter your password: ")
#     if username in username and password in password:
#         print("Welcome")
#     else:
#         print("No user Found")
#
#
# while True:
#     acc_ans = input("Choose: a) Sign Up     b)Login     c)Quit")
#     if acc_ans == "a":
#         register()
#     elif acc_ans == "b":
#         login()
#     elif acc_ans == "c":
#         break
# connection.close() # if you don' want to write this then do above
