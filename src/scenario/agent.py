# import json
# from typing import List, TypeVar, TYPE_CHECKING, AsyncIterable, Dict, Any, Callable, Optional
#
# from typing_extensions import Unpack
#
# from src.scenario.evaluation import AgentEvaluationCallback, truncate_stack, AgentEvaluationExecutor
# from src.models import QMessage, Conversation, QMessageChunk, \
#     AudioResponseBase64, QMessageType, \
#     LanguageModelType, QuiplyLanguageModelKwargs, set_all_q_kwarg_defaults
# from src.services import tts_service
# from src.utils import logger
# from .callback_handlers import AsyncIteratorCallbackHandlerChunked
# from .callback_handlers.streaming_aiter_buffered import ChunkingMethod
# from .memory import BaseConversationMemory, MessageListMemory
# from .models import Character, AgentImpression, QuiplyLanguageModel, AgentMetadata
# from .output_parsers import BidOutputParser
# from ..config import quiply_settings
# from ..config.evaluation import EvaluationMode
# from ..models.websocket import MessageWsEvents, BaseWsEvents
#
# TMemory = TypeVar('TMemory', bound=BaseConversationMemory)
#
# if TYPE_CHECKING:
#     from .base.scenario import Scenario
#
#
#
# class Agent:
#     _scenario: 'Scenario'
#     character: Character
#     memory: TMemory
#     conversation: Conversation  # Conversation and memory need to be separate since memory won't always have all messages
#     is_advisor: bool = False
#     model: QuiplyLanguageModel
#
#     _evaluation_agents: List['Agent'] = []
#
#     @property
#     def evaluation_agents(self) -> List['Agent']:
#         return self._evaluation_agents
#
#     @property
#     def scenario(self) -> 'Scenario':
#         return self._scenario
#
#     def __init__(
#             self,
#             *,
#             scenario: 'Scenario',
#             character: Character,
#             memory: TMemory = None,
#             conversation: Conversation = None,
#             is_advisor: bool = False,
#
#             **language_model_kwargs: Unpack[QuiplyLanguageModelKwargs]
#     ) -> None:
#         self._scenario = scenario
#         self.character = character
#         self.is_advisor = is_advisor
#
#         self.model = self.create_language_model(language_model_kwargs)
#
#         self.memory = memory if memory is not None else MessageListMemory()
#         self.conversation = conversation if conversation is not None else Conversation()
#
#         self.init_memory()
#
#     def create_language_model(self, q_kwargs: QuiplyLanguageModelKwargs) -> QuiplyLanguageModel:
#         set_all_q_kwarg_defaults(q_kwargs)
#
#         t_stop_tokens = [self.character.prefix, "Human:", "AI:"]
#         if 'stop_tokens' in q_kwargs:
#             q_kwargs['stop_tokens'] += t_stop_tokens
#         else:
#             q_kwargs['stop_tokens'] = t_stop_tokens
#
#         agent_metadata_dict: Dict[str, Any] = self.generate_metadata_dict()
#         q_kwargs['runnable_kwargs']['metadata'].update(agent_metadata_dict)
#
#         if quiply_settings.scenario.message_mode == 'stream':
#             q_kwargs['model_kwargs']['streaming'] = True
#
#         return self._scenario.create_language_model(
#             model_type=LanguageModelType.AGENT,
#             **q_kwargs
#         )
#
#     def cleanup(self):
#         # logger.warning('AGENT CLEANUP')
#         self.memory.clear()
#         del self.memory
#         self.conversation.clear()
#         del self.conversation
#
#         del self._scenario
#         del self.character
#
#     def set_evaluation_agents(self, evaluation_agents: List['Agent']):
#         self._evaluation_agents = evaluation_agents
#
#     @property
#     def system_message(self) -> SystemMessage:
#         return self.character.system_message
#
#     def reset(self) -> None:
#         self.memory.clear()
#         self.conversation.clear()
#
#     def init_memory(self) -> None:
#         self.memory.clear()
#         self.conversation.clear()
#
#     def add_message(self, message: QMessage) -> None:
#         self.memory.add_message(message)
#         self.conversation.add_message(message)
#
#         for evaluation_agent in self.evaluation_agents:
#             evaluation_agent.add_message(message)
#
#     @property
#     def last_message(self) -> QMessage:
#         return self.conversation.last_message
#
#     @property
#     def message_list(self) -> List[QMessage]:
#         return self.conversation.messages
#
#     @property
#     def messages_str(self) -> str:
#         return self.conversation.format_string()
#
#     @property
#     def prompt(self) -> PromptTemplate:
#         return PromptTemplate.from_template(
#             template=f"""{self.system_message.content}
#
# The Conversation So Far:
# {{chat_history}}
# {self.character.prefix}""")
#
#     # @property
#     # def prompt(self):
#     #     return ChatPromptTemplate.from_messages([
#     #         SystemMessage(content=self.system_message.content),
#     #         MessagesPlaceholder(variable_name='chat_history'),
#     #     ])
#
#     def generate_metadata_dict(
#             self,
#             user_message: Optional[QMessage] = None,
#             outer_stack: Optional[List[Any]] = None
#     ) -> Dict[str, Any]:
#         import inspect
#         stack = inspect.stack()
#         stack = truncate_stack(stack)
#         if outer_stack is not None:
#             stack += truncate_stack(outer_stack)
#         metadata = AgentMetadata(
#             character=self.character,
#             scenario_instance=self._scenario.scenario_instance,
#             user_message=user_message,
#             stack=stack,
#         ).model_dump()
#         return metadata
#
#     async def stream_async(
#             self,
#             user_message: Optional[QMessage] = None,
#             outer_stack: Optional[List[Any]] = None,
#             **q_kwargs: Unpack[QuiplyLanguageModelKwargs]
#     ) -> QMessage:
#         return await self._call(
#             self._stream_async,
#             user_message=user_message,
#             outer_stack=outer_stack,
#             **q_kwargs
#         )
#
#     async def predict_async(
#             self,
#             user_message: Optional[QMessage] = None,
#             outer_stack: Optional[List[Any]] = None,
#             **q_kwargs: Unpack[QuiplyLanguageModelKwargs]
#     ) -> QMessage:
#         return await self._call(
#             self._predict_async,
#             user_message=user_message,
#             outer_stack=outer_stack,
#             **q_kwargs
#         )
#
#     async def _call(
#             self,
#             func: Callable,
#             user_message: Optional[QMessage] = None,
#             outer_stack: Optional[List[Any]] = None,
#             **q_kwargs: Unpack[QuiplyLanguageModelKwargs]
#     ) -> QMessage:
#         do_eval = quiply_settings.evaluation.enabled and quiply_settings.evaluation.mode == EvaluationMode.multi_prompt
#         runnable_kwargs = q_kwargs.setdefault('runnable_kwargs', {})
#         runnable_kwargs.setdefault('callbacks', [])
#         runnable_kwargs.setdefault('metadata', {})
#
#         if do_eval:
#             metadata = self.generate_metadata_dict(user_message, outer_stack)
#             runnable_kwargs['metadata'].update(metadata)
#
#             executors = [AgentEvaluationExecutor(eval_agent, **q_kwargs) for eval_agent in self._evaluation_agents]
#
#             eval_callback = AgentEvaluationCallback(scenario=self._scenario)
#             runnable_kwargs['callbacks'] += [eval_callback]
#
#         result = await func(
#             allow_tts=quiply_settings.scenario.allow_tts,
#             send_to_client=True,
#             **q_kwargs
#         )
#
#         if do_eval:
#             coroutines = [executor.execute_async(eval_callback) for executor in executors]
#             self._scenario.async_manager.gather_and_create_task(coroutines)
#
#         return result
#
#     async def _stream_async(
#             self,
#             *,
#             allow_tts: bool = True,
#             send_to_client: bool = True,
#             **q_kwargs: Unpack[QuiplyLanguageModelKwargs]
#     ) -> QMessage:
#         if not send_to_client:
#             allow_tts = False
#
#         output_message = self.character.str_to_message(content="", message_type=QMessageType.ai, has_audio=allow_tts)
#
#         text_handler = AsyncIteratorCallbackHandler()
#         audio_handler = None
#
#         runnable_kwargs = q_kwargs.setdefault('runnable_kwargs', {})
#         runnable_kwargs.setdefault('callbacks', [])
#         runnable_kwargs['callbacks'] = runnable_kwargs['callbacks'] + [text_handler] + self._scenario.callbacks
#
#         if allow_tts:
#             audio_handler = AsyncIteratorCallbackHandlerChunked(
#                 chunking_method=ChunkingMethod.SENTENCE,
#                 chunk_size=1,
#                 for_first_chunks=3,
#                 then_chunk_size=2,
#             )
#             runnable_kwargs['callbacks'] = runnable_kwargs['callbacks'] + [audio_handler]
#
#         chain = self.model.chain(
#             chain_kwargs={
#                 'prompt': self.prompt,
#                 'memory': self.memory,
#             },
#             **q_kwargs
#         )
#
#         coroutine = chain.apredict()
#
#         self._scenario.async_manager.create_task(coroutine)
#
#         async def audio_task():
#             async def stream_audio_func(audio_generator: AsyncIterable[AudioResponseBase64]):
#                 async for chunk in audio_generator:
#                     chunk.message_uid = output_message.id
#                     # print('sending audio chunk', chunk)
#                     await self._scenario.websocket_connection.send_message_async(MessageWsEvents.AUDIO, chunk)
#
#             await tts_service.text_to_speech_input_streaming(
#                 voice_id=self.character.template.selected_voice_id,
#                 text_iterator=audio_handler.aiter(),
#                 stream_audio_func=stream_audio_func,  # Pass through to our websocket connection
#             )
#
#         async def text_task():
#             if send_to_client:
#                 await self._scenario.websocket_connection.send_message_async(MessageWsEvents.START, output_message)
#
#             async for chunk_str in text_handler.aiter():
#                 output_message.content += chunk_str
#                 if send_to_client:
#                     chunk = QMessageChunk(message_uid=output_message.id, content=chunk_str)
#                     await self._scenario.websocket_connection.send_message_async(MessageWsEvents.CHUNK, data=chunk)
#
#         text_task = self._scenario.async_manager.create_task(text_task())
#
#         tts_task = None
#         if allow_tts:
#             tts_task = self._scenario.async_manager.create_task(audio_task())
#
#         await text_task
#
#         if send_to_client:
#             self._on_generated_message(output_message)
#             self._scenario.websocket_connection.create_message_task(MessageWsEvents.END, output_message)
#
#         if tts_task:
#             await tts_task
#
#         return output_message
#
#     async def _predict_async(
#             self,
#             allow_tts: bool = True,
#             send_to_client: bool = True,
#             **q_kwargs: Unpack[QuiplyLanguageModelKwargs]
#     ) -> QMessage:
#         if not send_to_client:
#             allow_tts = False
#
#         if send_to_client:
#             self._scenario.websocket_connection.create_base_task(BaseWsEvents.TYPING_START, data=self.character.template.uid)
#
#         chain = self.model.chain(
#             chain_kwargs={
#                 'prompt': self.prompt,
#                 'memory': self.memory,
#             },
#             **q_kwargs
#         )
#         output_str = await chain.apredict()
#         output_message = self.character.str_to_message(
#             content=output_str,
#             message_type=QMessageType.ai if not self.is_advisor else QMessageType.advisor,
#             has_audio=allow_tts,
#         )
#
#         if send_to_client:
#             self._handle_predict_output(output_message, allow_tts)
#         return output_message
#
#     def send_pregenerated_message(
#             self,
#             content: str,
#             message_type: QMessageType = 'ai',
#     ) -> QMessage:
#         output_message = self.character.str_to_message(
#             content=content,
#             message_type=message_type,
#             has_audio=False,
#         )
#         self._handle_predict_output(output_message, tts=quiply_settings.scenario.allow_tts)
#         return output_message
#
#     def _handle_predict_output(
#             self,
#             output_message: QMessage,
#             tts: bool = False,
#             tts_stream: bool = True
#     ):
#         self._on_generated_message(output_message)
#         self._scenario.websocket_connection.create_message_task(MessageWsEvents.FULL_MESSAGE, output_message)
#
#         if tts:
#             if tts_stream:
#                 async def stream_audio_async():
#                     audio_generator = await tts_service.text_to_speech_async_stream_output(
#                         output_message.content,
#                         self.character.template.selected_voice_id
#                     )
#                     async for audio_chunk in audio_generator:
#                         audio_chunk.message_uid = output_message.id
#                         await self._scenario.websocket_connection.send_message_async(MessageWsEvents.AUDIO, audio_chunk)
#                 self._scenario.async_manager.create_task(stream_audio_async())
#             else:
#                 async def send_audio_async():
#                     audio_data = await tts_service.text_to_speech_async(
#                         output_message.content,
#                         self.character.template.selected_voice_id
#                     )
#                     audio_data.message_uid = output_message.id
#                     await self._scenario.websocket_connection.send_message_async(MessageWsEvents.AUDIO, audio_data)
#                 self._scenario.async_manager.create_task(send_audio_async())
#         return output_message
#
#     def _on_generated_message(self, output_message: QMessage):
#         if self.is_advisor:
#             self._scenario.on_advisor_message(output_message)
#         else:
#             self._scenario.on_agent_message(output_message)
#
#     async def get_impression_async(self) -> AgentImpression | None:
#         model = self._scenario.instruct_model
#         prompt = prompts.agent_impression
#         _input = prompt.format(
#             character_name=self.character.name,
#             users_name=self._scenario.users_name,
#             conversation_history=self.messages_str,
#             format_instructions=AgentImpression.get_format_instructions()
#         )
#         response = await model.invoke_async(_input)
#         print('get impression response', response)
#         try:
#             data = json.loads(response)
#             return AgentImpression(
#                 character_name=self.character.name,
#                 impression=data['impression'],
#                 reasoning=data['reasoning'],
#             )
#         except Exception as e:
#             logger.error(f"Error parsing response: {e}")
#             return None
#
#     async def bid_async(self, prompt: PromptTemplate = None) -> int:
#         """Ask the chat model to output a bid to speak."""
#
#         if prompt is None:
#             prompt = prompts.bid.get_prompt
#
#         model = self._scenario.instruct_model
#         bid_output_parser = BidOutputParser()
#         _input = prompt.format(
#             system_message=self.system_message.content,
#             chat_history=self.messages_str,
#             format_instructions=bid_output_parser.get_format_instructions()
#         )
#         output_str = await model.invoke_async(_input)
#         bid = int(bid_output_parser.parse(output_str)["bid"])
#         return bid
