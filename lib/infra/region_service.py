from bson import ObjectId
from pymongo.collection import Collection
from datetime import datetime
from lib.project import ProjectAccessService


class RegionService:
    def __init__(self, mongo: Collection, project_access_service: ProjectAccessService):
        self.mongo = mongo
        self.project_access_service = project_access_service

    def create(self, name: str, description: str, project_id: str, creator_id: str, organization_id: str):
        if not self.project_access_service.has_access(project_id, creator_id, "infra.region.admin"):
            raise Exception("Not allowed")

        if self.name_exists(name, project_id):
            raise Exception(f"Region {name} already exists")

        region_id = self.mongo.insert_one({
            "name": name,
            "description": description,
            "project_id": project_id,
            "creator_id": creator_id,
            "organization_id": organization_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }).inserted_id

        return {
            "id": str(region_id)
        }

    def fetch(self, project_id: str, requester_id: str, page: int = 0, size: int = 50) -> list[dict]:
        if not self.project_access_service.has_any_access(project_id, requester_id):
            raise Exception("Project not found")

        regions = self.mongo.find({
            "project_id": project_id,
        }).skip(page * size).limit(size)

        result = []

        for region in regions:
            result.append(self.to_dict(region))

        return result

    def get(self, region_id: str, project_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_any_access(project_id, requester_id):
            raise Exception("Project not found")

        region = self.mongo.find_one({
            "_id": ObjectId(region_id),
            "project_id": project_id,
        })

        if not region:
            raise Exception("Region not found")

        return self.to_dict(region)

    def update(self, region_id: str, name: str, description: str, project_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_access(project_id, requester_id, "infra.region.admin"):
            raise Exception("Not allowed")

        fields = {
            "updated_at": datetime.now(),
            "description": description,
        }

        if name:
            if self.mongo.count_documents({
                "_id": {"$ne": ObjectId(region_id)},
                "name": name,
                "project_id": project_id
            }) > 0:
                raise Exception(f"Project {name} already exists")

            fields["name"] = name

        result = self.mongo.update_one({
            "_id": ObjectId(region_id),
            "project_id": project_id,
        }, {
            "$set": fields
        })

        if result.matched_count == 0:
            raise Exception("Region not found")

        return {
            "id": region_id
        }

    def delete(self, region_id: str, project_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_access(project_id, requester_id, "infra.region.admin"):
            raise Exception("Not allowed")

        result = self.mongo.delete_one({
            "_id": ObjectId(region_id),
            "project_id": project_id,
        })

        if result.deleted_count == 0:
            raise Exception("Region not found")

        return {
            "id": region_id
        }

    def exists(self, region_id: str, project_id: str) -> bool:
        return self.mongo.count_documents({
            "_id": ObjectId(region_id),
            "project_id": project_id
        }) > 0

    def name_exists(self, name: str, project_id: str) -> bool:
        return self.mongo.count_documents({
            'name': name,
            'project_id': project_id
        }) > 0

    @staticmethod
    def to_dict(self) -> dict:
        return {
            "id": str(self["_id"]),
            "name": self["name"],
            "description": self["description"],
            "project_id": self["project_id"],
            "creator_id": self["creator_id"],
            "organization_id": self["organization_id"],
            "created_at": self["created_at"],
            "updated_at": self["updated_at"],
        }
