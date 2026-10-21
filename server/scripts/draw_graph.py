import os
import sys

# ----------------------------------------------------------------
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)
# ----------------------------------------------------------------

from server.agent.graph import graph  # noqa: E402

print(graph.get_graph().draw_mermaid())
# Then copy the content and paste to live tool https://mermaid.live/
