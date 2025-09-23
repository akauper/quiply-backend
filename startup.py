import asyncio

from dotenv import load_dotenv

from src.utils.logging import loggers

load_dotenv()

import argparse
from uvicorn import Config, Server

from tools import run_tool

from src.fastapi_app import get_application, QuiplyAPI
from src.settings import quiply_settings


def test():
    pass


tool_names = [
    "load_templates",
    "create_characters",
    "purge",
    "evaluate",
    "download_transformer_models",
    "create_user",
]

tools_requiring_server = {"evaluate"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse arguments for the app.")
    parser.add_argument("--host", type=str, help="Host for the server")
    parser.add_argument("--port", type=int, help="Port for the server")

    for tool_name in tool_names:
        parser.add_argument(
            f"--{tool_name}", nargs="*", help=f"Run the {tool_name} tool"
        )

    parser.add_argument("--force", action="store_true", help="Force the tool to run")

    return parser.parse_args()


async def run_server(app: QuiplyAPI, server_host: str, server_port: int):
    loggers.fastapi.info(f"Running on {server_host}:{server_port}")
    loggers.fastapi.info(f"Reload: {quiply_settings.reload}")

    config = Config(
        app=app,
        host=server_host,
        port=server_port,
        workers=quiply_settings.workers,
        # reload=quiply_settings.reload,
        reload=False,
        timeout_keep_alive=quiply_settings.timeout,
        use_colors=True,
        # log_level='debug'
    )
    server = Server(config)

    # server.run()
    await server.serve()


if __name__ == "__main__":
    try:
        test()

        args = parse_args()

        tool_name = None
        tool_args = []
        for name in tool_names:
            if getattr(args, name) is not None:
                tool_name = name
                tool_args = getattr(args, name)
                break

        host = args.host if args.host else quiply_settings.host
        port = args.port if args.port else quiply_settings.port

        if tool_name:

            def run_tool_callback():
                run_tool(tool_name, args.force, tool_args)

            if tool_name in tools_requiring_server:
                app = get_application([run_tool_callback])
                # run_server(app, host, port)
                asyncio.run(run_server(app, host, port))
            else:
                run_tool_callback()
                exit(0)
        else:
            app = get_application()
            # run_server(app, host, port)
            asyncio.run(run_server(app, host, port))

    except Exception as e:
        print(e)
        raise e
