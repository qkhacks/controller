from flask import Flask, render_template


class Web:
    def __init__(self, app: Flask) -> None:
        self.app = app

    def register(self):

        @self.app.get("/")
        def index():
            return render_template("index.html")
    