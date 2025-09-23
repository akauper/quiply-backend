# from typing import Any, Dict
#
# from langchain.callbacks import OpenAICallbackHandler
# from langchain.callbacks.openai_info import standardize_model_name
# from langchain.schema import LLMResult
#
# from src.models import LLMCompletionInfo
#
#
# class TokenTracker(OpenAICallbackHandler):
#
#     llm_completion_info: LLMCompletionInfo = LLMCompletionInfo()
#
#     tokens_by_model: Dict[str, LLMCompletionInfo] = {}
#
#     def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
#         super().on_text_generation_end(response, **kwargs)
#
#         model_name = 'default'
#         if response.llm_output is not None and hasattr(response.llm_output, "model_name"):
#             model_name = standardize_model_name(response.llm_output.get("model_name", ""))
#
#         if model_name not in self.tokens_by_model:
#             self.tokens_by_model[model_name] = LLMCompletionInfo()
#
#         completion_info = LLMCompletionInfo(
#             total_tokens=self.total_tokens,
#             prompt_tokens=self.prompt_tokens,
#             completion_tokens=self.completion_tokens,
#             successful_requests=self.successful_requests,
#             total_cost=self.total_cost,
#         )
#         self.tokens_by_model[model_name].add(completion_info)
#         self.llm_completion_info.add(completion_info)
