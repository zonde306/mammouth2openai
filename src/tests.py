import os
import unittest
import app
import features
import defines
import service
import blacksheep
import blacksheep.testing

class TestApp(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await app.app.start()
        self.client = blacksheep.testing.TestClient(app.app)
    
    async def test_models(self):
        response : blacksheep.Response = await self.client.get("/v1/models")
        data : dict = await response.json()
        self.assertEqual(response.status, 200)
        for model in data.get("data", []):
            self.assertEqual(model["object"], "model")
            self.assertIn("id", model)
            self.assertIn(model.get("name", ""), defines.MODELS)
    
    """
    async def test_chat_completions(self):
        messages = [
            {
                "role": "system",
                "content": "you are helpful assistant"
            },
            {
                "role": "user",
                "content": "hi",
            },
        ]

        response : blacksheep.Response = await self.client.post("/v1/chat/completions", json={
            "model": "anthropic-claude-3-7-sonnet-latest",
            "messages": messages,
            "stream": False,
        })

        data : dict = await response.json()
        self.assertEqual(response.status, 200)
        self.assertEqual(data["choices"][0]["finish_reason"], "STOP")
        print(data["choices"][0]["delta"]["content"])
    """

class TestFeatures(unittest.IsolatedAsyncioTestCase):
    def test_features(self):
        messages = [{
            "role": "system",
            "content": "first message\n"
                       "<roleInfo>\n"
                       "user:asdf8249\n"
                       "assistant: asfdf\n"
                       "system:fwasd\n"
                       "developer: ddd\n"
                       "</roleInfo>\n"
                       "<systemPrompt>just system message</systemPrompt>"
        }]
        feat = features.process_features(messages)

        self.assertEqual(feat.role.user, "asdf8249")
        self.assertEqual(feat.role.assistant, "asfdf")
        self.assertEqual(feat.role.system, "fwasd")
        self.assertEqual(feat.role.developer, "ddd")
        self.assertIn("just system", feat.system_prompt)

class TestService(unittest.IsolatedAsyncioTestCase):
    async def test_format_messages(self):
        messages = [
            {
                "role": "system",
                "content": "<roleInfo>\n"
                           "user:asdf8249\n"
                           "assistant: asfdf\n"
                           "system:fwasd\n"
                           "developer: ddd\n"
                           "</roleInfo>\njust system"
            },
            {
                "role": "user",
                "content": "hi",
            },
        ]
        feat = features.process_features(messages)
        prompt = await features.format_messages(messages, feat.role)

        self.assertNotIn("user: hi", prompt)
        self.assertIn("asdf8249: hi", prompt)
    
    async def test_send_message(self):
        messages = [
            {
                "role": "system",
                "content": "you are helpful assistant"
            },
            {
                "role": "user",
                "content": "hi",
            },
        ]
        async for msg in service.send_message(messages, "anthropic-claude-3-7-sonnet-latest"):
            print(msg)
        self.assertEqual(msg["choices"][0]["finish_reason"], "STOP")
        
        messages = [
            {
                "role": "system",
                "content": "you are helpful assistant"
            },
            {
                "role": "user",
                "content": "hi",
            },
        ]
        msg = await service.send_message_sync(messages, "anthropic-claude-3-7-sonnet-latest")
        print(msg)
        self.assertEqual(msg["choices"][0]["finish_reason"], "STOP")

    """
    async def test_error(self):
        messages = [
            {
                "role": "system",
                "content": "you are helpful assistant"
            },
            {
                "role": "user",
                "content": "hi",
            },
        ]
        async for msg in service.send_message(messages, "anthropic-claude-3-7-sonnet-latest"):
            print(msg)
            self.assertEqual(msg["choices"][0]["finish_reason"], "ERROR")
            self.assertIn("ERROR", msg["choices"][0]["delta"]["content"])
        
        messages = [
            {
                "role": "system",
                "content": "you are helpful assistant"
            },
            {
                "role": "user",
                "content": "hi",
            },
        ]
        msg = await service.send_message_sync(messages, "anthropic-claude-3-7-sonnet-latest")
        print(msg)
        self.assertEqual(msg["choices"][0]["finish_reason"], "error")
        self.assertIn("ERROR", msg["choices"][0]["message"]["content"])
    """
