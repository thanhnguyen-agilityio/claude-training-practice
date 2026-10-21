from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from langsmith.schemas import Example, Run

gpt_4o_mini = ChatOpenAI(model="gpt-4o-mini")
gpt_3_5_turbo = ChatOpenAI(model="gpt-3.5-turbo")

# Set model for evaluation
model_evals = gpt_4o_mini


class Similarity_Score(BaseModel):
    similarity_score: int = Field(
        description="Semantic similarity score between 1 and 10, where 1 means unrelated and 10 means identical."
    )


def compare_semantic_similarity(root_run: Run, example: Example):
    try:
        input_question = example.inputs["user_query"]
        reference_response = example.outputs["agent_response"]
        run_response = root_run.outputs["output"]
    except TypeError:
        raise ValueError("Invalid input or output format")

    messages = [
        SystemMessage(
            content="You are a semantic similarity evaluator. Compare the meanings of two responses to a question, "
            "Reference Response and New Response, where the reference is the correct answer, and we are trying to judge if the new response is similar. "
            "Provide a score between 1 and 10, where 1 means completely unrelated, and 10 means identical in meaning."
        ),
        HumanMessage(
            content=f"Question: {input_question}\n Reference Response: {reference_response}\n Run Response: {run_response}"
        ),
    ]
    try:
        ai_message = model_evals.with_structured_output(Similarity_Score).invoke(messages)
    except Exception as e:
        # from remote_pdb import RemotePdb
        # RemotePdb('127.0.0.1', 4444).set_trace()
        raise ValueError(f"Error invoking model: {e}")

    score = ai_message.similarity_score
    return {"score": score, "key": "similarity"}


# --- Test evaluator ---
# if __name__ == "__main__":
#     sample_run = {
#         "name": "Sample Run",
#         "inputs": {
#             "user_query": "Do you offer free shipping?"
#         },
#         "outputs": {
#             "agent_response": "No, we do not offer free shipping."
#         },
#         "is_root": True,
#         "status": "success",
#         "extra": {
#             "metadata": {
#                 "key": "value"
#             }
#         }
#     }

#     sample_example = {
#         "inputs": {
#             "user_query": "Do you offer free shipping?"
#         },
#         "outputs": {
#             "agent_response": "Yes, we offer free shipping on orders over 1 million VND."
#         },
#         "metadata": {
#             "dataset_split": [
#                 "AI generated",
#                 "base"
#             ]
#         }
#     }

#     similarity_score = compare_semantic_similarity(sample_run, sample_example)
#     print(f"Semantic similarity score: {similarity_score}")
