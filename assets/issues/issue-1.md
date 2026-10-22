# Issue [#1](https://github.com/thanhnguyen-agilityio/claude-training-practice/issues/1)
## Title: Chatbot shows error in long conversations
## Description:

**Issue**
- When a conversation gets long, the chatbot sometimes fails and the user sees an error instead of an answer.
- It does not happen every time, so it is hard to predict.
- Temporary workaround: the conversation summary feature is turned off.

**Expected**
- The chatbot keeps answering normally, no matter how long the conversation gets.
- The summary feature can be turned back on without causing errors.

## Error trace
```
|   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/openai/_base_client.py", line 1064, in _request
|     raise self._make_status_error_from_response(err.response) from None
| openai.BadRequestError: Error code: 400 - {'error': {'message': "Invalid parameter: messages with role 'tool' must be a response to a preceeding message with 'tool_calls'.", 'type': 'invalid_request_error', 'param': 'messages.[1].role', 'code': None}}
| During task with name 'assistant' and id 'ba44d01b-a387-dfc3-0734-b23c86789e06'
```

## State messages

```
(Pdb) state["messages"]
[
    ToolMessage(content='.', name='sql_db_list_tables', id='b0d34fc1-aa17-453b-ba8a-672619b6fa9c', tool_call_id='call_O1NRClmsOjuujZaCD5lUNbo5'),

    ToolMessage(content='.', name='sql_db_schema', id='0dd9b4d2-474b-46ae-a07e-6872b5f686b1', tool_call_id='call_BHb0bHPybr8K2Ecnhr8pE6NW'),

    AIMessage(content='', tool_calls=[{'name': 'check_and_execute_query_tool', 'args': {'query': "SELECT * FROM Product WHERE name LIKE '%Straight Cut Button-down Collar Shirt%';"}, 'id': 'call_qhyEBn0Fq4TkV9AN0Uw27E9o', 'type': 'tool_call'}]),

    ToolMessage(content="[(21, 'Straight Cut Button-down Collar Shirt', '...', 17.0, 51, 2, 'S,M,L,XL,XXL', '.', '.')]", name='check_and_execute_query_tool', id='f3488c6c-7499-4714-a03f-7ef2e4811de9', tool_call_id='call_qhyEBn0Fq4TkV9AN0Uw27E9o'),

    AIMessage(content="...", additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'ft:gpt-4o-mini-2024-07-18:personal::B16sK6xs', 'system_fingerprint': 'fp_6f625379d6'}, id='run-aeecf799-a718-43f1-91c7-779486f56890'),
]
```
