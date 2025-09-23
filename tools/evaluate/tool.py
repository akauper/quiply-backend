import asyncio
from typing import Any

from src.framework.evaluation import Evaluator
from ..base_tool import BaseTool


class EvaluateTool(BaseTool):

    def run_all(self, **kwargs: Any) -> None:
        rel_file_paths = kwargs.get('rel_file_path')
        for path in rel_file_paths:
            self.run(rel_file_path=path)

    def run(self, rel_file_path: str):
        # return asyncio.run(self.run_async(rel_file_path))
        return asyncio.create_task(self.run_async(rel_file_path))

    @staticmethod
    async def run_async(rel_file_path: str):
        evaluators = Evaluator.load(rel_file_path)
        for evaluator in evaluators:
            await evaluator.evaluate_async()
