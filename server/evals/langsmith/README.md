# LangSmith Evaluation

- Prepare dataset: ([sheet](https://docs.google.com/spreadsheets/d/1NxFwEmAGC4RcTo1vUV-WcOMsKAOOrK6Nb37l5USzhog/edit?gid=0#gid=0))
- Create dataset:
  - Way 1: Drag the data file to LangSmith "New Dataset"
  - Way 2: Run script
    ```
    cd server
    uv run langsmith/dataset.py
    ```


- Run evaluation:
```
cd server
uv run evals/langsmith/experiment.py
```
