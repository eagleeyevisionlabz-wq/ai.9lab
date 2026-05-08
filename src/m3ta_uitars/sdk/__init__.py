"""Agent SDK for Qu3bii / Hermes / Metatron / M3ta-0S.

Two clients with the same shape:
  - InProcessClient: calls the Engine directly. Use this for embedded agents.
  - HTTPClient:      calls the FastAPI surface over HTTP. Use this for agents
                     running outside the host process (e.g. Qu3bii on iOS,
                     Hermes in n8n).

Both expose the same convenience methods:
  - run_computer_task(...)
  - observe_screen(...)
  - get_task_status(...)
  - cancel_task(...)
  - get_audit_log(...)
"""

from m3ta_uitars.sdk.client import HTTPClient, InProcessClient, M3taUITARSClient

__all__ = ["HTTPClient", "InProcessClient", "M3taUITARSClient"]
