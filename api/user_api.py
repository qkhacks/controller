from flask import Flask

from api.utils import *
from lib.identity import UserService


class UserApi:
    def __init__(self, app: Flask, user_service: UserService):
        self.app = app
        self.user_service = user_service

    def register(self):

        @self.app.post("/api/v1/users/signup")
        def signup_user():
            return self.user_service.sign_up(
                required_param("username"),
                required_param("password"),
                required_param("organization_name"),
            )

        @self.app.post("/api/v1/users/token")
        def get_user_token():
            return self.user_service.get_token(
                required_param("username"),
                required_param("password"),
                required_param("organization_name"),
            )

        @self.app.get("/api/v1/users/me")
        @authenticate_user
        def get_user(user):
            return self.user_service.get(user["id"])

        @self.app.put("/api/v1/users/me/password")
        @authenticate_user
        def change_user_password(user):
            return self.user_service.change_password(user["id"], required_param("password"))

        @self.app.post("/api/v1/users")
        @authenticate_user
        def add_user(user):
            check_admin(user)
            return self.user_service.add(
                required_param("username"),
                required_param("admin", bool),
                user["id"],
                user["organization_id"],
            )

        @self.app.get("/api/v1/users")
        @authenticate_user
        def fetch_users(user):
            return self.user_service.fetch(user["organization_id"], page(), size())

        @self.app.get("/api/v1/users/<user_id>")
        @authenticate_user
        def get_organization_user(user, user_id):
            return self.user_service.get_by_organization(user_id, user["organization_id"])

        @self.app.put("/api/v1/users/<user_id>/password")
        @authenticate_user
        def reset_user_password(user, user_id):
            check_admin(user)
            return self.user_service.reset_password(user_id, user["organization_id"])

        @self.app.put("/api/v1/users/<user_id>/admin")
        @authenticate_user
        def change_user_admin(user, user_id):
            check_admin(user)
            return self.user_service.change_admin(user_id, required_param("admin", bool), user["organization_id"])

        @self.app.delete("/api/v1/users/<user_id>")
        @authenticate_user
        def delete_user(user, user_id):
            check_admin(user)
            return self.user_service.delete(user_id, user["organization_id"])
