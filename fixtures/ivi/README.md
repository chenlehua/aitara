# IVI Test Fixtures

This directory contains test fixture data for In-Vehicle Infotainment (IVI) system TARA analysis.

## File Structure

Per **specs/tara-design.md § 2.2.1** and **specs/tara-deepresearch.md § 4.1** requirements:

```
fixtures/ivi/
├── 系统定义与架构 (System Architecture)
│   ├── ivi_system_architecture.png   # System architecture diagram (PNG)
│   ├── ivi_data_flow_diagram.png     # Data flow diagram - DFD (PNG)
│   ├── ivi_trust_boundaries.png      # Trust boundary visualization (PNG)
│   ├── ivi_attack_tree.png           # Attack tree diagram (PNG)
│   └── system_architecture.json      # Structured architecture data (JSON)
│
├── 软硬件清单 (Bill of Materials)
│   ├── hardware_bom.csv              # Hardware BOM (CSV)
│   └── software_bom.csv              # Software BOM (CSV)
│
├── 网络通信 (Communication Matrix)
│   ├── communication_matrix.csv      # Signal definitions (CSV)
│   ├── communication_matrix.arxml    # AUTOSAR format (ARXML)
│   └── ivi_signals.dbc               # CAN database (DBC)
│
└── 功能规范 (Functional Specification)
    ├── functional_specification.json # Structured data (JSON)
    ├── functional_specification.md   # Document format (Markdown)
    └── functional_specification.pdf  # Document format (PDF)
```

## Data Categories Mapping

| 资料类别 | tara-deepresearch.md 4.1 | tara-design.md 2.2.1 | 本目录文件 |
|---------|-------------------------|---------------------|-----------|
| 系统架构图 | Visio, PNG, PDF | PDF, Visio, PNG/JPG | `ivi_system_architecture.png` |
| 数据流图 | PNG, Draw.io | (同上) | `ivi_data_flow_diagram.png` |
| 硬件BOM | Excel, CSV, CycloneDX | Excel | `hardware_bom.csv` |
| 软件BOM | Excel, CSV, CycloneDX | Excel | `software_bom.csv` |
| 通信矩阵 | DBC, ARXML, FIBEX | DBC, ARXML, Excel | `*.csv`, `*.dbc`, `*.arxml` |
| 功能规范 | Word, PDF | PDF | `*.md`, `*.pdf`, `*.json` |

---

## 1. System Architecture

### Diagram Files (PNG)

| File | Description | Key Information |
|------|-------------|-----------------|
| `ivi_system_architecture.png` | ECU connection topology | Trust boundaries, physical/logical connections |
| `ivi_data_flow_diagram.png` | Data flow between components | Data sensitivity, storage, transmission paths |
| `ivi_trust_boundaries.png` | Security zone visualization | External/User/Kernel/TrustZone/Vehicle boundaries |
| `ivi_attack_tree.png` | Threat modeling diagram | Attack vectors and paths |

### Structured Data (`system_architecture.json`)

Contains:
- **Trust Boundaries**: Security zones (External, User Space, Kernel, TrustZone, Vehicle Network)
- **Components**: Hardware (SoC, modules) and Software (OS, apps, services)
- **Interfaces**: External attack surfaces (WiFi, BT, USB, CAN, etc.)
- **Connections**: Data flows between components with security properties

---

## 2. Bill of Materials

### Hardware BOM (`hardware_bom.csv`)

| Field | Description |
|-------|-------------|
| id | Unique identifier (HW-xxx) |
| category | Component type (SoC, Memory, Communication, Interface, etc.) |
| name | Component name |
| manufacturer | Vendor |
| model | Part number |
| security_features | Built-in security capabilities |
| interfaces | Physical interfaces exposed |

### Software BOM (`software_bom.csv`)

| Field | Description |
|-------|-------------|
| id | Unique identifier (SW-xxx) |
| category | Software type (OS, Service, Library, Application, Bootloader) |
| name | Software name |
| vendor | Publisher |
| version | Version number |
| license | License type |
| known_vulnerabilities | Associated CVEs |
| security_config | Security configurations |

---

## 3. Communication Matrix

### CSV Format (`communication_matrix.csv`)

Tabular format with signal definitions:
- CAN ID, signal name, source/destination nodes
- Data encoding and security level

### DBC Format (`ivi_signals.dbc`)

Industry-standard Vector DBC format compatible with:
- CANdb++, Vehicle Spy, CANalyzer
- Python `cantools` library

### ARXML Format (`communication_matrix.arxml`)

AUTOSAR R4.0 compliant XML format containing:
- ECU instances and communication clusters
- I-PDU groups with security classifications
- Signal definitions with computation methods
- Frame triggerings with CAN ID assignments

---

## 4. Functional Specification

### JSON Format (`functional_specification.json`)

Structured data for programmatic processing:
- **Use Cases**: 10 detailed use cases with security requirements
  - UC-001: Media Playback from USB
  - UC-002: Bluetooth Phone Pairing
  - UC-003: Navigation Route Guidance
  - UC-004: Over-The-Air (OTA) Update
  - UC-005: Remote Door Lock/Unlock via Mobile App
  - UC-006: Web Browsing
  - UC-007: Apple CarPlay Connection
  - UC-008: Voice Command Recognition
  - UC-009: Vehicle Diagnostics Display
  - UC-010: WiFi Hotspot Sharing
- **Data Assets**: Sensitive data inventory with classification

### Document Formats (`functional_specification.md`, `functional_specification.pdf`)

Chinese-language functional specification document per ISO/SAE 21434:
- System architecture overview with trust boundaries
- Detailed use case specifications with security requirements (41 requirements)
- Data asset inventory with sensitivity classification (8 assets)
- Interface specifications (external and internal)
- Security requirements organized by STRIDE categories
- Terminology glossary

---

## Usage Examples

### Python - Load All Data

```python
import json
import csv
from pathlib import Path

fixtures = Path('fixtures/ivi')

# Load system architecture
with open(fixtures / 'system_architecture.json') as f:
    architecture = json.load(f)

# Load hardware BOM
with open(fixtures / 'hardware_bom.csv') as f:
    hardware_bom = list(csv.DictReader(f))

# Load software BOM
with open(fixtures / 'software_bom.csv') as f:
    software_bom = list(csv.DictReader(f))

# Load functional specification
with open(fixtures / 'functional_specification.json') as f:
    func_spec = json.load(f)

# Load DBC with cantools
import cantools
db = cantools.database.load_file(fixtures / 'ivi_signals.dbc')

# Load ARXML (requires autosar library)
# import autosar
# workspace = autosar.workspace()
# workspace.loadPackage(fixtures / 'communication_matrix.arxml')
```

### Neo4j - Import to Graph Database

```cypher
// Create components from architecture
UNWIND $components AS comp
CREATE (c:Component {
  id: comp.id,
  name: comp.name,
  type: comp.type,
  trust_boundary: comp.trust_boundary
})

// Create interfaces
UNWIND $interfaces AS iface
CREATE (i:Interface {
  id: iface.id,
  name: iface.name,
  type: iface.type,
  access_level: iface.access_level
})

// Create connections
UNWIND $connections AS conn
MATCH (src {id: conn.source})
MATCH (tgt {id: conn.target})
CREATE (src)-[:CONNECTS_TO {
  protocol: conn.protocol,
  encryption: conn.encryption
}]->(tgt)
```

---

## Security Levels

Signals and components are classified by security level:

| Level | Description | Examples |
|-------|-------------|----------|
| **Critical** | Safety/security impact | Remote door unlock, firmware, engine start |
| **High** | Privacy/diagnostic access | OBD-II, user credentials, certificates |
| **Medium** | Operational data | Vehicle speed, door status, parking brake |
| **Low** | Comfort/entertainment | Media, climate, volume settings |

---

## Related Components

These fixtures support TARA analysis for:
- **Asset Identification**: From BOMs and architecture diagrams
- **Threat Scenario Generation**: Based on interfaces and data flows
- **Attack Path Analysis**: Through component connections in graph database
- **Risk Assessment**: Using security classifications and STRIDE model
