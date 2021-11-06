import asyncio
import logging
import pathlib
import sys
from typing import Annotated

from examples.common import Config, example_registry

log = logging.getLogger(__name__)


async def run_async(ctx: Config, examples: list[str]) -> Annotated[bool, "Success"]:
    if not examples:
        return await example_registry.run_all(ctx)
    else:
        success = True
        for ex in examples:
            success = success and await example_registry.run(ctx, ex)
        return success


def run():
    # last index of string "examples"
    example_index = sys.argv.index("examples")
    examples = sys.argv[example_index + 1:]

    config_location = pathlib.Path(__file__).parent.resolve().joinpath("./flow.json")
    ctx = Config(config_location)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(run_async(ctx, examples))
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    run()
