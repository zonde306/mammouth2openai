import time
import json
import logging
import defines
import service
import middleware
import blacksheep

logger = logging.getLogger(__name__)
app = blacksheep.Application()

app.middlewares.append(middleware.authorization)


@blacksheep.get("/v1/models")
async def models(request : blacksheep.Request) -> blacksheep.Response:
    return blacksheep.json({
        "object": "list",
        "data": [
            {
                "id": model,
                "object": "model",
                "name": model,
                "created": int(time.time()),
                "owned_by": "mammouth",
            }
            for model in defines.MODELS
        ],
    })

@blacksheep.post("/v1/chat/completions")
async def chat_completions(request : blacksheep.Request) -> blacksheep.Response:
    data : dict = await request.json()
    model : str = data.get("model", None)
    if model not in defines.MODELS:
        logging.error(f"Invalid model: {model} only {defines.MODELS} are allowed")
        return blacksheep.Response(400, content=f"Invalid model {model} only {defines.MODELS} are allowed")
    
    messages : list = data.get("messages", [])
    if not messages:
        logging.error(f"Invalid messages: {messages}")
        return blacksheep.Response(400, content="Empty messages")
    
    if data.get("stream", False):
        async def streaming():
            async for chunk in service.send_message(messages, model):
                yield f"data: {json.dumps(chunk, separators=(',', ':'))}\n\n".encode("utf-8")
            yield b"data: [DONE]\n\n"
        return blacksheep.Response(200, content=blacksheep.StreamedContent(b"text/plain", streaming))
    
    return blacksheep.json(await service.send_message_sync(messages, model))
