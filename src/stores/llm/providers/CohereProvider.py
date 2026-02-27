from ..LLMInterface import LLMInterface
import cohere
import logging
from ..LLMEnums import CohereEnums ,DocumentTypeEnum
class CohereProvider(LLMInterface):
    def __init__(self,api_key:str
                 ,default_input_max_characters:int=1000,
                 default_generation_max_output_tokens:int=1000,
                  default_generation_temperature:float=0.1):
        self.api_key=api_key
        self.default_input_max_characters=default_input_max_characters
        self.default_generation_max_output_tokens=default_generation_max_output_tokens
        self.default_generation_temperature=default_generation_temperature
        self.generation_model_id=None
        self.embedding_model_id=None
        self.embedding_size=None
        self.enums=CohereEnums
        self.client=cohere.Client(
            api_key=self.api_key
        )
        self.logger=logging.getLogger(__name__)
    def set_generation_model(self, model_id):
        self.generation_model_id=model_id
    def  set_embedding_model(self, model_id,embedding_size):
        self.embedding_model_id=model_id
        self.embedding_size=embedding_size

    def generate_text(self, prompt,chat_history, max_output_tokens=None, temperature = None):
         if not self.client:
            self.logger.error("Cohere client was not set")
            return None
         if not self.generation_model_id:
            self.logger.error("generation model for Cohere was not set")
            return None
         max_output_tokens= max_output_tokens if max_output_tokens is not None else self.default_generation_max_output_tokens 
         temperature =temperature if temperature is not None else self.default_generation_temperature
         chat_history.append(
             self.construct_prompt(prompt=prompt,role=CohereEnums.USER.value)
         )
         response=self.client.chat(
             model=self.generation_model_id,
             chat_history=chat_history,
             message=self.process_text(prompt),
             temperature=temperature,
             max_tokens=max_output_tokens
            
         )
         if not response or not response.text:
             self.logger.error("Error while generation text with Cohere")
             return None
         return response.text

    def embed_text(self, text, document_type=None):
        if not self.client:
            self.logger.error("Cohere client was not set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Cohere was not set")
            return None
        input_type= CohereEnums.DOCUMENT
        if document_type ==DocumentTypeEnum.QUERY:
            input_type=CohereEnums.QUERY
        
        response=self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type,
            embedding_types=["float"]
        )
        if not response or not response.embeddings  or not response.embeddings.float:
            self.logger.error("Erro while embedding text with Cohere")
            return None
        return response.embeddings.float[0]

    def construct_prompt(self, prompt, role):
        return{
             "role":role,
             "text":self.process_text(prompt)
         }
    def process_text(self,text:str):
        return text.strip() 
