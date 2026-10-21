import uuid

from langgraph.store.memory import InMemoryStore

# LangGraph Store
in_memory_store = InMemoryStore()
user_id = "1"
namespace_for_memory = (user_id, "memories")
key = str(uuid.uuid4())
value = {"name": "Thanh"}
in_memory_store.put(namespace_for_memory, key, value)

memories = in_memory_store.search(namespace_for_memory)
print("search---")
print("memories type:", type(memories))
print("memories value:", memories)

# metadata
print("metadata---: ", memories[0].dict())

# key, value
print("key, value---")
print("key:", memories[0].key)
print("value:", memories[0].value)

# Get memory by namespace and key
memory = in_memory_store.get(namespace_for_memory, key)
print(f"memory of {key}:", memory.dict())

# Chatbot with long-term memory
