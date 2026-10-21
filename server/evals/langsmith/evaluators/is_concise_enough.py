def is_concise_enough(reference_outputs: dict, outputs: dict) -> dict:
    score = len(outputs["output"]) < 1.5 * len(reference_outputs["agent_response"])
    return {"key": "is_concise", "score": int(score)}
