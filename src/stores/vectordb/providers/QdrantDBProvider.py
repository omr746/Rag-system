from qdrant_client import models,QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from typing import List
import logging
from models.db_schemes import RetrieveDocument
class QdrantDBProvider(VectorDBInterface):
    def __init__(self,db_path:str,distance_method:str):
        self.db_path=db_path
        self.client=None
        self.distance_method=None
        self.logger=logging.getLogger(__name__)
        if distance_method ==DistanceMethodEnums.COSINE.value:
            self.distance_method=models.Distance.COSINE

        if distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method=models.Disatnce.DOT
        
    def connect(self):
        self.client=QdrantClient(path=self.db_path)
    def disconnect(self):
        self.client=None
    def is_collection_existed(self, collection_name)->bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self)->List:
        return self.client.get_collections()
    def get_collection_info(self, collection_name)->dict:
        return self.client.get_collection(collection_name=collection_name)
    def delete_collection(self, collection_name):
        if self.is_collection_existed(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)
    
    def create_collection(self, collection_name, embedding_size, do_reset = False):
      if do_reset:
          self.delete_collection(collection_name=collection_name)
      if not self.is_collection_existed(collection_name=collection_name):
          self.client.create_collection(
              collection_name=collection_name,
              vectors_config=models.VectorParams(
                 size=embedding_size,
                  distance=self.distance_method
              )
          )
          return True
      return False
    def insert_one(self, collection_name, text, vector, metadata = None, record_id = None):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")

            return False
        try:
            self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=[record_id],
                        vector=vector,
                        payload={
                            "text":text,
                            "metadata":metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting {e}")
            return False
        return True
    def insert_many(self, collection_name, texts, vectors, metadata = None, record_ids = None, batch_size = 50):
        if metadata is None:
            metadata=[None]*len(texts)
        if record_ids is None:
            record_ids=[None]*len(texts)
        for i in range(0,len(texts),batch_size):
            batch_end=i+batch_size
            batch_texts=texts[i:batch_end]
            batch_vectors=vectors[i:batch_end]
            batch_metadata=metadata[i:batch_end]
            batch_ids=record_ids[i:batch_end]
            batch_records=[
                   models.Record(
                    id=batch_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text":batch_texts[x],
                        "metadata":batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]
            try:
                self.client.upload_records(
                collection_name=collection_name,
                records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch:{e}")
                return False
            return True
    def search_by_vector(self, collection_name, vector, limit=5):
        results=self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )
        if not results or len(results)==0:
            return None
        return[
            RetrieveDocument(**{
                "text":result.payload["text"],
                "score":result.score
            })
            for result in results
        ]





      
    