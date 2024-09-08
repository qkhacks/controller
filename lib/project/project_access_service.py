from pymongo.collection import Collection
from datetime import datetime


class ProjectAccessService:
    def __init__(self, mongo: Collection):
        self.mongo = mongo

    def add(self, project_id: str, user_id: str, permissions: list[str], creator_id: str) -> dict:
        self.mongo.update_one({
            "project_id": project_id,
            "user_id": user_id,
        }, {
            "$setOnInsert": {
                "project_id": project_id,
                "user_id": user_id,
                "creator_id": creator_id,
                "created_at": datetime.now()
            },
            "$addToSet": {
                "permissions": {
                    "$each": permissions
                }
            },
            "$set": {
                "updated_at": datetime.now(),
            }
        }, upsert=True)

        return {
            "project_id": project_id,
            "user_id": user_id
        }

    def delete(self, project_id: str, user_id: str, permissions: list[str]) -> dict:
        result = self.mongo.update_one({
            "project_id": project_id,
            "user_id": user_id,
        }, {
            "$set": {
                "updated_at": datetime.now(),
            },
            "$pullAll": {
                "permissions": permissions
            }
        })

        if result.matched_count == 0:
            raise Exception("Project access not found")

        return {
            "project_id": project_id,
            "user_id": user_id
        }

    def delete_all(self, project_id: str, user_id: str) -> dict:
        result = self.mongo.delete_one({
            "project_id": project_id,
            "user_id": user_id
        })

        if result.deleted_count == 0:
            raise Exception("Project access not found")

        return {
            "project_id": project_id,
            "user_id": user_id
        }

    def fetch_users(self, project_id: str, page: int = 0, size: int = 50) -> list[dict]:
        mappings = self.mongo.find({
            "project_id": project_id,
        }).skip(page * size).limit(size)

        result = []
        for mapping in mappings:
            result.append({
                "user_id": mapping["user_id"],
                "permissions": mapping["permissions"]
            })

        return result

    def fetch_projects(self, user_id: str, page: int = 0, size: int = 50) -> list[dict]:
        mappings = self.mongo.find({
            "user_id": user_id,
        }).skip(page * size).limit(size)

        result = []
        for mapping in mappings:
            result.append({
                "project_id": mapping["project_id"],
                "permissions": mapping["permissions"]
            })

        return result

    def has_access(self, project_id: str, user_id: str, permission: str):
        return self.mongo.count_documents({
            "project_id": project_id,
            "user_id": user_id,
            "permissions": {"$in": [permission, "all"]}
        }) > 0

    def has_any_access(self, project_id: str, user_id: str) -> bool:
        return self.mongo.count_documents({
            "project_id": project_id,
            "user_id": user_id,
            "permissions": {
                "$not": {
                    "$size": 0
                }
            }
        }) > 0
