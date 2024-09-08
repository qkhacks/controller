from flask import Flask


def register_health_api(app: Flask):

    @app.get("/health")
    def health_check():
        return {
            "status": "ok"
        }
