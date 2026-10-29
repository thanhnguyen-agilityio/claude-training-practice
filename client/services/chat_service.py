import json
import logging

import httpx
import requests
from langserve import RemoteRunnable
from utils.constants import API_BASE_URL, ERROR_CONNECTION, ERROR_REQUEST

logger = logging.getLogger(__name__)


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
            logger.exception("Request failed: /chat/invoke")
            raise Exception(ERROR_CONNECTION) from e
        else:
            if response.status_code != 200:
                logger.error(
                    "HTTP %s on /chat/invoke: %s",
                    response.status_code,
                    response.text[:200],
                )
                raise Exception(
                    ERROR_REQUEST
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
                # NDJSON: one JSON value per line, however the bytes are chunked
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning("Skipping malformed stream line: %r", line)

    def chat_history(self) -> dict:
        """Get chat history of a thread_id"""
        try:
            response = requests.get(
                self.base_url + "/history",
                params={"thread_id": self.thread_id},
                timeout=30,
            )
        except Exception as e:
            logger.exception("Request failed: /history")
            raise Exception(ERROR_CONNECTION) from e
        else:
            if response.status_code != 200:
                logger.error(
                    "HTTP %s on /history: %s",
                    response.status_code,
                    response.text[:200],
                )
                raise Exception(
                    ERROR_REQUEST
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
            logger.exception("Request failed: /chat/approve")
            raise Exception(ERROR_CONNECTION) from e
        else:
            if response.status_code != 200:
                logger.error(
                    "HTTP %s on /chat/approve: %s",
                    response.status_code,
                    response.text[:200],
                )
                raise Exception(
                    ERROR_REQUEST
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
            logger.exception("Request failed: /chat/reject")
            raise Exception(ERROR_CONNECTION) from e
        else:
            if response.status_code != 200:
                logger.error(
                    "HTTP %s on /chat/reject: %s",
                    response.status_code,
                    response.text[:200],
                )
                raise Exception(
                    ERROR_REQUEST
                )

            return response.json()
