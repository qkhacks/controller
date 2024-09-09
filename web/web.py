from flask import Flask, render_template


class Web:
    def __init__(self, app: Flask) -> None:
        self.app = app

    def register(self):

        @self.app.get("/")
        def index():
            return render_template("index.html")

        @self.app.get("/join")
        def join():
            return render_template("join.html")

        @self.app.get("/login")
        def login():
            return render_template("login.html")

        @self.app.get("/logout")
        def logout():
            return render_template("logout.html")

        @self.app.get("/home")
        def home():
            return render_template("home.html")

        @self.app.get("/account")
        def account():
            return render_template("account.html")
