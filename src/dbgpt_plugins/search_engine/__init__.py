"""This is the Baidu search engines plugin for Auto-GPT."""
import os
from typing import Any, Dict, List, Optional, Tuple, TypedDict, TypeVar

from auto_gpt_plugin_template import AutoGPTPluginTemplate

from .baidu_search import _baidu_search
from .google_search import _google_search
from .bing_search import _bing_search

PromptGenerator = TypeVar("PromptGenerator")

class Message(TypedDict):
    role: str
    content: str

class AutoGPTSearchEngine(AutoGPTPluginTemplate):
    def __init__(self):
        super().__init__()
        self._name = "Search-Engine-Plugin"
        self._version = "0.2.0"
        self._description = (
            "This plug-in provides search for Internet information."
        )
        self.search_engine = os.getenv("SEARCH_ENGINE")
        language = os.getenv("LANGUAGE", "en")
        if self.search_engine is None:
            if language is not None and language == "en":
                self.search_engine = "google"
            else:
                self.search_engine = "baidu"

    def can_handle_post_prompt(self) -> bool:
        return True

    def post_prompt(self, prompt: PromptGenerator) -> PromptGenerator:
        if self.search_engine == "google":
            # Add Baidu Search command
            prompt.add_command(
                "Internet information search engine",
                "google_search",
                {"query": "<query>"},
                _google_search,
            )
        elif self.search_engine == "bing":
            # Add Baidu Search command
            prompt.add_command(
                "Internet information search engine",
                "bing_search",
                {"query": "<query>"},
                _bing_search,
            )
        else:
            # Add Baidu Search command
            prompt.add_command(
                "Internet information search engine",
                "baidu_search",
                {"query": "<query>"},
                _baidu_search,
            )

        return prompt

    def can_handle_pre_command(self) -> bool:
        return True

    def pre_command(
        self, command_name: str, arguments: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        print(f"pre_command:{command_name},{arguments}")
        if self.search_engine == "google":
            return "google_search", {"query": arguments["query"]}
        elif self.search_engine == "bing":
            return "bing_search", {"query": arguments["query"]}
        else:
            return "baidu_search", {"query": arguments["query"]}

    def can_handle_post_command(self) -> bool:
        return False

    def post_command(self, command_name: str, response: str) -> str:
        pass

    def can_handle_on_planning(self) -> bool:
        return False

    def on_planning(
        self, prompt: PromptGenerator, messages: List[Message]
    ) -> Optional[str]:
        pass

    def can_handle_on_response(self) -> bool:
        return False

    def on_response(self, response: str, *args, **kwargs) -> str:
        pass

    def can_handle_post_planning(self) -> bool:
        return False

    def post_planning(self, response: str) -> str:
        pass

    def can_handle_pre_instruction(self) -> bool:
        return False

    def pre_instruction(self, messages: List[Message]) -> List[Message]:
        pass

    def can_handle_on_instruction(self) -> bool:
        return False

    def on_instruction(self, messages: List[Message]) -> Optional[str]:
        pass

    def can_handle_post_instruction(self) -> bool:
        return False

    def post_instruction(self, response: str) -> str:
        pass
    
    def can_handle_chat_completion(
        self, messages: Dict[Any, Any], model: str, temperature: float, max_tokens: int
    ) -> bool:
        return False

    def handle_chat_completion(
        self, messages: List[Message], model: str, temperature: float, max_tokens: int
    ) -> str:
        pass
    
    def can_handle_text_embedding(
        self, text: str
    ) -> bool:
        return False
    
    def handle_text_embedding(
        self, text: str
    ) -> list:
        pass
    
    def can_handle_user_input(self, user_input: str) -> bool:
        return False

    def user_input(self, user_input: str) -> str:
        return user_input

    def can_handle_report(self) -> bool:
        return False

    def report(self, message: str) -> None:
        pass

