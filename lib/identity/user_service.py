import time
from datetime import datetime

import bcrypt
import jwt
from bson import ObjectId
from password_generator import PasswordGenerator
from pymongo.collection import Collection

from .organization_service import OrganizationService


class UserService:

    def __init__(self, mongo: Collection, organization_service: OrganizationService, jwt_signing_key: str):
        self.mongo = mongo
        self.organization_service = organization_service
        self.jwt_signing_key = jwt_signing_key
        self.password_generator = PasswordGenerator()

    def sign_up(self, username: str, password: str, organization_name: str) -> dict:
        if self.organization_service.name_exists(organization_name):
            raise Exception(f"Organization {organization_name} already exists")

        user_id = self.mongo.insert_one({
            "username": username,
            "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "organization_id": None,
            "creator_id": None,
            "admin": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }).inserted_id

        user_id_str = str(user_id)
        organization_id = self.organization_service.create(organization_name, user_id_str)["id"]

        self.mongo.update_one({
            "_id": user_id
        }, {
            "$set": {
                "organization_id": organization_id
            }
        })

        return {
            "id": user_id_str,
            "organization_id": organization_id
        }

    def get_token(self, username: str, password: str, organization_name: str) -> dict:
        organization = self.organization_service.get_by_name(organization_name)
        user = self.mongo.find_one({
            "username": username,
            "organization_id": organization["id"]
        })

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            raise Exception("Invalid username and password combination")

        token = jwt.encode({
            "sub": str(user["_id"]),
            "organization_id": user["organization_id"],
            "admin": user["admin"],
            "iat": int(time.time()),
            "iss": "silicate",
            "aud": "silicate",
        }, algorithm="HS256", key=self.jwt_signing_key)

        return {
            "token": token
        }

    def get(self, user_id: str) -> dict:
        user = self.mongo.find_one({
            "_id": ObjectId(user_id),
        })

        if not user:
            raise Exception("User not found")

        return self.to_dict(user)

    def change_password(self, user_id: str, password: str):
        fields = {
            "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "updated_at": datetime.now(),
        }

        result = self.mongo.update_one({
            "_id": ObjectId(user_id),
        }, {
            "$set": fields
        })

        if result.matched_count == 0:
            raise Exception("User not found")

        return {
            "id": user_id
        }

    def add(self, username: str, admin: bool, creator_id: str, organization_id: str) -> dict:
        if self.username_exists(username, organization_id):
            raise Exception(f"Username {username} already exists")

        password = self.password_generator.generate()

        user_id = self.mongo.insert_one({
            "username": username,
            "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "admin": admin,
            "creator_id": creator_id,
            "organization_id": organization_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }).inserted_id

        return {
            "id": str(user_id),
            "password": password,
        }

    def delete(self, user_id: str, organization_id: str) -> dict:
        result = self.mongo.delete_one({
            "_id": ObjectId(user_id),
            "organization_id": organization_id
        })

        if result.deleted_count == 0:
            raise Exception("User not found")

        return {
            "id": user_id
        }

    def fetch(self, organization_id: str, page=0, size=50) -> list[dict]:
        users = self.mongo.find({
            "organization_id": organization_id
        }).skip(page * size).limit(size)

        result = []
        for user in users:
            result.append(self.to_dict(user))

        return result

    def fetch_by_ids(self, user_ids: list[str]) -> list[dict]:
        ids = []
        for user_id in user_ids:
            ids.append(ObjectId(user_id))
        users = self.mongo.find({
            "_id": {"$in": ids}
        })

        result = []
        for user in users:
            result.append(self.to_dict(user))
        return result

    def get_by_organization(self, user_id: str, organization_id: str) -> dict:
        user = self.mongo.find_one({
            "_id": ObjectId(user_id),
            "organization_id": organization_id
        })

        if not user:
            raise Exception("User not found")

        return self.to_dict(user)

    def reset_password(self, user_id: str, organization_id: str) -> dict:
        password = self.password_generator.generate()
        fields = {
            "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            "updated_at": datetime.now()
        }

        result = self.mongo.update_one({
            "_id": ObjectId(user_id),
            "organization_id": organization_id
        }, {
            "$set": fields
        })

        if result.matched_count == 0:
            raise Exception("User not found")

        return {
            "id": user_id,
            "password": password
        }

    def change_admin(self, user_id: str, admin: bool, organization_id: str) -> dict:
        fields = {
            "updated_at": datetime.now(),
            "admin": admin
        }

        result = self.mongo.update_one({
            "_id": ObjectId(user_id),
            "organization_id": organization_id
        }, {
            "$set": fields
        })

        if result.matched_count == 0:
            raise Exception("User not found")

        return {
            "id": user_id
        }

    def username_exists(self, username: str, organization_id: str) -> bool:
        return self.mongo.count_documents({
            "username": username,
            "organization_id": organization_id
        }) > 0

    @staticmethod
    def to_dict(self):
        return {
            "id": str(self["_id"]),
            "username": self["username"],
            "organization_id": self["organization_id"],
            "admin": self["admin"],
            "created_at": self["created_at"],
            "updated_at": self["updated_at"]
        }
