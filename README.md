# 🚀 Intersight MCP Server  
### A FastMCP-based AI Agent Server for Cisco Intersight Automation

This project provides a fully modular **Model Context Protocol (MCP) Server** built with **FastMCP**, designed to expose Cisco Intersight APIs and workflows as callable tools for LLMs, agents, and and automation systems.

It supports both:

- **Cisco Intersight Python SDK** (`intersight.api.*`)
- **Cisco Intersight REST API** (signed requests using `IntersightAuth`)

This allows AI/LLM systems to query, analyze, and automate Intersight environments securely.

---

## 🧩 Features

### ✔ Python SDK + REST Support  
- Full Intersight authentication via signed requests  
- Supports API Key v2 (RSA) and v3 (ECDSA)  
- Auto-detects signing scheme  
- Automatic fallback secret key path  

### ✔ FastMCP Tools  
Current tools:

| Tool Name | Description |
|-----------|-------------|
| `greet` | Sample test tool to verify FastMCP |
| `list_physical_summaries` | Retrieves compute/PhysicalSummaries |
| `get_organization_list` | Retrieves organization/Organizations |

Recommended future tools:

- Server Profiles  
- Server Profile Templates  
- Workflow listing  
- Workflow trigger  
- Compute Blades  
- Switch/Fabric profiles  

---

## 📁 Project Structure

```
IntersightMCPServer/
│
├── README.md                      # This file
├── .env                           # Environment variables (ignored by git)
├── intersight_server.py           # Main MCP Server with tools
├── test_mcp_tools.py              # Test client for tools
│
├── utils/
│   ├── intersight_auth.py         # Python SDK authentication utility
│   └── intersight_rest.py         # REST session authentication utility
│
├── models/
│   └── organization.py            # Pydantic schema for Organizations
│
└── NSDev01-SecretKey.txt          # Secret Key (ignored by git)
```

---

## 🔐 Environment Setup

Create a `.env` file in the project directory:

```env
INTERSIGHT_API_KEY=<your-api-key-id>
INTERSIGHT_SECRET_FILE_PATH=C:/IntersightMCPServer/NSDev01-SecretKey.txt
INTERSIGHT_ENDPOINT=https://intersight.com/api/v1
```

**Important:**  
The `.gitignore` file ensures `.env` and secret key files are never committed.

---

## 📦 Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶ Running the MCP Server

```bash
fastmcp run intersight_server.py:mcp --transport http --port 8000
```

You should see:

```
Uvicorn running on http://127.0.0.1:8000
```

---

## 🧪 Testing Tools

Use the provided test script:

```bash
python test_mcp_tools.py
```

Example usage:

```python
async with Client("http://127.0.0.1:8000/mcp") as client:
    result = await client.call_tool("list_physical_summaries", {"top": 5})
    print(result)
```

---

## 🛠 Example Tool (REST)

```python
@mcp.tool
def get_organization_list():
    session, endpoint = get_intersight_rest_session()
    url = f"{endpoint}/api/v1/organization/Organizations"
    r = session.get(url)
    return r.json().get("Results", [])
```

---

## 🛠 Example Tool (Python SDK)

```python
@mcp.tool
def list_physical_summaries(top: int = 10):
    client = intersight_client_connection()
    compute = compute_api.ComputeApi(client)
    response = compute.get_compute_physical_summary_list(top=top)
    return [item.to_dict() for item in response.results]
```

---

## 🔒 Security Notes

- Do **not** commit `.env` or secret key files  
- Only use dedicated Intersight API keys  
- Rotate keys periodically  
- `.gitignore` already blocks sensitive files  

---

## 📌 Requirements

- Python 3.10+  
- FastMCP 2.13+  
- intersight 1.0.11.x  
- intersight_auth  
- python-dotenv  
- requests  

---

## 🤝 Contributing

Pull requests are welcome.  
For major changes, please open an issue first to discuss what you’d like to change.

---

## 📄 License

This project is intended for internal automation use.
