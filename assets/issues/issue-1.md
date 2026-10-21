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
[ToolMessage(content='Category, Product, SupportTicket', name='sql_db_list_tables', id='b0d34fc1-aa17-453b-ba8a-672619b6fa9c', tool_call_id='call_O1NRClmsOjuujZaCD5lUNbo5'), ToolMessage(content='\nCREATE TABLE "Product" (\n\tid INTEGER NOT NULL, \n\tname VARCHAR NOT NULL, \n\tdescription VARCHAR, \n\tprice FLOAT NOT NULL, \n\tquantity INTEGER, \n\tcategory_id INTEGER NOT NULL, \n\tsizes VARCHAR, \n\tthumbnail VARCHAR, \n\turl VARCHAR, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(category_id) REFERENCES "Category" (id)\n)', name='sql_db_schema', id='0dd9b4d2-474b-46ae-a07e-6872b5f686b1', tool_call_id='call_BHb0bHPybr8K2Ecnhr8pE6NW'), AIMessage(content='', additional...
```