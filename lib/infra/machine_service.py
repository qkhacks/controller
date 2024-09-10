from pymongo.collection import Collection
from .machine_key_service import MachineKeyService
from datetime import datetime


class MachineService:
    def __init__(self, mongo: Collection, machine_key_service: MachineKeyService):
        self.mongo = mongo
        self.machine_key_service = machine_key_service

    def process_heartbeat(self):
        pass
