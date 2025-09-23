import base64
from typing import TYPE_CHECKING, List, Callable

from devtools import debug

from src.framework import SpeechToTextGenerator, DiarizationGenerator
from src.framework.models import Message
from src.models.voice import VoiceTranscript, VoiceStream, VoiceChunk
from src.utils import logger
from src.websocket.connection import WebSocketConnection
from src.websocket.models.events import VoiceTranscriptEvent, PacketEventType, PacketMessageEvent

if TYPE_CHECKING:
    from src.scenario.base import Scenario


CHUNK_COUNT_THRESHOLD = 2

class ScenarioVoiceStreaming:
    scenario: "Scenario"
    websocket_connection: WebSocketConnection
    handle_user_message_callback: Callable[[Message], None]

    stt_generator: SpeechToTextGenerator
    diarization_generator: DiarizationGenerator

    def __init__(
        self,
        scenario: "Scenario",
        websocket_connection: WebSocketConnection,
        handle_user_message_callback: Callable[[Message], None],
    ) -> None:
        self.scenario = scenario
        self.websocket_connection = websocket_connection
        self.handle_user_message_callback = handle_user_message_callback

        websocket_connection.on_voice_stream_start(self._on_voice_stream_start)

        self.stt_generator = SpeechToTextGenerator(process_id=scenario.instance_uid)
        self.diarization_generator = DiarizationGenerator(
            process_id=scenario.instance_uid
        )

    def _on_voice_stream_start(self, stream: VoiceStream):
        self.scenario.create_task(self._handle_audio_stream(stream))

    async def _handle_audio_stream(self, stream: VoiceStream):
        try:
            no_speech_count = 0
            speech_chunks: List[VoiceChunk] = []
            send_chunks: List[VoiceChunk] = []

            async for chunk in stream:
                if not chunk.audio or chunk.audio == "":
                    continue

                audio_bytes = base64.b64decode(chunk.audio)

                diarization_response = await self.diarization_generator.run_async(
                    audio_bytes
                )

                if diarization_response.speaker_count == 0:
                    no_speech_count += 1
                else:
                    speech_chunks.append(chunk)
                    no_speech_count = 0

                    send_chunks.append(chunk)
                    if len(send_chunks) >= CHUNK_COUNT_THRESHOLD:
                        self.scenario.create_task(self._handle_speech(send_chunks.copy()))
                        send_chunks.clear()

                if no_speech_count > 1:
                    no_speech_count = 0
                    if len(speech_chunks) > 0:
                        self.scenario.create_task(self._handle_no_speech(speech_chunks.copy()))
                        speech_chunks.clear()
        except Exception as e:
            logger.exception(e)

    async def _handle_no_speech(self, chunks: List[VoiceChunk]):
        try:
            audio_bytes = self._chunks_to_bytes(chunks)
            stt_response = await self.stt_generator.run_async(audio_bytes)

            debug(f"STT Response: {stt_response.text}")

            message = Message.from_user(
                stt_response.text,
                author_id=self.scenario.user_uid,
                author_name=self.scenario.users_name,
                scenario_instance_id=self.scenario.instance_uid,
            )

            final_transcript: VoiceTranscript = VoiceTranscript(
                stream_id="end",
                chunk_id="end",
                text=stt_response.text,
                is_final=True,
            )
            # await self.websocket_connection.send_voice_async(VoiceTranscriptEvent(data=final_transcript.model_dump()))
            # await self.websocket_connection.send_packet_async(PacketMessageEvent(type=PacketEventType.MESSAGE, data=message))
            await self.websocket_connection.send_async(VoiceTranscriptEvent(data=final_transcript.model_dump()))
            await self.websocket_connection.send_async(PacketMessageEvent(type=PacketEventType.MESSAGE, data=message))

            self.handle_user_message_callback(message)

            # await self.websocket_connection.send_voice_async(VoiceTranscriptEvent(data=message.model_dump()))
            # await self.websocket_connection.send_packet_async(PacketEvent(type=PacketEventType.MESSAGE, data=message)) # LLMPacketEventType.END, message)
            # self.handle_user_message_callback(message)
        except Exception as e:
            logger.exception(e)

    async def _handle_speech(self, chunks: List[VoiceChunk]):
        try:
            audio_bytes = self._chunks_to_bytes(chunks)

            stt_response = await self.stt_generator.run_async(audio_bytes)

            transcript: VoiceTranscript = chunks[0].create_transcript(stt_response.text)
            debug(transcript)
            event: VoiceTranscriptEvent = VoiceTranscriptEvent(data=transcript.model_dump())

            # await self.websocket_connection.send_voice_async(event)
            await self.websocket_connection.send_async(event)
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def _chunks_to_bytes(chunks: List[VoiceChunk]) -> bytes:
        return b"".join([base64.b64decode(chunk.audio) for chunk in chunks])
