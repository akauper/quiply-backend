import asyncio
import os
import re
from typing import List, Optional

from pydantic import Field

from src.framework import TextGenerator, TextGenerationParams, Prompt

from src.utils import logger
from .constants import PROMPT_TEMPLATE, PROMPT_FORMAT_INSTRUCTIONS, ACTOR_TEMPLATE_DECLARATION, \
    DATA_DIR, HEADER
from ..base_tool import BaseTool


class CreateCharactersTool(BaseTool):
    custom_prompt: Optional[str] = Field(default=None),
    temperature: float = Field(default=0.7),
    top_p: Optional[float] = Field(default=None, ge=0, le=1),
    frequency_penalty: Optional[float] = Field(default=None, ge=-2, le=2),
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2, le=2),
    forbidden_names: Optional[List[str]] = Field(default=None),
    model_name: str = Field(default='gpt-4-1106-preview')  # 'gpt-4'

    def run_all(self, **kwargs) -> None:
        count = kwargs.get('count', 2)
        self.run(count=count)

    def run(self, count) -> asyncio.Task:
        return asyncio.create_task(self.run_async(count=count))

    async def run_async(self, count) -> List[str]:
        if not os.path.isdir(DATA_DIR):
            logger.error(f"Data directory {DATA_DIR} does not exist.")
            return []

        if self.forbidden_names is not None and len(self.forbidden_names) > 0:
            forbidden_names_prompt = 'DO NOT USE THE FOLLOWING NAMES' + ', '.join(self.forbidden_names)
        else:
            forbidden_names_prompt = ''

        logger.info(f'Creating {count} actor templates...')
        tasks = [self.create_actor_template_async(forbidden_names_prompt) for _ in range(count)]
        templates = await asyncio.gather(*tasks)

        actor_names = []

        for idx, template in enumerate(templates):
            match = re.search(r"name\s*=\s*['\"]([^'\"]+)['\"]", template)
            if match:
                actor_name = match.group(1)
            else:
                actor_name = f"actor_{idx + 1}"
            actor_names.append(actor_name + '.py')
            self.save_to_file(actor_name.lower(), template)

        print(f"Created {count} actor templates: {actor_names}")
        return list(map(str, templates))

    async def create_actor_template_async(self, forbidden_names_prompt: str) -> str:
        params = TextGenerationParams(
            model=self.model_name,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
        )
        text_generator = TextGenerator(generation_params=params)
        prompt = Prompt(template=PROMPT_TEMPLATE)
        _input = prompt.format(
            custom_prompt=self.custom_prompt,
            names_prompt=forbidden_names_prompt,
            actor_template_declaration=ACTOR_TEMPLATE_DECLARATION,
            format_instructions=PROMPT_FORMAT_INSTRUCTIONS
        )
        response = await text_generator.run_async(_input)

        return HEADER.format(response=response.content)

    @staticmethod
    def save_to_file(actor_name: str, template: str):
        file_path = os.path.join(DATA_DIR, f"{actor_name}.py")

        if os.path.exists(file_path):
            count = 1
            while os.path.exists(file_path):
                file_path = os.path.join(DATA_DIR, f"{actor_name}_{count}.py")
                count += 1

        try:
            with open(file_path, "wb") as f:
                template_crlf = template.replace("\n", "\r\n")
                f.write(template_crlf.encode('utf-8'))
                print(f"Saved {actor_name} to {file_path}")
        except Exception as e:
            logger.error(f"Error saving {actor_name} to {file_path}: {e}")
            print(e)
