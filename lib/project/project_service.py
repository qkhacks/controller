from bson import ObjectId
from pymongo.collection import Collection
from datetime import datetime
from .project_access_service import ProjectAccessService
from lib.identity import UserService


class ProjectService:

    def __init__(self, mongo: Collection, project_access_service: ProjectAccessService, user_service: UserService):
        self.mongo = mongo
        self.project_access_service = project_access_service
        self.user_service = user_service

    def create(self, name: str, creator_id: str, organization_id: str) -> dict:
        if self.name_exists(name, organization_id):
            raise Exception(f"Project {name} already exists")

        project_id = self.mongo.insert_one({
            "name": name,
            "creator_id": creator_id,
            "organization_id": organization_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }).inserted_id

        project_id_str = str(project_id)

        self.project_access_service.add(project_id_str, creator_id, ["all"], "")

        return {
            "id": project_id_str
        }

    def fetch(self, requester_id: str, page: int = 0, size: int = 50) -> list[dict]:
        mappings = self.project_access_service.fetch_projects(requester_id, page, size)
        project_ids = []
        for mapping in mappings:
            project_ids.append(ObjectId(mapping["project_id"]))

        projects = self.mongo.find({
            "_id": {"$in": project_ids}
        })

        project_map = {}
        for project in projects:
            p = self.to_dict(project)
            project_map[p["id"]] = p

        result = []
        for mapping in mappings:
            result.append({
                "permissions": mapping["permissions"],
                "project": project_map[mapping["project_id"]],
            })

        return result

    def get(self, project_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_any_access(project_id, requester_id):
            raise Exception("Project not found")

        project = self.mongo.find_one({"_id": ObjectId(project_id)})

        if not project:
            raise Exception("Project not found")

        return self.to_dict(project)

    def update(self, project_id: str, name: str, requester_id: str, organization_id: str) -> dict:
        if not self.project_access_service.has_access(project_id, requester_id, "all"):
            raise Exception("Not allowed")

        fields = {
            "updated_at": datetime.now(),
        }

        if name:
            if self.mongo.count_documents({
                "_id": {"$ne": ObjectId(project_id)},
                "name": name,
                "organization_id": organization_id
            }) != 0:
                raise Exception(f"Project {name} already exists")

            fields["name"] = name

        result = self.mongo.update_one({
            "_id": ObjectId(project_id),
        }, {
            "$set": fields
        })

        if result.matched_count == 0:
            raise Exception("Project not found")

        return {
            "id": project_id
        }

    def delete(self, project_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_access(project_id, requester_id, "all"):
            raise Exception("Not allowed")

        result = self.mongo.delete_one({"_id": ObjectId(project_id)})
        if result.deleted_count == 0:
            raise Exception("Project not found")

        return {
            "id": project_id
        }

    def add_access(self, project_id: str, user_id: str, permissions: list[str], creator_id: str, organization_id: str) -> dict:
        if not self.project_access_service.has_access(project_id, creator_id, "all"):
            raise Exception("Not allowed")

        user = self.user_service.get_by_organization(user_id, organization_id)
        self.project_access_service.add(project_id, user["id"], permissions, creator_id)

        return {
            "project_id": project_id,
            "user": user,
            "permissions": permissions
        }

    def delete_access(self, project_id: str, user_id: str, permissions: list[str], requester_id: str) -> dict:
        if not self.project_access_service.has_access(project_id, requester_id, "all"):
            raise Exception("Not allowed")

        return self.project_access_service.delete(project_id, user_id, permissions)

    def delete_all_access(self, project_id: str, user_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_access(project_id, requester_id, "all"):
            raise Exception("Not allowed")

        return self.project_access_service.delete_all(project_id, user_id)

    def fetch_users(self, project_id: str, requester_id: str, page: int = 0, size: int = 50) -> list[dict]:
        if not self.project_access_service.has_any_access(project_id, requester_id):
            raise Exception("Project not found")

        mappings = self.project_access_service.fetch_users(project_id, page, size)

        user_ids = []
        for mapping in mappings:
            user_ids.append(mapping["user_id"])

        users = self.user_service.fetch_by_ids(user_ids)
        user_map = {}
        for user in users:
            user_map[user["id"]] = user

        result = []
        for mapping in mappings:
            result.append({
                "permissions": mapping["permissions"],
                "user": user_map[mapping["user_id"]],
            })
        return result

    def name_exists(self, name: str, organization_id: str) -> bool:
        return self.mongo.count_documents({
            "name": name,
            "organization_id": organization_id
        }) > 0

    @staticmethod
    def to_dict(self):
        return {
            "id": str(self["_id"]),
            "name": self["name"],
            "creator_id": self["creator_id"],
            "organization_id": self["organization_id"],
            "created_at": self["created_at"],
            "updated_at": self["updated_at"],
        }
