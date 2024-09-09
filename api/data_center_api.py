from flask import Flask

from lib.infra import DataCenterService
from .utils import *


class DataCenterApi:

    def __init__(self, app: Flask, data_center_service: DataCenterService) -> None:
        self.app = app
        self.data_center_service = data_center_service

    def register(self):
        @self.app.post("/api/v1/projects/<project_id>/infra/data-centers")
        @authenticate_user
        def create_data_center(user, project_id):
            return self.data_center_service.create(
                required_param("name"),
                optional_param("description"),
                project_id,
                user["id"],
                user["organization_id"],
            )

        @self.app.get("/api/v1/projects/<project_id>/infra/data-centers")
        @authenticate_user
        def fetch_data_centers(user, project_id):
            return self.data_center_service.fetch(project_id, user["id"], page(), size())

        @self.app.get("/api/v1/projects/<project_id>/infra/data-centers/<data_center_id>")
        @authenticate_user
        def get_data_center(user, project_id, data_center_id):
            return self.data_center_service.get(data_center_id, project_id, user["id"])

        @self.app.put("/api/v1/projects/<project_id>/infra/data-centers/<data_center_id>")
        @authenticate_user
        def update_data_center(user, project_id, data_center_id):
            return self.data_center_service.update(
                data_center_id,
                optional_param("name"),
                optional_param("description"),
                project_id,
                user["id"],
            )

        @self.app.delete("/api/v1/projects/<project_id>/infra/data-centers/<data_center_id>")
        @authenticate_user
        def delete_data_center(user, project_id, data_center_id):
            return self.data_center_service.delete(data_center_id, project_id, user["id"])
