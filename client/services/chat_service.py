import json

import httpx
import requests
from langserve import RemoteRunnable
from utils.constants import API_BASE_URL


class ChatService:
    def __init__(
        self, base_url: str = API_BASE_URL, user_id: str = None, thread_id: str = None
    ):
        self.base_url = base_url
        self.user_id = user_id if user_id else "user_1"
        self.thread_id = thread_id if thread_id else "thread_1"
        self.agent = RemoteRunnable(f"{base_url}/chat")

    def chat_invoke(self, message: str) -> dict:
        input = {
            "message": message,
            "thread_id": self.thread_id,
            "user_id": self.user_id,
        }

        try:
            response = requests.post(
                self.base_url + "/chat/invoke", json={"input": input}
            )
        except Exception as e:
            raise Exception(
                "Cannot invoke chat API. Please check the server logs."
            ) from e
        else:
            if response.status_code != 200:
                raise Exception(
                    "Chat API response not success. Please check the server logs."
                )

            return response.json()

    async def chat_stream(self, message: str):
        """
        Stream chat messages in client side with httpx
        """
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                self.base_url + "/chat/stream",
                json={
                    "message": message,
                    "thread_id": self.thread_id,
                    "user_id": self.user_id,
                },
                timeout=30,
            ) as response:
                async for chunk in response.aiter_bytes():
                    try:
                        yield json.loads(chunk)
                    except json.JSONDecodeError:
                        yield chunk.strip()

    def chat_history(self) -> dict:
        """Get chat history of a thread_id"""
        try:
            response = requests.get(
                self.base_url + f"/history?thread_id={self.thread_id}"
            )
        except Exception as e:
            raise Exception(
                "Cannot get chat history. Please check the server logs."
            ) from e
        else:
            if response.status_code != 200:
                raise Exception(
                    "Cannot get chat history. Please check the server logs."
                )

            return response.json()

    def approve_tool_call(self, tool_call_id: str) -> dict:
        try:
            response = requests.post(
                self.base_url + "/chat/approve/", json={
                    "message": "Approved",
                    "user_id": self.user_id,
                    "thread_id": self.thread_id,
                    "tool_call_id": tool_call_id,
                    "user_input": "The tool call is approved.",
                }
            )
        except Exception as e:
            raise Exception(
                "Cannot call chat API. Please check the server logs."
            ) from e
        else:
            if response.status_code != 200:
                raise Exception(
                    "Chat API response not success. Please check the server logs."
                )

            return response.json()

    def reject_tool_call(self, tool_call_id: str):
        try:
            response = requests.post(
                self.base_url + "/chat/reject/", json={
                    "message": "Rejected",
                    "user_id": self.user_id,
                    "thread_id": self.thread_id,
                    "tool_call_id": tool_call_id,
                    "user_input": "The tool call is rejected.",
                }
            )
        except Exception as e:
            raise Exception(
                "Cannot call chat API. Please check the server logs."
            ) from e
        else:
            if response.status_code != 200:
                raise Exception(
                    "Chat API response not success. Please check the server logs."
                )

            return response.json()
