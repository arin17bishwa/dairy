from typing import Sequence


class SimpleContextBuilder:
    def get_system_prompt(self):
        return """You are a personal assistant, named Tsubaki. You help me explore my life and memories which I have written down or somehow digitally recorded. 
        You also help me psychoanalyse myself.

        Answer the user's question using the supplied journal
        entries, chats with friends, etc. Do not invent information that isn't present
        in the entries."""

    def get_user_prompt(self, retrievals:Sequence[dict], query:str)->str:

        retrieval_context="\n".join(
            f"""
            Journal entry - {retrieval['chunk'].start_timestamp.strftime("%B %d, %Y")}
            {retrieval['chunk'].text}"""
            for retrieval in retrievals
        )

        context=f"""
        CONTEXT:
        {retrieval_context}
        
        USER:
        {query}"""

        return context
