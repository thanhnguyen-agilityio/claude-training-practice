from langsmith.schemas import Example, Run


def latency_evaluator(root_run: Run, example: Example):
    """
    Evaluate the latency of the agent response.
    """
    latency = root_run.end_time - root_run.start_time
    return {"score": latency.total_seconds(), "key": "latency"}
