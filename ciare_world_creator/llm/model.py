import os
import sys
from typing import List

import langchain
import openai
from langchain import OpenAI
from langchain.cache import SQLiteCache
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    BaseMessage,
    ChatGeneration,
    ChatResult,
    Generation,
    HumanMessage,
    SystemMessage,
)

from ciare_world_creator.utils.json import parse_output_to_json

langchain.verbose = True
langchain.llm_cache = SQLiteCache(database_path="/var/tmp/ciare/.langchain.db")


class CachedChatOpenAI(ChatOpenAI):
    def _generate(self, messages: List[BaseMessage], *args, **kwargs) -> ChatResult:
        # NOTE: the cache does currently not respect additional arguments beyond the messages.
        messages_prompt = repr(messages)
        if langchain.llm_cache:
            results = langchain.llm_cache.lookup(messages_prompt, self.model_name)
            if results:
                print("Using cached query result.")
                assert len(results) == 1
                result: Generation = results[0]
                chat_result = ChatResult(
                    generations=[
                        ChatGeneration(message=AIMessage(content=result.text))
                    ],
                    llm_output=result.generation_info,
                )
                return chat_result
        chat_result = super()._generate(messages, *args, **kwargs)
        if langchain.llm_cache:
            assert len(chat_result.generations) == 1
            result = Generation(
                text=chat_result.generations[0].message.content,
                generation_info=chat_result.llm_output,
            )
            langchain.llm_cache.update(messages_prompt, self.model_name, [result])
        return chat_result


def prompt_model(context: str, prompt: str, model: str = "gpt-3.5-turbo-16k"):
    llm = CachedChatOpenAI(
        model=model, temperature=0, max_retries=0, request_timeout=120
    )
    messages = [SystemMessage(content=context), HumanMessage(content=prompt)]
    try:
        ans = llm(messages)
    except openai.error.Timeout:
        print(
            "Timeout while waiting for model response."
            "Probably in your prompt there are too many models\n"
            "Re-run the script and adapt the prompt so that model will generate less models."
        )
        sys.exit(os.EX_UNAVAILABLE)
    return parse_output_to_json(ans.content)
