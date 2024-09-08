from bson import ObjectId
from pymongo.collection import Collection
from datetime import datetime


class OrganizationService:
    def __init__(self, mongo: Collection):
        self.mongo = mongo

    def create(self, name: str, creator_id: str) -> dict:
        organization_id = self.mongo.insert_one({
            "name": name,
            "creator_id": creator_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }).inserted_id

        return {
            "id": str(organization_id),
        }

    def get(self, organization_id: str) -> dict:
        organization = self.mongo.find_one({
            "_id": ObjectId(organization_id)
        })

        if not organization:
            raise Exception("Organization not found")

        return self.to_dict(organization)

    def get_by_name(self, name: str) -> dict:
        organization = self.mongo.find_one({
            "name": name
        })

        if not organization:
            raise Exception(f"Organization {name} not found")

        return self.to_dict(organization)

    def name_exists(self, name: str) -> bool:
        return self.mongo.count_documents({
            "name": name
        }) > 0

    @staticmethod
    def to_dict(self):
        return {
            "id": str(self["_id"]),
            "name": self["name"],
            "creator_id": self["creator_id"],
            "created_at": self["created_at"],
            "updated_at": self["updated_at"],
        }
