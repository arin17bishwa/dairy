import os

from ollama import chat, Client
from src.llm.llm import LLM
from dotenv import load_dotenv

load_dotenv()


class OllamaLLM(LLM):

    def __init__(self, model: str,
                 host:str=os.environ.get("OLLAMA_HOST","http://localhost:11434"),
                 token:str=os.environ.get("OLLAMA_API_KEY","")
                 ):
        self.model = model

        headers={"Authorization":f"Bearer {token}"}
        print(f'ollama calling at: {host}')
        self.client=Client(host=host, headers=headers, verify=False)


    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return response.message.content
