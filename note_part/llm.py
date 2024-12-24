import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

class OpenAILLM:
    def __init__(self):
        self.model = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")
        self.strucutue_model = None
        self.chain = None
    
    def build(self, template, schema=None):
        prompt = PromptTemplate.from_template(template)
        if schema:
            self._strucuturize(schema)
            self.chain = prompt | self.strucutue_model
        else:
            self.chain = prompt | self.model
        
    def invoke(self, payload):
        return self.chain.invoke(payload)
    
    def _strucuturize(self, schema):
        self.strucutue_model = self.model.with_structured_output(schema)