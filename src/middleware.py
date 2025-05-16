from typing import Callable, Awaitable
import defines
import blacksheep

async def authorization(request: blacksheep.Request,
                        next_handler : Callable[[blacksheep.Request], Awaitable[blacksheep.Response]]) -> blacksheep.Response:
    token = request.headers.get_first(b"Authorization") or b""
    if token.startswith(b"Bearer "):
        token = token[7:]
    
    if token.decode("ascii") != defines.PASSWORD:
        raise blacksheep.HTTPException(401, "Unauthorized")
    
    return await next_handler(request)
