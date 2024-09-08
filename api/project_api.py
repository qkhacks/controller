from flask import Flask
from lib.project import ProjectService
from .utils import *


class ProjectApi:
    def __init__(self, app: Flask, project_service: ProjectService):
        self.app = app
        self.project_service = project_service

    def register(self):
        @self.app.post("/api/v1/projects")
        @authenticate_user
        def create_project(user):
            check_admin(user)
            return self.project_service.create(
                required_param("name"),
                user["id"],
                user["organization_id"]
            )

        @self.app.get("/api/v1/projects")
        @authenticate_user
        def fetch_projects(user):
            return self.project_service.fetch(
                user["id"],
                page(),
                size()
            )

        @self.app.get("/api/v1/projects/<project_id>")
        @authenticate_user
        def get_project(user, project_id):
            return self.project_service.get(project_id, user["id"])

        @self.app.put("/api/v1/projects/<project_id>")
        @authenticate_user
        def update_project(user, project_id):
            return self.project_service.update(
                project_id,
                optional_param("name"),
                user["id"],
                user["organization_id"]
            )

        @self.app.delete("/api/v1/projects/<project_id>")
        @authenticate_user
        def delete_project(user, project_id):
            return self.project_service.delete(project_id, user["id"])

        @self.app.post("/api/v1/projects/<project_id>/users/<user_id>/access")
        @authenticate_user
        def add_project_access(user, project_id, user_id):
            return self.project_service.add_access(
                project_id,
                user_id,
                required_param("permissions", list),
                user["id"],
                user["organization_id"]
            )

        @self.app.delete("/api/v1/projects/<project_id>/users/<user_id>/access")
        @authenticate_user
        def delete_project_access(user, project_id, user_id):
            return self.project_service.delete_access(
                project_id,
                user_id,
                required_param("permissions", list),
                user["id"],
            )

        @self.app.delete("/api/v1/projects/<project_id>/users/<user_id>")
        @authenticate_user
        def delete_all_project_access(user, project_id, user_id):
            return self.project_service.delete_all_access(
                project_id,
                user_id,
                user["id"]
            )

        @self.app.get("/api/v1/projects/<project_id>/users")
        @authenticate_user
        def fetch_project_users(user, project_id):
            return self.project_service.fetch_users(
                project_id,
                user["id"],
                page(),
                size()
            )
