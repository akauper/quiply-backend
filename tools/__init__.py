from src.utils import loggers


def run_load_templates(force: bool = False, *args):
    from .app_package import AppPackageTool

    AppPackageTool().run_all(force=force)


def run_create_characters(force: bool = False, *args):
    from .create_characters import CreateCharactersTool

    CreateCharactersTool(
        custom_prompt="",
        temperature=1,
        forbidden_names=[],
    ).run(count=2)


def run_create_user(force: bool = False, *args):
    from .create_user import CreateUserTool

    CreateUserTool().run()

def run_purge(force: bool = False, *args):
    from .purge import PurgeTool, PurgeOptions

    purge_tool = PurgeTool()
    # purge_all(PurgeOptions(
    #     user_id='7BugpH33o6alv7mqphZbRN85ng52',
    #     preserve_recent_count=5
    # ))

    # purge_tool.purge_all_scenario_templates(PurgeOptions(
    #     user_id='7BugpH33o6alv7mqphZbRN85ng52',
    # ))

    purge_tool.purge_scenario_instances(
        PurgeOptions(user_id="7BugpH33o6alv7mqphZbRN85ng52", preserve_recent_count=5)
    )


def run_evaluate(force: bool = False, *args):
    if not args or not args[0]:
        raise ValueError("Evaluation tool requires exactly one argument (yaml file).")

    from .evaluate import EvaluateTool
    evaluate_tool = EvaluateTool()
    evaluate_tool.run_all(rel_file_path=args[0])


def run_download_transformer_models(force: bool = False, *args):
    from .download_transformer_models import DownloadTransformerModelsTool

    DownloadTransformerModelsTool().run_all(force=force)


_lookup = {
    "load_templates": run_load_templates,
    "create_characters": run_create_characters,
    "purge": run_purge,
    "evaluate": run_evaluate,
    "download_transformer_models": run_download_transformer_models,
    "create_user": run_create_user,
}


def run_tool(tool_name: str, force: bool, tool_args: list):
    if tool_name not in _lookup:
        loggers.system.error(f"Unknown tool: {tool_name}")
        exit(1)

    loggers.system.info(f'Running Tool "{tool_name}" with args: {tool_args}')
    try:
        _lookup[tool_name](force, tool_args)
    except Exception as e:
        loggers.system.error(f'Error running "{tool_name}": {e}')
        raise e

    loggers.system.info(f'{tool_name} completed successfully.')
