from flask import Flask
from lib.infra import MachineKeyService
from .utils import *

class MachineKeyApi:
    def __init__(self, app: Flask, machine_key_service: MachineKeyService):
        self.app = app
        self.machine_key_service = machine_key_service

    def register(self):

        @self.app.post("/api/v1/projects/<project_id>/infra/machine-keys")
        @authenticate_user
        def create_machine_key(user, project_id):
            return self.machine_key_service.create(
                project_id,
                required_param("name"),
                user["id"],
                user["organization_id"]
            )

        @self.app.get("/api/v1/projects/<project_id>/infra/machine-keys")
        @authenticate_user
        def fetch_machine_keys(user, project_id):
            return self.machine_key_service.fetch(project_id, user["id"], page(), size())

        @self.app.get("/api/v1/projects/<project_id>/infra/machine-keys/<machine_key_id>")
        @authenticate_user
        def get_machine_key(user, project_id, machine_key_id):
            return self.machine_key_service.get(machine_key_id, project_id, user["id"])

        @self.app.put("/api/v1/projects/<project_id>/infra/machine-keys/<machine_key_id>")
        @authenticate_user
        def update_machine_key(user, project_id, machine_key_id):
            return self.machine_key_service.update(
                machine_key_id,
                optional_param("name"),
                project_id,
                user["id"]
            )

        @self.app.delete("/api/v1/projects/<project_id>/infra/machine-keys/<machine_key_id>")
        @authenticate_user
        def delete_machine_key(user, project_id, machine_key_id):
            return self.machine_key_service.delete(machine_key_id, project_id, user["id"])

        @self.app.get("/api/v1/projects/<project_id>/infra/machine-keys/<machine_key_id>/key")
        @authenticate_user
        def get_machine_key_secret(user, project_id, machine_key_id):
            return self.machine_key_service.get_key(machine_key_id, project_id, user["id"])
