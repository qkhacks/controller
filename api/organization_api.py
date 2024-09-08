from flask import Flask

from lib.identity import OrganizationService
from .utils import *


class OrganizationApi:

    def __init__(self, app: Flask, organization_service: OrganizationService) -> None:
        self.app = app
        self.organization_service = organization_service

    def register(self):

        @self.app.get("/api/v1/organization")
        @authenticate_user
        def get_organization(user):
            return self.organization_service.get(user["organization_id"])
