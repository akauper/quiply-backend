import asyncio
import json
import time
from datetime import datetime
from typing import Optional, Union, Any

from devtools import debug
from pydantic import Field, model_validator

from framework import framework_settings
from src.framework import Agent, prompts, Message, Conversation, \
    MessageAudioChunk, MessageAudio, MessageChunk, Prompt, MessageRole, TextGenerationRequest
from src.models import ActorSchema, MentorSchema
from src.scenario.models import AgentImpression, AgentType
from src.utils import logger
from src.websocket import ScenarioTypingStartEvent, PacketStreamEndEvent, PacketAudioEvent, PacketStreamChunkEvent, \
    PacketStreamStartEvent, PacketMessageEvent


class ScenarioAgent(Agent):
    template: Union[ActorSchema, MentorSchema]
    type: AgentType = Field(default=AgentType.AGENT)

    scenario: Any

    full_conversation: Conversation = Field(default_factory=Conversation)
    personality: str = Field(default='')

    @model_validator(mode='after')
    def validate_data(self) -> None:
        if not self:
            return
        if self.scenario is None:
            raise ValueError('Scenario cannot be None')

        self.text_generator.generation_params.stop += [self.prefix, self.scenario.users_prefix]

    @property
    def id(self) -> str:
        return self.template.uid

    @property
    def name(self) -> str:
        return self.template.name

    @property
    def prefix(self) -> str:
        return f"{self.name}: "

    def cleanup(self) -> None:
        self.full_conversation.clear()
        del self.full_conversation

        del self.scenario
        super().cleanup()

    def add_message(self, message: TextGenerationRequest) -> None:
        super().add_message(message)
        if isinstance(message, list):
            for msg in message:
                self.full_conversation.add_message(msg)
        elif isinstance(message, Message):
            self.full_conversation.add_message(message)
        elif isinstance(message, str):
            self.full_conversation.add_message(Message.from_user(message))

    async def run_async(
            self,
            request: Optional[TextGenerationRequest] = None,
            **kwargs
    ) -> Message:
        def do_audio_callback(audio: MessageAudio):
            # self.scenario.websocket_connection.create_packet_task(PacketEventType.AUDIO, data=audio)
            pass

        try:
            # self.scenario.websocket_connection.create_scenario_task(ScenarioTypingStartEvent(data=self.template.uid))
            self.scenario.websocket_connection.create_send_task(ScenarioTypingStartEvent(data=self.template.uid))

            # audio_callback = do_audio_callback if quiply_settings.services.tts.enabled else None
            audio_callback = do_audio_callback if framework_settings.runnables.generators.audio.enabled else None
            message = await super().run_async(request, audio_callback=audio_callback)

            # Set the correct agent information for the message
            message.author_id = self.template.uid
            message.author_name = self.template.name
            message.scenario_instance_id = self.scenario.instance_uid
            if self.type == AgentType.MENTOR:
                message.role = MessageRole.mentor
                # message.metadata.setdefault('from_advisor', True)

            # await self.scenario.websocket_connection.send_message_async(LLMPacketEventType.FULL_MESSAGE, data=message)
            # await self.scenario.websocket_connection.send_packet_async(PacketMessageEvent(data=message))
            await self.scenario.websocket_connection.send_async(PacketMessageEvent(data=message))

            if self.type == AgentType.MENTOR:
                self.scenario.lifecycle_manager.on_advisor_message(message)
            else:
                self.scenario.lifecycle_manager.on_agent_message(message)

            return message
        except Exception as e:
            logger.error(f'Error running agent: {e}')
            raise e

    async def run_async_stream(
            self,
            request: Optional[TextGenerationRequest] = None,
            **kwargs
    ) -> Message:
        async def send_start_message_delayed():
            nonlocal sent_start_message

            delay = 2.5
            last_message = self.full_conversation.last_message
            if last_message and last_message.is_from(MessageRole.user):
                time_since_last_message = time.time() - datetime.fromisoformat(last_message.created_at).timestamp()
                delay = max(delay - time_since_last_message, 0)

            print(delay)
            await asyncio.sleep(delay)

            if not sent_start_message:
                thinking_message = injected_message.model_copy()
                thinking_message.content = ''
                thinking_message.metadata.setdefault('is_thinking', True)

                sent_start_message = True
                # await self.scenario.websocket_connection.send_packet_async(PacketStreamStartEvent(data=thinking_message))
                await self.scenario.websocket_connection.send_async(PacketStreamStartEvent(data=thinking_message))

        def text_callback(chunk: MessageChunk):
            if chunk.index == 0:
                nonlocal sent_start_message

                if not sent_start_message:
                    zero_content_message = injected_message.model_copy()
                    zero_content_message.content = ''

                    sent_start_message = True
                    # self.scenario.websocket_connection.create_packet_task(PacketStreamStartEvent(data=zero_content_message))
                    self.scenario.websocket_connection.create_send_task(PacketStreamStartEvent(data=zero_content_message))

            # self.scenario.websocket_connection.create_packet_task(PacketStreamChunkEvent(data=chunk))
            self.scenario.websocket_connection.create_send_task(PacketStreamChunkEvent(data=chunk))

        def audio_callback(chunk: MessageAudioChunk):
            # self.scenario.websocket_connection.create_packet_task(PacketAudioEvent(data=chunk))
            self.scenario.websocket_connection.create_send_task(PacketAudioEvent(data=chunk))

        try:
            sent_start_message = False
            # self.scenario.websocket_connection.create_scenario_task(ScenarioTypingStartEvent(data=self.template.uid))
            self.scenario.websocket_connection.create_send_task(ScenarioTypingStartEvent(data=self.template.uid))

            # This sets the correct starting message
            injected_message = Message.from_ai(
                content='',
                author_id=self.template.uid,
                author_name=self.template.name,
                scenario_instance_id=self.scenario.instance_uid,
                from_advisor=self.type == AgentType.MENTOR,
            )

            self.scenario.create_task(send_start_message_delayed())

            # await asyncio.sleep(10)

            message = await super().run_async_stream(
                request,
                injected_message=injected_message,
                message_chunk_callback=text_callback,
                # audio_chunk_callback=audio_callback if quiply_settings.services.tts.enabled else None,
                audio_chunk_callback=audio_callback if framework_settings.runnables.generators.audio.enabled else None,
            )

            # await self.scenario.websocket_connection.send_packet_async(PacketStreamEndEvent(data=message))
            await self.scenario.websocket_connection.send_async(PacketStreamEndEvent(data=message))

            if self.type == AgentType.MENTOR:
                self.scenario.lifecycle_manager.on_advisor_message(message)
            else:
                self.scenario.lifecycle_manager.on_agent_message(message)
        except Exception as e:
            logger.error(f'Error running agent stream: {e}')
            raise e

        return message

    async def send_pregenerated_message(
            self,
            content: str,
            **metadata,
    ) -> Message:
        def do_audio_callback(audio: MessageAudio):
            # self.scenario.websocket_connection.create_packet_task(PacketEventType.AUDIO, data=audio)
            pass

        # audio_callback = do_audio_callback if quiply_settings.scenario.allow_tts else None
        audio_callback = do_audio_callback if framework_settings.runnables.generators.speech_to_text.enabled else None

        message = Message.from_ai(
            content=content,
            author_id=self.template.uid,
            author_name=self.template.name,
            scenario_instance_id=self.scenario.instance_uid,
            **metadata,
        )

        if self.runnable_params.verbose:
            debug(self, request=content)

        if audio_callback:
            if not self.audio_generator:
                logger.warning('Audio response callback provided but no audio generator is set. Audio will not be generated.')
            else:
                audio_response = await self.audio_generator.run_async(content)
                message_audio = MessageAudio(
                    message_id=message.id,
                    audio=audio_response.audio,
                    normalized_alignment=audio_response.normalized_alignment
                )
                audio_callback(message_audio)
                message.audio_id = message_audio.id

        self.memory.save(message)

        # await self.scenario.websocket_connection.send_message_async(LLMPacketEventType.FULL_MESSAGE, data=message)
        # await self.scenario.websocket_connection.send_packet_async(PacketMessageEvent(data=message))
        await self.scenario.websocket_connection.send_async(PacketMessageEvent(data=message))

        if self.type == AgentType.MENTOR:
            self.scenario.lifecycle_manager.on_advisor_message(message)
        else:
            self.scenario.lifecycle_manager.on_agent_message(message)

        return message

    async def get_impression_async(self) -> Optional[AgentImpression]:
        prompt = prompts.agent_impression
        _input = prompt.format(
            character_name=self.name,
            users_name=self.scenario.users_name,
            conversation_history=self.full_conversation.to_string(),
            format_instructions=AgentImpression.get_format_instructions()
        )
        response = await self.text_generator.run_async(_input)
        print('get impression response', response)
        try:
            data = json.loads(response.content)
            return AgentImpression(
                character_name=self.name,
                impression=data['impression'],
                reasoning=data['reasoning'],
            )
        except Exception as e:
            logger.error(f'Error parsing agent impression response: {e}')
            return None

    async def bid_async(self, prompt: Prompt) -> int:
        raise NotImplementedError('ScenarioAgent.bid_async() is not implemented')

        # if prompt is None:
        #     prompt = prompts.bid.get_prompt
        #
        # model = self._scenario.instruct_model
        # bid_output_parser = BidOutputParser()
        # _input = prompt.format(
        #     system_message=self.system_message.content,
        #     chat_history=self.messages_str,
        #     format_instructions=bid_output_parser.get_format_instructions()
        # )
        # output_str = await model.invoke_async(_input)
        # bid = int(bid_output_parser.parse(output_str)["bid"])
        # return bid
