# from typing import Optional, Any, Dict, List
# from uuid import UUID
#
# from langchain.callbacks.base import BaseCallbackHandler
# from langchain.schema.messages import BaseMessage
# from langchain.schema.output import LLMResult
#
# from src.utils import logger
# from src.utils.logging import loggers
#
#
# class DebugHandler(BaseCallbackHandler):
#
#     def on_llm_end(
#             self,
#             response: LLMResult,
#             *,
#             run_id: UUID,
#             parent_run_id: Optional[UUID] = None,
#             **kwargs: Any,
#     ) -> Any:
#         # logger.log_llm_prompt(f'LLM END: {response.generations[0][0].text}')
#         pass
#
#     def on_llm_error(
#             self,
#             error: BaseException,
#             *,
#             run_id: UUID,
#             parent_run_id: Optional[UUID] = None,
#             **kwargs: Any,
#     ) -> Any:
#         loggers.llm.exception(error)
#
#     def on_llm_start(
#             self,
#             serialized: Dict[str, Any],
#             prompts: List[str],
#             *,
#             run_id: UUID,
#             parent_run_id: Optional[UUID] = None,
#             tags: Optional[List[str]] = None,
#             metadata: Optional[Dict[str, Any]] = None,
#             **kwargs: Any,
#     ) -> Any:
#         loggers.llm.info(f'LLM START: {prompts[0]}')
#
#     def on_chat_model_start(
#         self,
#         serialized: Dict[str, Any],
#         messages: List[List[BaseMessage]],
#         *,
#         run_id: UUID,
#         parent_run_id: Optional[UUID] = None,
#         tags: Optional[List[str]] = None,
#         metadata: Optional[Dict[str, Any]] = None,
#         **kwargs: Any,
#     ) -> Any:
#         """Run when a chat model starts running."""
#         loggers.llm.info(f"""
# CHAT MODEL START: {messages[0][0].content}
# """)