# import asyncio
# from enum import Enum
# from typing import Any, AsyncIterator, Dict, List
#
# from langchain.callbacks.base import AsyncCallbackHandler
# from langchain.schema.output import LLMResult
#
#
# class ChunkingMethod(Enum):
#     """Enum for the different chunking methods."""
#     NONE = "none"
#     TOKEN = "token"
#     CHARACTER = "character"
#     WORD = "word"
#     SENTENCE = "sentence"
#
#
# class ChunkBuffer:
#     def __init__(
#             self,
#             chunking_method: ChunkingMethod,
#             chunk_size: int,
#             for_first_chunks: int,
#             then_chunk_size: int,
#     ):
#         self.initial_chunk_size = chunk_size
#         self.for_first_chunks = for_first_chunks
#         self.then_chunk_size = then_chunk_size
#         self.chunking_method = chunking_method
#         self.buffer = []
#         self.word_splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
#         self.sentence_splitters = (".", "?", "!")
#         self.chunks_yielded = 0
#
#     @property
#     def chunk_size(self):
#         if self.for_first_chunks <= 0 or self.chunks_yielded < self.for_first_chunks:
#             return self.initial_chunk_size
#         else:
#             return self.then_chunk_size
#
#     def add(self, token: str):
#         if self.chunking_method == ChunkingMethod.NONE or self.chunking_method == ChunkingMethod.TOKEN:
#             self.buffer.append(token)
#         elif self.chunking_method == ChunkingMethod.CHARACTER:
#             self.buffer.extend(token)
#         elif self.chunking_method == ChunkingMethod.WORD:
#             self._add_word(token)
#         elif self.chunking_method == ChunkingMethod.SENTENCE:
#             self._add_sentence(token)
#
#     def _add_word(self, token: str):
#         if token.startswith(" ") or len(self.buffer) == 0 or self.buffer[-1].endswith(self.word_splitters):
#             self.buffer.append(token)
#         else:
#             self.buffer[-1] += token
#
#     def _add_sentence(self, token: str):
#         if len(self.buffer) == 0 or self.buffer[-1].endswith(self.sentence_splitters):
#             self.buffer.append(token)
#         else:
#             self.buffer[-1] += token
#
#     def get_chunk(self):
#         if self.chunking_method == ChunkingMethod.NONE:
#             return self.flush()
#         else:
#             chunk = ''.join(self.buffer[:self.chunk_size])
#             self.buffer = self.buffer[self.chunk_size:]
#             self.chunks_yielded += 1
#             print('yielding chunk', chunk)
#             return chunk
#
#     def has_chunk(self):
#         if self.chunking_method is ChunkingMethod.SENTENCE:
#             return len(self.buffer) > self.chunk_size
#         return len(self.buffer) >= self.chunk_size
#
#     def flush(self):
#         self.chunks_yielded += 1
#         return ''.join(self.buffer)
#
#
# class AsyncIteratorCallbackHandlerChunked(AsyncCallbackHandler):
#     """Callback handler that returns an async iterator."""
#
#     queue: asyncio.Queue[str]
#     done: asyncio.Event
#     chunk_buffer: ChunkBuffer
#     chunking_method: ChunkingMethod
#     chunk_size: int
#     for_first_chunks: int
#     then_chunk_size: int
#
#     @property
#     def always_verbose(self) -> bool:
#         return True
#
#     def __init__(
#             self,
#             chunking_method: ChunkingMethod = ChunkingMethod.NONE,
#             chunk_size: int = 10,
#             for_first_chunks: int = 0,
#             then_chunk_size: int = 10,
#     ) -> None:
#         self.queue = asyncio.Queue()
#         self.done = asyncio.Event()
#         self.chunking_method = chunking_method
#         self.chunk_size = chunk_size
#         self.for_first_chunks = for_first_chunks
#         self.then_chunk_size = then_chunk_size
#         self.chunk_buffer = ChunkBuffer(chunking_method, chunk_size, for_first_chunks, then_chunk_size)
#
#     async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
#         # If two calls are made in a row, this resets the state
#         self.done.clear()
#
#     async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
#         if token is not None and token != "":
#             self.queue.put_nowait(token)
#
#     async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
#         self.done.set()
#
#     async def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
#         self.done.set()
#
#     async def aiter(self) -> AsyncIterator[str]:
#         while not self.queue.empty() or not self.done.is_set():
#             # Wait for the next token in the queue,
#             # but stop waiting if the done event is set
#             done, other = await asyncio.wait(
#                 [
#                     asyncio.ensure_future(self.queue.get()),
#                     asyncio.ensure_future(self.done.wait()),
#                 ],
#                 return_when=asyncio.FIRST_COMPLETED,
#             )
#
#             # Cancel the other task
#             if other:
#                 other.pop().cancel()
#
#             # Extract the value of the first completed task
#             token_or_done = done.pop().result()
#
#             # If the extracted value is the boolean True, the done event was set
#             if token_or_done is True:
#                 break
#
#             self.chunk_buffer.add(token_or_done)
#
#             # print('got token', token_or_done)
#
#             while self.chunk_buffer.has_chunk():
#                 yield self.chunk_buffer.get_chunk()
#
#         # Yield the remaining data in the buffer
#         remaining_data = self.chunk_buffer.flush()
#         if remaining_data:
#             yield remaining_data
#
# # class AsyncIteratorCallbackHandlerChunked(AsyncCallbackHandler):
# #     """Callback handler that returns an async iterator."""
# #
# #     queue: asyncio.Queue[str]
# #     done: asyncio.Event
# #     token_buffer: List[str]
# #     character_buffer: str
# #     words_buffer: List[str]
# #     sentences_buffer: List[str]
# #     chunking_method: ChunkingMethod
# #     chunk_size: int
# #
# #     @property
# #     def always_verbose(self) -> bool:
# #         return True
# #
# #     def __init__(self, chunking_method: ChunkingMethod = ChunkingMethod.NONE, chunk_size: int = 10) -> None:
# #         self.queue = asyncio.Queue()
# #         self.done = asyncio.Event()
# #         self.token_buffer = []
# #         self.character_buffer = ""
# #         self.words_buffer = []
# #         self.sentences_buffer = []
# #         self.chunking_method = chunking_method
# #         self.chunk_size = chunk_size
# #
# #     async def on_llm_start(
# #         self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
# #     ) -> None:
# #         # If two calls are made in a row, this resets the state
# #         self.done.clear()
# #
# #     async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
# #         if token is not None and token != "":
# #             self.queue.put_nowait(token)
# #
# #     async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
# #         self.done.set()
# #
# #     async def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
# #         self.done.set()
# #
# #     # TODO implement the other methods
# #
# #     async def aiter(self) -> AsyncIterator[str]:
# #         while not self.queue.empty() or not self.done.is_set():
# #             # Wait for the next token in the queue,
# #             # but stop waiting if the done event is set
# #             done, other = await asyncio.wait(
# #                 [
# #                     # NOTE: If you add other tasks here, update the code below,
# #                     # which assumes each set has exactly one task each
# #                     asyncio.ensure_future(self.queue.get()),
# #                     asyncio.ensure_future(self.done.wait()),
# #                 ],
# #                 return_when=asyncio.FIRST_COMPLETED,
# #             )
# #
# #             # Cancel the other task
# #             if other:
# #                 other.pop().cancel()
# #
# #             # Extract the value of the first completed task
# #             token_or_done = cast(Union[str, Literal[True]], done.pop().result())
# #
# #             # If the extracted value is the boolean True, the done event was set
# #             if token_or_done is True:
# #                 break
# #
# #             token = token_or_done
# #
# #             print('got token', token)
# #
# #             if self.chunking_method == ChunkingMethod.NONE:
# #                 yield token
# #                 continue
# #
# #             if self.chunking_method == ChunkingMethod.TOKEN:
# #                 self.token_buffer.append(token)
# #                 while len(self.token_buffer) >= self.chunk_size:
# #                     chunk = "".join(self.token_buffer[:self.chunk_size])
# #                     yield chunk
# #                     self.token_buffer = self.token_buffer[self.chunk_size:]
# #             if self.chunking_method == ChunkingMethod.CHARACTER:
# #                 self.character_buffer += token
# #                 while len(self.character_buffer) >= self.chunk_size:
# #                     chunk = self.character_buffer[:self.chunk_size]
# #                     yield chunk
# #                     self.character_buffer = self.character_buffer[self.chunk_size:]
# #             elif self.chunking_method == ChunkingMethod.WORD:
# #                 splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
# #                 if token.startswith(" ") or len(self.words_buffer) == 0 or self.words_buffer[-1].endswith(splitters):
# #                     self.words_buffer.append(token)
# #                 else:
# #                     self.words_buffer[-1] += token
# #                 while len(self.words_buffer) >= self.chunk_size:
# #                     chunk = "".join(self.words_buffer[:self.chunk_size])
# #                     yield chunk
# #                     self.words_buffer = self.words_buffer[self.chunk_size:]
# #             elif self.chunking_method == ChunkingMethod.SENTENCE:
# #                 splitters = (".", "?", "!")
# #                 if len(self.sentences_buffer) == 0 or self.sentences_buffer[-1].endswith(splitters):
# #                     self.sentences_buffer.append(token)
# #                 else:
# #                     self.sentences_buffer[-1] += token
# #                 while len(self.sentences_buffer) > self.chunk_size:
# #                     chunk = "".join(self.sentences_buffer[:self.chunk_size])
# #                     yield chunk
# #                     self.sentences_buffer = self.sentences_buffer[self.chunk_size:]
# #
# #         # Yield the remaining data in the buffers
# #         if self.chunking_method == ChunkingMethod.CHARACTER and self.character_buffer:
# #             yield self.character_buffer
# #         elif self.chunking_method == ChunkingMethod.WORD and self.words_buffer:
# #             yield "".join(self.words_buffer)
# #         elif self.chunking_method == ChunkingMethod.SENTENCE and self.sentences_buffer:
# #             yield "".join(self.sentences_buffer)
