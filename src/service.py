import json
import uuid
import time
import logging
import random
from typing import AsyncGenerator
import defines
import features
import rnet

CLIENTS : dict[str, rnet.Client] = {}
CLIENTS_POLL : int = -1

logger = logging.getLogger(__name__)

def setup():
    for cookie in defines.COOKIES:
        client = rnet.Client(
            cookie_store=True,
            impersonate=rnet.Impersonate.Chrome133,
            proxies= [rnet.Proxy.all(defines.PROXIES)] if defines.PROXIES else [],
        )
        client.set_cookie("https://mammouth.ai/", rnet.Cookie("auth_session", cookie))
        client.set_cookie("https://mammouth.ai/", rnet.Cookie("i18n_redirected", "en"))
        CLIENTS[cookie] = client

async def get_client() -> rnet.Client:
    if not CLIENTS:
        logger.error("No API keys available")
        return rnet.Client(impersonate=rnet.Impersonate.Chrome100)

    global CLIENTS_POLL
    CLIENTS_POLL += 1
    clients = list(CLIENTS.values())
    return clients[CLIENTS_POLL % len(clients)]

async def send_message(messages: list, model: str) -> AsyncGenerator[dict, None]:
    feat = features.process_features(messages)
    formatted = await features.format_messages(messages, feat.role)
    client = await get_client()

    """
    info = await login(client)
    print(info)
    chatid, info = await create_chat(client, model, "HI")
    print(info)
    """

    multipart = rnet.Multipart(*[
        rnet.Part("model", model),
        rnet.Part("preprompt", feat.system_prompt),
        rnet.Part("messages", json.dumps({
            "content": formatted,
            "imagesData": [],
            "documentsData": [],
        }, separators=(',', ':'))),
    ])

    headers = {
        "Referer": f"https://mammouth.ai/app/a/default/c/{random.randint(1000000, 9999999)}",
        "origin": "https://mammouth.ai",
    }

    error_message = ""
    request_id = f"chatcmpl-{uuid.uuid4()}"

    try:
        async with await client.post("https://mammouth.ai/api/models/llms", headers=headers, multipart=multipart) as response:
            assert isinstance(response, rnet.Response)
            assert response.status_code.is_success(), f"{response.status_code} {await response.text()} {client.get_cookies('https://mammouth.ai/api/models/llms')}"
            async with response.stream() as streamer:
                assert isinstance(streamer, rnet.Streamer)
                async for chunk in streamer:
                    assert isinstance(chunk, bytes)
                    yield {
                        "id": request_id,
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {
                                    "content": chunk.decode("utf-8"),
                                },
                            }
                        ],
                    }
    except (AssertionError, ConnectionError) as e:
        error_message = str(e)
        logger.error(f"Error: {e}", exc_info=True)
    
    if error_message:
        print(error_message)
        yield {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "content": f"ERROR: {error_message}",
                    },
                    "finish_reason": "ERROR",
                }
            ],
        }
    else:
        yield {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "content": "",
                    },
                    "finish_reason": "STOP",
                }
            ],
        }


async def send_message_sync(messages: list, model: str):
    content = ""
    error_message = ""
    async for message in send_message(messages, model):
        content += message["choices"][0]["delta"]["content"]
        if message["choices"][0].get("finish_reason", None) == "ERROR":
            error_message = message["choices"][0]["delta"]["content"]

    if error_message:
        return {
            "id": message["id"],
            "object": "chat.completion",
            "created": message["created"],
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": error_message,
                    },
                    "finish_reason": "ERROR",
                }
            ],
        }

    return {
        "id": message["id"],
        "object": "chat.completion",
        "created": message["created"],
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": "STOP",
            }
        ],
        "usage": None,
    }


async def login(client: rnet.Client):
    response : rnet.Response = await client.get("https://mammouth.ai/api/login/user")
    assert isinstance(response, rnet.Response)
    assert response.status_code.is_success(), f"{response.status_code} {await response.text()} {client.get_cookies('https://mammouth.ai/api/login/user')}"
    return await response.json()

async def create_chat(client: rnet.Client, model: str, message: str):
    response : rnet.Response = await client.post(
        "https://mammouth.ai/api/chat/create",
        headers={
            "referer": "https://mammouth.ai/app/a/default/",
            "origin": "https://mammouth.ai",
        },
        json={
            "message": message,
            "model": model,
            "defaultModels": {
                "text": "fireworks-llama-4.0-maverick",
                "image": "openai-gpt-image-1",
                "webSearch": "openperplex-v1"
            },
            "assistantId": None,
            "attachments": [],
            "metadata": {
                "task": {
                    "id": "",
                    "type": "imagine",
                    "value": ""
                }
        }
    })

    assert response.status_code.is_success(), f"{response.status_code} {await response.text()} {client.get_cookies('https://mammouth.ai/api/chat/create')}"
    data = await response.json()
    return data["chat"]["id"], data

setup()
