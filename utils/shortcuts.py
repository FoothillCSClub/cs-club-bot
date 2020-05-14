"""
> ArchiveGlider
> Copyright (c) 2020 Xithrius
> GNU AGPL, Refer to LICENSE for more info
"""


import asyncio
import concurrent.futures
import functools
import os
import sys
import typing as t


def path(*filepath) -> str:
    """Returns absolute path from main caller file to another location.

    Args:
        filepath (iritable): Arguments to add to the current filepath.

    Returns:
        String of filepath with OS based seperator.

    Examples:
        >>> print(path('tmp', 'image.png'))
        C:\\Users\\Xithr\\Documents\\Repositories\\Xythrion\\tmp\\image.png

    """
    lst = [
        os.path.abspath(os.path.dirname(sys.argv[0])),
        (os.sep).join(str(y) for y in filepath)
    ]
    return (os.sep).join(str(s) for s in lst)


def parallel_executor(func: t.Callable) -> t.Coroutine:
    """

    """

    async def run_blocking(func: functools.partial,
                           loop: asyncio.AbstractEventLoop,
                           executor: concurrent.futures.Executor):
        """

        """
        done, pending = await asyncio.wait(
            fs=(loop.run_in_executor(executor, func),),
            return_when=asyncio.FIRST_COMPLETED
        )

        return done.pop().result()

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs) -> None:
        """

        """
        p_func = functools.partial(func, self, *args, **kwargs)
        result = await asyncio.ensure_future(
            run_blocking(p_func, self.bot.loop, self.bot.executor)
        )

        return result

    return wrapper
