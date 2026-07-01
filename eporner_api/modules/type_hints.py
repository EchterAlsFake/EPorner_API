from typing import Callable, Awaitable

type on_error_hint = Callable[[str, Exception, int], Awaitable[bool]] | None