from langsmith import Client
from langsmith import utils as ls_utils
from uuid import UUID
from typing import Optional, Union
from pydantic import BaseModel
import asyncio

class SendFeedbackBody(BaseModel):
    run_id: UUID
    key: str = "user_score"

    score: Union[float, int, bool, None] = None
    feedback_id: Optional[UUID] = None
    comment: Optional[str] = None

class UpdateFeedbackBody(BaseModel):
    feedback_id: UUID
    score: Union[float, int, bool, None] = None
    comment: Optional[str] = None

class GetTraceBody(BaseModel):
    run_id: UUID

class LangsmithHandler():
    def __init__(self):
        self.client = Client()

    async def send_feedback(self, body: SendFeedbackBody):
        self.client.create_feedback(
            body.run_id,
            body.key,
            score=body.score,
            comment=body.comment,
            feedback_id=body.feedback_id,
        )
        return {"result": "posted feedback successfully", "code": 200}

    async def update_feedback(self, body: UpdateFeedbackBody):
        feedback_id = body.feedback_id
        if feedback_id is None:
            return {
                "result": "No feedback ID provided",
                "code": 400,
            }
        self.client.update_feedback(
            feedback_id,
            score=body.score,
            comment=body.comment,
        )
        return {"result": "patched feedback successfully", "code": 200}

    async def get_trace(self, body: GetTraceBody):
        run_id = body.run_id
        if run_id is None:
            return {
                "result": "No LangSmith run ID provided",
                "code": 400,
            }
        return await self._aget_trace_url(str(run_id))

    # TODO: Update when async API is available
    async def _arun(self, func, *args, **kwargs):
        return await asyncio.get_running_loop().run_in_executor(None, func, *args, **kwargs)

    async def _aget_trace_url(self, run_id: str) -> str:
        for i in range(5):
            try:
                await self._arun(self.client.read_run, run_id)
                break
            except ls_utils.LangSmithError:
                await asyncio.sleep(1**i)

        if await self._arun(self.client.run_is_shared, run_id):
            return await self._arun(self.client.read_run_shared_link, run_id)
        return await self._arun(self.client.share_run, run_id)
