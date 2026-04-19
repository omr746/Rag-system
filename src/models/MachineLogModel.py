from .BaseDataModel import BaseDataModel
from .db_schemes import MachineLog
from .enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId
from pymongo import InsertOne
import json

class MachineLogModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_MACHINE_LOG_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_MACHINE_LOG_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_MACHINE_LOG_NAME.value]
            indexes = MachineLog.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_log(self, log: MachineLog):
        result = await self.collection.insert_one(log.dict(by_alias=True, exclude_unset=True))
        log.id = result.inserted_id
        return log

    async def get_log(self, log_id: str):
        result = await self.collection.find_one({"_id": ObjectId(log_id)})
        if result is None:
            return None
        return MachineLog(**result)

    async def insert_many_logs(self, logs: list, batch_size: int = 100):
        for i in range(0, len(logs), batch_size):
            batch = logs[i:i + batch_size]
            operations = [
                InsertOne(log.dict(by_alias=True, exclude_unset=True))
                for log in batch
            ]
            await self.collection.bulk_write(operations)
        return len(logs)

    async def delete_logs_by_machine_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"machine_project_id": project_id})
        return result.deleted_count

    async def get_machine_project_logs(self, project_id: ObjectId, page_no: int = 1, page_size: int = 50):
        results = await self.collection.find({"machine_project_id": project_id})\
                                       .skip((page_no - 1) * page_size)\
                                       .limit(page_size)\
                                       .to_list(length=None)
        return [MachineLog(**rec) for rec in results]
        return json.loads(
            json.dumps(results,default=lambda x: x.__dict__)
        )