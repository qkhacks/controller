from flask import Flask
from lib.infra import RegionService
from .utils import *


class RegionApi:
    def __init__(self, app: Flask, region_service: RegionService) -> None:
        self.app = app
        self.region_service = region_service

    def register(self):
        @self.app.post("/api/v1/projects/<project_id>/infra/regions")
        @authenticate_user
        def create_region(user, project_id):
            return self.region_service.create(
                required_param("name"),
                optional_param("description"),
                project_id,
                user["id"],
                user["organization_id"],
            )

        @self.app.get("/api/v1/projects/<project_id>/infra/regions")
        @authenticate_user
        def fetch_regions(user, project_id):
            return self.region_service.fetch(project_id, user["id"], page(), size())

        @self.app.get("/api/v1/projects/<project_id>/infra/regions/<region_id>")
        @authenticate_user
        def get_region(user, project_id, region_id):
            return self.region_service.get(region_id, project_id, user["id"])

        @self.app.put("/api/v1/projects/<project_id>/infra/regions/<region_id>")
        @authenticate_user
        def update_region(user, project_id, region_id):
            return self.region_service.update(
                region_id,
                optional_param("name"),
                optional_param("description"),
                project_id,
                user["id"],
            )

        @self.app.delete("/api/v1/projects/<project_id>/infra/regions/<region_id>")
        @authenticate_user
        def delete_region(user, project_id, region_id):
            return self.region_service.delete(region_id, project_id, user["id"])
