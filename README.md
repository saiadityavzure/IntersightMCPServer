# 🚀 Intersight MCP Server
### FastMCP-based AI Agent Server for Cisco Intersight Automation

The **Intersight MCP Server** exposes Cisco Intersight automation workflows as **Model Context Protocol (MCP) tools**, allowing AI agents (ChatGPT, LangGraph, custom LLMs) to:

- Query hardware inventory  
- Generate Excel reports  
- Retrieve alarms  
- Trigger ICO workflows  
- Power ON/OFF VMs  
- Modify VM networks  
- Retrieve utilization metrics  
- And more  

All automation runs **inside your private network** with secure Intersight authentication.

---

# 🧰 Features

### ✔️ Full Cisco Intersight Integration  
Supports both:
- **Python SDK** → `intersight.api.*`
- **Signed REST API** → via `IntersightAuth`

### ✔️ 16+ Production-Ready MCP Tools  
Inventory, monitoring, reporting, and VM automation.

### ✔️ Private Network Deployment  
No cloud dependencies.  
Safe for enterprise workloads.

### ✔️ Docker + Python Support  
Run locally, in a VM, or in a container.

---

# 📁 Project Structure

```
IntersightMCPServer/
│
├── README.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
├── .env.example
│
├── intersight_server.py               # Main MCP server
├── test_mcp_tools.py                  # Client test script
├── get_tools.py                       # Utility to print list of tools
│
├── toolsfile/                         # (optional) extra tool modules
├── reports/                           # Generated Excel reports
├── logs/                              # Application logs
│
├── utils/
│   ├── intersight_auth.py             # Authentication for Python SDK
│   └── intersight_rest.py             # Authentication for REST API
│
├── models/
│   └── organization.py                # Example Pydantic model
│
└── NSDev01-SecretKey.txt              # Secret key (git ignored)
```

---

# 🔐 Environment Setup

Create `.env`:

```env
INTERSIGHT_API_KEY=<key-id>
INTERSIGHT_SECRET_FILE_PATH=C:/IntersightMCPServer/NSDev01-SecretKey.txt
INTERSIGHT_ENDPOINT=https://intersight.com/api/v1
```

Security:
- `.env` and secret files are already ignored by `.gitignore`
- Never commit your private key
- Rotate keys periodically

---

# 📦 Installing Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶ Starting the MCP Server

### Run directly (local Python):

```bash
fastmcp run intersight_server.py:mcp --transport http --port 8000
```

Server will start at:

```
http://localhost:8000/mcp
```

---

# 🧪 Testing with the Client

```bash
python test_mcp_tools.py
```

Example call:

```python
async with Client("http://127.0.0.1:8000/mcp") as client:
    result = await client.call_tool("power_on_a_vm", {"vm_name": "TestVM01"})
    print(result)
```

---

# 🐳 Docker Deployment

### 1. Build the image

```bash
docker build -t intersight-mcp-server .
```

### 2. Run with environment variables + mounted secret key

```bash
docker run -d   --name intersight_mcp   --env-file .env   -v C:/IntersightMCPServer/NSDev01-SecretKey.txt:/app/NSDev01-SecretKey.txt   -p 8000:8000   intersight-mcp-server
```

---

# 🐳 Docker-Compose

`docker-compose.yml`:

```yaml
services:
  mcp_server:
    build: .
    container_name: intersight_mcp_server
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./NSDev01-SecretKey.txt:/app/NSDev01-SecretKey.txt
      - ./reports:/app/reports
      - ./logs:/app/logs
```

Start with:

```bash
docker-compose up -d --build
```

---

# 🧰 MCP Tools Overview  
*(Tags + Input Names Only)*

## 🩺 1. health_check  
**Tags:** health, status, system  
**Inputs:** *(none)*  

## ➖ 2. calculate_sum  
**Tags:**  
**Inputs:** a, b  

## 🖥️ 3. generate_server_data_report  
**Tags:** compute, report, server  
**Inputs:** *(none)*  

## 🏢 4. get_organization_list  
**Tags:** iam, organization, rest  
**Inputs:** *(none)*  

## 🔗 5. get_fabric_interconnect_report  
**Tags:** fabric-interconnect, network, report  
**Inputs:** *(none)*  

## 🧩 6. generate_chassis_data_report  
**Tags:** chassis, ucs, report  
**Inputs:** *(none)*  

## 🧠 7. dimm_mirroring_tool  
**Tags:** bios, compute, dimm, memory, report  
**Inputs:** *(none)*  

## 🚨 8. get_intersight_alarms  
**Tags:** alarms, intersight, monitoring, report  
**Inputs:** from_date  

## 🖥️ 9. create_a_vm_through_ico  
**Tags:** compute, ico, vm, workflow  
**Inputs:** vm_name_value, vm_cpu_value, vm_mem_value, vm_network_value, cluster_name_value  

## 💾 10. create_vm_snapshot  
**Tags:** ico, snapshot, vm, workflow  
**Inputs:** vm_name_value, vm_snapshot_name_value, vm_snapshot_desc_value  

## 🌐 11. modify_vm_network  
**Tags:** ico, network, vm  
**Inputs:** vm_name_value, vm_network_value  

## 🔌 12. power_on_a_vm  
**Tags:** on, power, virtualization, vm  
**Inputs:** vm_name  

## ⚡ 13. power_off_a_vm  
**Tags:** off, power, virtualization, vm  
**Inputs:** vm_name  

## 📊 14. get_vm_cpu_utilization  
**Tags:** cpu, utilization, vm  
**Inputs:** *(none)*  

## 🧠 15. get_vm_memory_utilization  
**Tags:** memory, utilization, vm  
**Inputs:** *(none)*  

## 🔌 16. get_virtual_machines_powerstatus  
**Tags:** powerstate, report, vm  
**Inputs:** power_state  

---

# 🤝 Contributing

Pull requests welcome.

---

# 📄 License

Internal use only.
