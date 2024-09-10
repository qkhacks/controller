from bson import ObjectId
from pymongo.collection import Collection
from datetime import datetime

from .region_service import RegionService
from lib.project import ProjectAccessService


class DataCenterService:
    def __init__(self, mongo: Collection, region_service: RegionService, project_access_service: ProjectAccessService):
        self.mongo = mongo
        self.region_service = region_service
        self.project_access_service = project_access_service

    def create(self, name: str, description: str, region_id: str, project_id: str, creator_id: str,
               organization_id: str):
        if not self.project_access_service.has_access(project_id, creator_id, "infra.datacenter.admin"):
            raise Exception("Not allowed")

        if self.name_exists(name, project_id):
            raise Exception(f"Data center {name} already exists in this project")

        if not self.region_service.exists(region_id, project_id):
            raise Exception("Region not found")

        data_center_id = self.mongo.insert_one({
            "name": name,
            "description": description,
            "region_id": region_id,
            "project_id": project_id,
            "creator_id": creator_id,
            "organization_id": organization_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }).inserted_id

        return {
            "id": str(data_center_id),
        }

    def fetch(self, region_id: str, project_id: str, requester_id: str, page: int = 0, size: int = 50) -> list[dict]:
        if self.project_access_service.has_any_access(project_id, requester_id):
            raise Exception("Project not found")

        data_centers = self.mongo.find({
            "region_id": region_id,
            "project_id": project_id
        }).skip(page * size).limit(size)

        result = []

        for data_center in data_centers:
            result.append(self.to_dict(data_center))

        return result

    def get(self, data_center_id: str, region_id: str, project_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_any_access(project_id, requester_id):
            raise Exception("Project not found")

        data_center = self.mongo.find_one({
            "_id": ObjectId(data_center_id),
            "region_id": region_id,
            "project_id": project_id
        })

        if not data_center:
            raise Exception("Data center not found")

        return self.to_dict(data_center)

    def update(self, data_center_id: str, name: str, description: str, region_id: str, project_id: str,
               requester_id: str):
        if not self.project_access_service.has_access(project_id, requester_id, "infra.datacenter.admin"):
            raise Exception("Project not found")

        fields = {
            "updated_at": datetime.now(),
            "description": description,
        }

        if name:
            if self.mongo.count_documents({
                "_id": {"$ne": ObjectId(data_center_id)},
                "name": name,
                "project_id": project_id
            }):
                raise Exception(f"Data center {name} already exists in this project")

            fields["name"] = name

        result = self.mongo.update_one({
            "_id": ObjectId(data_center_id),
            "region_id": region_id,
            "project_id": project_id,
        }, {
            "$set": fields
        })

        if result.matched_count == 0:
            raise Exception("Data center not found")

        return {
            "id": data_center_id,
        }

    def delete(self, data_center_id: str, region_id: str, project_id: str, requester_id: str) -> dict:
        if not self.project_access_service.has_access(project_id, requester_id, "infra.datacenter.admin"):
            raise Exception("Project not found")

        result = self.mongo.delete_one({
            "_id": ObjectId(data_center_id),
            "region_id": region_id,
            "project_id": project_id
        })

        if result.deleted_count == 0:
            raise Exception("Data center not found")

        return {
            "id": data_center_id,
        }

    def name_exists(self, name: str, project_id: str) -> bool:
        return self.mongo.count_documents({
            "name": name,
            "project_id": project_id
        }) > 0

    @staticmethod
    def to_dict(self):
        return {
            "id": str(self["_id"]),
            "name": self["name"],
            "description": self["description"],
            "project_id": self["project_id"],
            "creator_id": self["creator_id"],
            "organization_id": self["organization_id"],
            "created_at": self["created_at"],
            "updated_at": self["updated_at"]
        }
