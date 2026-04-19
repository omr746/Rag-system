from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum

class ProcessController(BaseController):
    def __init__(self,project_id:str):
        super().__init__()
        self.project_id=project_id
        self.project_path=ProjectController().get_project_path(project_id=project_id)
    
    def get_file_extension(self,file_id:str):
        return os.path.splitext(file_id)[-1]
    def get_file_loader(self,file_id:str):
        file_ext=self.get_file_extension(file_id=file_id)
        file_path=os.path.join(
            self.project_path,
            file_id
        )
        if not os.path.exists(file_path):
            return None
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path,encoding="utf-8")
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        if file_ext == ProcessingEnum.JSON.value:
            return JSONLoader(
            file_path=file_path,
            jq_schema=".",
            text_content=False
          )
        return None
    def get_file_content(self,file_id:str):
        loader= self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()
        return None
    def process_file_content(self,file_content:list,
                             file_id:str,chunk_size:int=100,overlap_size:int=20):
        
        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )
        file_content_texts= [
            rec.page_content
            for rec in file_content
        ]
        file_content_metadata= [
            rec.metadata
            for rec in file_content
        ]
        chunks=text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_metadata
        )
        return chunks
    def process_file_content2(self, file_content: list,
                          file_id: str, chunk_size: int = 100, overlap_size: int = 20):
        import json
        from langchain.schema import Document

        chunks = []

        for rec in file_content:
            try:
                parsed   = json.loads(rec.page_content)
                patterns = parsed if isinstance(parsed, list) else [parsed]

                for pattern in patterns:
                    if "historical_pattern_id" not in pattern:
                        continue
                    if not pattern.get("window_data") or len(pattern["window_data"]) < 5:
                        continue

                    narrative = logs_to_embedding_text(
                        window_data  = pattern["window_data"],
                        label        = pattern.get("label"),
                        failure_type = pattern.get("failure_type"),
                        machine_id   = pattern.get("machine_project_id"),
                    )

                    chunks.append(Document(
                        page_content=narrative,
                        metadata={
                            **rec.metadata,
                            "file_id":      file_id,
                            "pattern_id":   pattern["historical_pattern_id"],
                            "machine_id":   pattern["machine_project_id"],
                            "label":        pattern.get("label", "UNKNOWN"),
                            "failure_type": pattern.get("failure_type", "NONE"),
                            "analysis":     pattern.get("analysis", ""),
                        }
                    ))

            except (json.JSONDecodeError, KeyError) as e:
                print(f"[SKIP] unparseable record in file {file_id}: {e}")
                continue

        return chunks