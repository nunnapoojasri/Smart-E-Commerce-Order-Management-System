# Smart-E-Commerce-Order-Management-System

A CrewAI-powered order-support demo. Four agents verify the order, check inventory,
track delivery, and prepare a customer resolution. Streamlit provides the customer
interface; sample orders and inventory are stored in CSV files.

## Run locally

Requires Python 3.10–3.12 (recommended for CrewAI dependency compatibility) and an
OpenAI API key.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Use a Python 3.10–3.12 interpreter to create the virtual environment.

No API key is needed for local mode. It handles requests using the included
sample order, inventory, and mock tracking records. To enable CrewAI/LLM responses,
set `OPENAI_API_KEY` before starting the app. Optionally set `OPENAI_MODEL`;
the default is `openai/gpt-4o-mini`. On Windows PowerShell, set the key with
`$env:OPENAI_API_KEY="your-api-key"`.

## Try the sample orders

| Order ID | Scenario |
| --- | --- |
| `ORD1025` | Delayed wireless headphones; the originally ordered SKU is out of stock, with alternatives listed |
| `ORD1026` | Delivered mechanical keyboard |
| `ORD1027` | Smart speaker being processed; the SKU is out of stock, with an alternative listed |
| `ORD1028` | Another delayed wireless-headphone shipment |

Order and inventory records are in `order_management/data/`. The tracking tool uses
mock carrier data from `orders.csv`; no live carrier or ticketing service is connected.

## Human escalation

Before recommending a resolution, the Resolution Agent checks the escalation policy.
Requests for a human, safety concerns, suspected fraud, payment disputes, refund or
cancellation requests, and shipments marked delivered but reported missing are routed
to a human-support handoff rather than answered automatically. The interface displays
the escalation reason and an internal summary when available. This demo flags the
handoff in the UI; connecting it to a ticketing or support queue requires an external
service integration.

## Tests

```bash
python -m unittest discover -s tests -v
```