import csv

from langsmith import Client


def create_dataset(csv_file_path):
    dataset = []
    try:
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

        # Check if columns "input" and "output" exist
        if (
            "user_query" in csv_reader.fieldnames
            and "agent_response" in csv_reader.fieldnames
        ):
            for row in csv_reader:
                input_value = row["user_query"]
                output_value = row["agent_response"]
                dataset.append((input_value, output_value))
        else:
            print(
                "CSV file does not have the required 'user_query' and 'agent_response' columns."
            )
    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    client = Client()
    dataset_id = "ecommerce-agent-dataset"
    dataset = create_dataset("assets/ecommerce-agent-dataset.csv")

    # Prepare inputs and outputs for bulk creation
    inputs = []
    outputs = []
    for input_prompt, output_answer in dataset:
        inputs.append({"user_query": input_prompt})
        outputs.append({"agent_response": output_answer})

    client.create_examples(
        inputs=inputs,
        outputs=outputs,
        dataset_id=dataset_id,
    )

# https://langchain-ai.github.io/langgraph/tutorials/chatbot-simulation-evaluation/agent-simulation-evaluation/?h=eval
