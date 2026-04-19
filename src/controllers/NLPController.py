from .BaseController import BaseController
from models.db_schemes import Project,DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum

from typing import List
import json
class NLPController(BaseController):
    def __init__(self,vectordb_client,generation_client,embedding_client,template_parser):
        super().__init__()
        self.vectordb_client=vectordb_client
        self.generation_client=generation_client
        self.embedding_client=embedding_client
        self.template_parser=template_parser
    def create_collection_name(self,project_id:str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self,project:Project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        return  self.vectordb_client.delete_collection(collection_name=collection_name)
    def get_vector_db_collection_info(self,project:Project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        collection_info=self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info,default=lambda x: x.__dict__)
        )
    def index_into_vector_db(self,project:Project,chunks:List[DataChunk],chunks_ids:List[int],do_reset:bool=False):
          collection_name=self.create_collection_name(project_id=project.project_id)
          texts=[c.chunk_text for c in chunks]
          metadata=[c.chunk_metadata for c in chunks]
          vectors=[
              self.embedding_client.embed_text(text=text,document_type=DocumentTypeEnum.DOCUMENT.value)

              for text in texts
          ]
          self.vectordb_client.create_collection(
              collection_name=collection_name,
              embedding_size=self.embedding_client.embedding_size,
              do_reset=do_reset
          )
          self.vectordb_client.insert_many(
              collection_name=collection_name,
              texts=texts,
              metadata=metadata,
              vectors=vectors,
              record_ids=chunks_ids
            
          )
          return True
    def search_vector_db_collection(self,project:Project,text:str,limit:int=10):
          collection_name=self.create_collection_name(project_id=project.project_id)
          vector=self.embedding_client.embed_text(
               text=text,
               document_type=DocumentTypeEnum.QUERY.value

          )
          if not vector or len(vector)==0:
               return False
          results=self.vectordb_client.search_by_vector(
              collection_name=collection_name,
              vector=vector,
              limit=limit
            
          )
          if not results:
               return False
          return results
    def answer_rag_quesrtion(self,project:Project,query:str,limit:int=10):
         retrieved_documents=self.search_vector_db_collection(
              project=project,text=query,limit=limit
         )
         answer,full_prompt,chat_history=None,None,None

         if not retrieved_documents or len(retrieved_documents)==0:
              return answer,full_prompt,chat_history
         system_prompt=self.template_parser.get("rag","system_prompt")
         documents_prompts="\n".join([
        self.template_parser.get("rag","document_prompt",{
                        "doc_num":idx+1,
                        "chunk_text":doc.text
                   })
              for idx,doc in enumerate(retrieved_documents)
         ])
         footer_prompt=self.template_parser.get("rag","footer_prompt",{"user_question":query})
         chat_history=[
              self.generation_client.construct_prompt(
                   prompt=system_prompt,
                   role=self.generation_client.enums.SYSTEM.value
              )
         ]
         full_prompt="\n\n".join(
              [documents_prompts,footer_prompt]
         )
         answer=self.generation_client.generate_text(
              prompt=full_prompt,chat_history=chat_history
         )
         return answer,full_prompt,chat_history

    def answer_rag_question2(self, project: Project, logs: list, query: str, limit: int = 10):

        # 1. Focus strictly on the last 30 logs
        window_size = 30
        analysis_window = logs[-window_size:]
        
        if not analysis_window:
            return None, None, None

        # # 2. CREATE SMART QUERY FROM TRENDS
        # # This ensures Qdrant finds the RIGHT historical failures
        # first, last = analysis_window[0].data, analysis_window[-1].data
        # trend_summary = (
        #      f"Trend: Temp {first.get('Process temperature [K]')} to {last.get('Process temperature [K]')}, "
        #      f"Torque {first.get('Torque [Nm]')} to {last.get('Torque [Nm]')}, "
        #      f"Tool wear {last.get('Tool wear [min]')}. Find similar failure outcomes."
        # )

        # 3. Retrieve Historical Context
        search_text = " | ".join([
        f"TS:{l.ts} | "
        f"AirTemp:{l.data.get('Air temperature [K]')}K, "
        f"ProcTemp:{l.data.get('Process temperature [K]')}K, "
        f"RPM:{l.data.get('Rotational speed [rpm]')}, "
        f"Torque:{l.data.get('Torque [Nm]')}Nm, "
        f"Wear:{l.data.get('Tool wear [min]')}min"
        for l in analysis_window
    ])
        retrieved_documents = self.search_vector_db_collection(
            project=project, 
            text=search_text, # نرسل النص وليس القائمة
            limit=limit
        )
        
        if not retrieved_documents:
            return  "No historical data found to compare.", None, None

        # 4. Format Historical Documents (RAG)
        documents_prompts = "### HISTORICAL FAILURE PATTERNS:\n" + "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx + 1, "chunk_text": doc.text
            }) for idx, doc in enumerate(retrieved_documents)
        ])

        # 5. Format the 30 Logs (Current Window)
        logs_formatted_list = ["### CURRENT 30-LOG WINDOW:"]
        count = len(analysis_window)
        
        for idx, log in enumerate(analysis_window):
            offset = count - 1 - idx
            pos = "CURRENT" if offset == 0 else f"T-{offset}"
            
            # We simplify the log formatting here as requested
            logs_formatted_list.append(
                self.template_parser.get("rag", "log_prompt", {
                        "position": pos,
                        "ts": log.ts,
                        "log_data": str(log.data)
                })
            )

        # 6. Build Final Prompt
        system_prompt = self.template_parser.get("rag", "system_prompt2")
        logs_prompts = "\n".join(logs_formatted_list)
        footer = self.template_parser.get("rag", "footer_prompt", {"user_question": query})

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value
            )
        ]

        full_prompt = "\n\n".join([documents_prompts, logs_prompts, footer])

        # 7. Generate Plain Text Response
        answer = self.generation_client.generate_text(
            prompt=full_prompt, chat_history=chat_history
        )

        return answer, full_prompt, chat_history


        
