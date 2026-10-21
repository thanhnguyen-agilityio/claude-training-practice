Issue: Summary conversation sometime got error:
- temp fix: disable feature
```
raise self._make_status_error_from_response(err.response) from None
    | openai.BadRequestError: Error code: 400 - {'error': {'message': "Invalid parameter: messages with role 'tool' must be a response to a preceeding message with 'tool_calls'.", 'type': 'invalid_request_error', 'param': 'messages.[1].role', 'code': None}}
+-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/starlette/responses.py", line 264, in wrap
    |     await func()
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/starlette/responses.py", line 245, in stream_response
    |     async for chunk in self.body_iterator:
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/server/routers/chat.py", line 64, in stream_agent_response
    |     for msg, metadata in graph.stream(
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langgraph/pregel/__init__.py", line 1724, in stream
    |     for _ in runner.tick(
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langgraph/pregel/runner.py", line 302, in tick
    |     _panic_or_proceed(
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langgraph/pregel/runner.py", line 619, in _panic_or_proceed
    |     raise exc
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langgraph/pregel/executor.py", line 83, in done
    |     task.result()
    |   File "/Users/thanhnguyendiem/.pyenv/versions/3.11.1/lib/python3.11/concurrent/futures/_base.py", line 449, in result
    |     return self.__get_result()
    |            ^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/.pyenv/versions/3.11.1/lib/python3.11/concurrent/futures/_base.py", line 401, in __get_result
    |     raise self._exception
    |   File "/Users/thanhnguyendiem/.pyenv/versions/3.11.1/lib/python3.11/concurrent/futures/thread.py", line 58, in run
    |     result = self.fn(*self.args, **self.kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langgraph/pregel/retry.py", line 40, in run_with_retry
    |     return task.proc.invoke(task.input, config)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langgraph/utils/runnable.py", line 506, in invoke
    |     input = step.invoke(input, config, **kwargs)
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langgraph/utils/runnable.py", line 270, in invoke
    |     ret = context.run(self.func, *args, **kwargs)
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/server/agent/graph.py", line 53, in __call__
    |     result = self.runnable.invoke(state)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langchain_core/runnables/base.py", line 3016, in invoke
    |     input = context.run(step.invoke, input, config)
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langchain_core/runnables/base.py", line 5352, in invoke
    |     return self.bound.invoke(
    |            ^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 284, in invoke
    |     self.generate_prompt(
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 860, in generate_prompt
    |     return self.generate(prompt_messages, stop=stop, callbacks=callbacks, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 690, in generate
    |     self._generate_with_cache(
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 913, in _generate_with_cache
    |     for chunk in self._stream(messages, stop=stop, **kwargs):
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/langchain_openai/chat_models/base.py", line 722, in _stream
    |     response = self.client.create(**payload)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/openai/_utils/_utils.py", line 279, in wrapper
    |     return func(*args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/openai/resources/chat/completions.py", line 863, in create
    |     return self._post(
    |            ^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/openai/_base_client.py", line 1283, in post
    |     return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))
    |                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/openai/_base_client.py", line 960, in request
    |     return self._request(
    |            ^^^^^^^^^^^^^^
    |   File "/Users/thanhnguyendiem/Documents/thanhnguyen-agilityio-github/ecommerce-agent/.venv/lib/python3.11/site-packages/openai/_base_client.py", line 1064, in _request
    |     raise self._make_status_error_from_response(err.response) from None
    | openai.BadRequestError: Error code: 400 - {'error': {'message': "Invalid parameter: messages with role 'tool' must be a response to a preceeding message with 'tool_calls'.", 'type': 'invalid_request_error', 'param': 'messages.[1].role', 'code': None}}
    | During task with name 'assistant' and id 'ba44d01b-a387-dfc3-0734-b23c86789e06'
    +------------------------------------
```

- State messages:
```
(Pdb) state["messages"]
[ToolMessage(content='Category, Product, SupportTicket', name='sql_db_list_tables', id='b0d34fc1-aa17-453b-ba8a-672619b6fa9c', tool_call_id='call_O1NRClmsOjuujZaCD5lUNbo5'), ToolMessage(content='\nCREATE TABLE "Product" (\n\tid INTEGER NOT NULL, \n\tname VARCHAR NOT NULL, \n\tdescription VARCHAR, \n\tprice FLOAT NOT NULL, \n\tquantity INTEGER, \n\tcategory_id INTEGER NOT NULL, \n\tsizes VARCHAR, \n\tthumbnail VARCHAR, \n\turl VARCHAR, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(category_id) REFERENCES "Category" (id)\n)', name='sql_db_schema', id='0dd9b4d2-474b-46ae-a07e-6872b5f686b1', tool_call_id='call_BHb0bHPybr8K2Ecnhr8pE6NW'), AIMessage(content='', additional_kwargs={'tool_calls': [{'index': 0, 'id': 'call_qhyEBn0Fq4TkV9AN0Uw27E9o', 'function': {'arguments': '{"query":"SELECT * FROM Product WHERE name LIKE \'%Straight Cut Button-down Collar Shirt%\';"}', 'name': 'check_and_execute_query_tool'}, 'type': 'function'}]}, response_metadata={'finish_reason': 'tool_calls', 'model_name': 'ft:gpt-4o-mini-2024-07-18:personal::B16sK6xs', 'system_fingerprint': 'fp_6f625379d6'}, id='run-44bd1905-a38f-4e57-9b64-92556bec673b', tool_calls=[{'name': 'check_and_execute_query_tool', 'args': {'query': "SELECT * FROM Product WHERE name LIKE '%Straight Cut Button-down Collar Shirt%';"}, 'id': 'call_qhyEBn0Fq4TkV9AN0Uw27E9o', 'type': 'tool_call'}]), ToolMessage(content="[(21, 'Straight Cut Button-down Collar Shirt', 'The shirt provides comfort while remaining impressive, suitable for various occasions from office to street wear. - Button-down collar design brings elegance and neatness, suitable for both office and casual styles. - Modern zipper detail creates a novel accent and adds convenience when wearing....', 17.0, 51, 2, 'S,M,L,XL,XXL', 'https://pubcdn.ivymoda.com/files/product/thumab/1400/2024/12/06/06ae1f0d2157a7b14479f3e01b18c3bc.webp', 'https://ivymoda.com/sanpham/ao-so-mi-co-duc-dang-suong-ms-16m8962-41263')]", name='check_and_execute_query_tool', id='f3488c6c-7499-4714-a03f-7ef2e4811de9', tool_call_id='call_qhyEBn0Fq4TkV9AN0Uw27E9o'), AIMessage(content="Here's the elegant **Straight Cut Button-down Collar Shirt** you're interested in:\n- 💲 Price: $17.00\n- ✨ Description: The shirt provides comfort while remaining impressive, suitable for various occasions from office to street wear.  \n  - ✅ Button-down collar design brings elegance and neatness, suitable for both office and casual styles.  \n  - ✨ Modern zipper detail creates a novel accent and adds convenience when wearing.  \n- ✅ Availability: 51 pieces in stock  \n- 🖼️ ![Image](https://pubcdn.ivymoda.com/files/product/thumab/1400/2024/12/06/06ae1f0d2157a7b14479f3e01b18c3bc.webp)  \n- 🔗 [👉 Shop Now](https://ivymoda.com/sanpham/ao-so-mi-co-duc-dang-suong-ms-16m8962-41263)  \nElevate your shirt collection with this versatile piece! 👔✨", additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'ft:gpt-4o-mini-2024-07-18:personal::B16sK6xs', 'system_fingerprint': 'fp_6f625379d6'}, id='run-aeecf799-a718-43f1-91c7-779486f56890'), HumanMessage(content='Compare "Gilded Prowl Skirt" with "Khaki Mini Skirt"', additional_kwargs={}, response_metadata={}, id='2a7ff992-0188-4671-8328-da84d9d06b85'), AIMessage(content='', additional_kwargs={'tool_calls': [{'index': 0, 'id': 'call_kAapUVZKMiuhmCP9IUJ9NkeH', 'function': {'arguments': '{}', 'name': 'sql_db_list_tables'}, 'type': 'function'}, {'index': 1, 'id': 'call_E1GpuGMsg8clljNDcBwTgPQz', 'function': {'arguments': '{"table_names": "Product"}', 'name': 'sql_db_schema'}, 'type': 'function'}]}, response_metadata={'finish_reason': 'tool_calls', 'model_name': 'ft:gpt-4o-mini-2024-07-18:personal::B16sK6xs', 'system_fingerprint': 'fp_6f625379d6'}, id='run-49b78e37-17e9-4b5f-ade7-c37f86a9e475', tool_calls=[{'name': 'sql_db_list_tables', 'args': {}, 'id': 'call_kAapUVZKMiuhmCP9IUJ9NkeH', 'type': 'tool_call'}, {'name': 'sql_db_schema', 'args': {'table_names': 'Product'}, 'id': 'call_E1GpuGMsg8clljNDcBwTgPQz', 'type': 'tool_call'}]), ToolMessage(content='Category, Product, SupportTicket', name='sql_db_list_tables', id='c0e6a77a-6720-430f-998c-e4a3f71c73ee', tool_call_id='call_kAapUVZKMiuhmCP9IUJ9NkeH'), ToolMessage(content='\nCREATE TABLE "Product" (\n\tid INTEGER NOT NULL, \n\tname VARCHAR NOT NULL, \n\tdescription VARCHAR, \n\tprice FLOAT NOT NULL, \n\tquantity INTEGER, \n\tcategory_id INTEGER NOT NULL, \n\tsizes VARCHAR, \n\tthumbnail VARCHAR, \n\turl VARCHAR, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(category_id) REFERENCES "Category" (id)\n)', name='sql_db_schema', id='74bbd476-aece-4b14-92c7-2a893fe859d4', tool_call_id='call_E1GpuGMsg8clljNDcBwTgPQz'), AIMessage(content='', additional_kwargs={'tool_calls': [{'index': 0, 'id': 'call_qK4FSmTRJBQpZX3aJFwNl5PD', 'function': {'arguments': '{"query": "SELECT * FROM Product WHERE name LIKE \'%Gilded Prowl Skirt%\';"}', 'name': 'check_and_execute_query_tool'}, 'type': 'function'}, {'index': 1, 'id': 'call_yc6cJCeHk9CG7XQp3RkOUKiH', 'function': {'arguments': '{"query": "SELECT * FROM Product WHERE name LIKE \'%Khaki Mini Skirt%\';"}', 'name': 'check_and_execute_query_tool'}, 'type': 'function'}]}, response_metadata={'finish_reason': 'tool_calls', 'model_name': 'ft:gpt-4o-mini-2024-07-18:personal::B16sK6xs', 'system_fingerprint': 'fp_6f625379d6'}, id='run-be6a3815-eed5-47e7-b46d-4e21fb72acb7', tool_calls=[{'name': 'check_and_execute_query_tool', 'args': {'query': "SELECT * FROM Product WHERE name LIKE '%Gilded Prowl Skirt%';"}, 'id': 'call_qK4FSmTRJBQpZX3aJFwNl5PD', 'type': 'tool_call'}, {'name': 'check_and_execute_query_tool', 'args': {'query': "SELECT * FROM Product WHERE name LIKE '%Khaki Mini Skirt%';"}, 'id': 'call_yc6cJCeHk9CG7XQp3RkOUKiH', 'type': 'tool_call'}]), ToolMessage(content="[(27, 'Gilded Prowl Skirt', 'Gilded Prowl Skirt made from silk with a mermaid tail design. Part of the You product line.', 21.0, 73, 7, 'S,M,L,XL,XXL', 'https://pubcdn.ivymoda.com/files/product/thumab/1400/2024/12/05/db720242603a5471c3be6d8dda697e0e.webp', 'https://ivymoda.com/sanpham/chan-vay-gilded-prowl-ms-31b0050-41288')]", name='check_and_execute_query_tool', id='81179b2c-a177-4063-a7d2-ab6d31b418c8', tool_call_id='call_qK4FSmTRJBQpZX3aJFwNl5PD'), ToolMessage(content="[(25, 'Khaki Mini Skirt', 'Khaki Mini Skirt made from Khaki material, A shape, above the knee, plain design.', 21.0, 79, 7, 'S,M,L,XL,XXL', 'https://pubcdn.ivymoda.com/files/product/thumab/1400/2024/12/06/06ae1f0d2157a7b14479f3e01b18c3bc.webp', 'https://ivymoda.com/sanpham/chan-vay-mini-khaki-ms-31m8981-41152')]", name='check_and_execute_query_tool', id='52666f8a-75c9-4ca4-b9bf-fee30fe3ebec', tool_call_id='call_yc6cJCeHk9CG7XQp3RkOUKiH')]
```
See: there are 2 tools calls message:
```
ToolMessage(content="[(27, 'Gilded Prowl Skirt', 'Gilded Prowl Skirt made from silk with a mermaid tail design. Part of the You product line.', 21.0, 73, 7, 'S,M,L,XL,XXL', 'https://pubcdn.ivymoda.com/files/product/thumab/1400/2024/12/05/db720242603a5471c3be6d8dda697e0e.webp', 'https://ivymoda.com/sanpham/chan-vay-gilded-prowl-ms-31b0050-41288')]", name='check_and_execute_query_tool', id='81179b2c-a177-4063-a7d2-ab6d31b418c8', tool_call_id='call_qK4FSmTRJBQpZX3aJFwNl5PD'), ToolMessage(content="[(25, 'Khaki Mini Skirt', 'Khaki Mini Skirt made from Khaki material, A shape, above the knee, plain design.', 21.0, 79, 7, 'S,M,L,XL,XXL', 'https://pubcdn.ivymoda.com/files/product/thumab/1400/2024/12/06/06ae1f0d2157a7b14479f3e01b18c3bc.webp', 'https://ivymoda.com/sanpham/chan-vay-mini-khaki-ms-31m8981-41152')]", name='check_and_execute_query_tool', id='52666f8a-75c9-4ca4-b9bf-fee30fe3ebec', tool_call_id='call_yc6cJCeHk9CG7XQp3RkOUKiH')
```
One not have message before is AIMessage with `tools_call` cause error.

> https://github.com/langchain-ai/langgraph/discussions/1398