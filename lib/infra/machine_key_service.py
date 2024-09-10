from bson import ObjectId
from pymongo.collection import Collection
from datetime import datetime
from password_generator import PasswordGenerator
from lib.project import ProjectAccessService


class MachineKeyService:
    def __init__(self, mongo: Collection, project_access_service: ProjectAccessService):
        self.mongo = mongo
        self.project_access_service = project_access_service
        self.key_generator = PasswordGenerator()
        self.key_generator.minlen = 128
        self.key_generator.maxlen = 128
        self.key_generator.excludeschars = True

    def create(self, project_id: str, name: str, creator_id: str, organization_id: str):
        if self.project_access_service.has_access(project_id, creator_id, "infra.machine-key.admin"):
            raise Exception("Not allowed")

        key = self.key_generator.generate()

        if self.name_exists(name, project_id):
            raise Exception(f"Machine key {name} already exists")

        machine_key_id = self.mongo.insert_one({
            "name": name,
            "key": key,
            "project_id": project_id,
            "creator_id": creator_id,
            "organization_id": organization_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }).inserted_id

        return {
            "id": str(machine_key_id)
        }

    def fetch(self, project_id: str, requester_id: str, page: int = 0, size: int = 50) -> list[dict]:
        if not self.project_access_service.has_any_access(project_id, requester_id):
            raise Exception("Project not found")

        machine_keys = self.mongo.find({
            "project_id": project_id,
        }).skip(page * size).limit(size)

        result = []

        for machine_key in machine_keys:
            result.append(self.to_dict(machine_key))

        return result

    def get(self, machine_key_id: str, project_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_any_access(project_id, requester_id):
            raise Exception("Project not found")

        machine_key = self.mongo.find_one({
            "_id": ObjectId(machine_key_id),
            "project_id": project_id,
        })

        if not machine_key:
            raise Exception("Machine key not found")

        return self.to_dict(machine_key)

    def update(self, machine_key_id: str, name: str, project_id: str, requester_id: str) -> dict:
        if self.project_access_service.has_access(project_id, requester_id, "infra.machine-key.admin"):
            raise Exception("Not allowed")

        fields = {
            "updated_at": datetime.now(),
        }

        if name:
            if self.mongo.count_documents({
                "_id": {"$ne": ObjectId(machine_key_id)},
                "name": name,
                "project_id": project_id,
            }) > 0:
                raise Exception("Machine key {name} already exists")

            fields["name"] = name

        result = self.mongo.update_one({
            "_id": ObjectId(machine_key_id),
            "project_id": project_id,
        }, {
            "$set": fields,
        })

        if result.matched_count == 0:
            raise Exception("Machine key not found")

        return {
            "id": machine_key_id
        }

    def delete(self, machine_key_id: str, project_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_access(project_id, requester_id, "infra.machine-key.admin"):
            raise Exception("Project not found")

        result = self.mongo.delete_one({
            "_id": ObjectId(machine_key_id),
            "project_id": project_id,
        })

        if result.deleted_count == 0:
            raise Exception("Machine key not found")

        return {
            "id": machine_key_id
        }

    def get_key(self, machine_key_id: str, project_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_access(project_id, requester_id, "infra.machine-key.admin"):
            raise Exception("Project not found")

        machine_key = self.mongo.find_one({
            "_id": ObjectId(machine_key_id),
            "project_id": project_id,
        })

        if not machine_key:
            raise Exception("Machine key not found")

        return {
            "id": str(machine_key["_id"]),
            "key": machine_key["key"]
        }

    def name_exists(self, name: str, project_id: str):
        return self.mongo.count_documents({
            'name': name,
            'project_id': project_id
        }) > 0

    @staticmethod
    def to_dict(self) -> dict:
        return {
            'id': str(self['_id']),
            'name': self['name'],
            'project_id': self['project_id'],
            'creator_id': self['creator_id'],
            'organization_id': self['organization_id'],
            'created_at': self['created_at'],
            'updated_at': self['updated_at'],
        }
