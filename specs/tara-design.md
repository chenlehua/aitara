# AI TARA 智能威胁分析与风险评估平台设计文档

**版本**: 1.0.0
**日期**: 2026-01-29
**状态**: 设计阶段

---

## 目录

1. [概述](#1-概述)
2. [系统架构设计](#2-系统架构设计)
3. [技术栈规范](#3-技术栈规范)
4. [核心模块设计](#4-核心模块设计)
5. [数据模型设计](#5-数据模型设计)
6. [API接口设计](#6-api接口设计)
7. [AI推理引擎设计](#7-ai推理引擎设计)
8. [知识图谱设计](#8-知识图谱设计)
9. [工作流程设计](#9-工作流程设计)
10. [前端设计](#10-前端设计)
11. [部署架构](#11-部署架构)
12. [附录](#附录)

---

## 1. 概述

### 1.1 项目背景

随着汽车产业向"软件定义汽车"(Software Defined Vehicle, SDV)快速转型，车辆已从传统的机械设备演变为集成海量代码、复杂电子电气架构(E/E架构)及持续云端连接的智能移动终端。这种数字化转型虽带来了自动驾驶、智能座舱等革命性体验，但也使汽车网络安全面临前所未有的挑战。

传统的基于人工文档的威胁分析与风险评估(TARA)方法已无法满足快速迭代的开发需求及日益严苛的监管要求。本项目旨在构建一个面向汽车行业的智能TARA平台，实现对汽车网络安全风险的自动化、动态化与智能化分析。

### 1.2 设计目标

| 目标维度 | 具体目标 | 成功指标 |
|---------|---------|---------|
| **合规性** | 严格遵循ISO/SAE 21434标准及UN R155法规 | 100%覆盖标准条款 |
| **智能化** | 利用多模态AI自动识别架构图与生成威胁 | 识别准确率 > 90% |
| **高效性** | 将TARA分析周期从数周缩短至数小时 | 效率提升 > 10倍 |
| **可追溯** | 全流程记录，支持审计追溯 | 100%操作可追溯 |
| **可扩展** | 支持新车型、新威胁库的快速接入 | 扩展无需代码修改 |

### 1.3 核心场景

本平台重点针对以下两个高风险域进行深度分析：

- **车载信息娱乐系统 (IVI)**: 代码量最大、对外接口最多，是最高危的攻击面
- **远程信息处理器 (T-BOX)**: 车辆的"调制解调器"，负责所有与云端的通信，是远程控制功能的物理入口

### 1.4 术语定义

| 术语 | 全称 | 说明 |
|-----|------|-----|
| TARA | Threat Analysis and Risk Assessment | 威胁分析与风险评估 |
| IVI | In-Vehicle Infotainment | 车载信息娱乐系统 |
| T-BOX | Telematics Box | 远程信息处理器 |
| STRIDE | Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege | 威胁分类模型 |
| SFOP | Safety, Financial, Operational, Privacy | 影响评估维度 |
| BOM | Bill of Materials | 物料清单 |
| DFD | Data Flow Diagram | 数据流图 |

---

## 2. 系统架构设计

### 2.1 整体架构图

```mermaid
flowchart TB
    subgraph ClientLayer["客户端层 (Client Layer)"]
        WebApp["Web应用<br/>React 19.2 + TypeScript 5.9"]
    end

    subgraph ServiceLayer["服务层 (Service Layer)"]
        subgraph CoreServices["核心业务服务"]
            AssetService["资产管理服务"]
            ThreatService["威胁分析服务"]
            RiskService["风险评估服务"]
            ReportService["报告生成服务"]
        end

        subgraph AIServices["AI推理服务"]
            VisionService["视觉解析服务<br/>Qwen3-VL"]
            ReasoningService["推理分析服务<br/>Qwen-Max"]
            EmbeddingService["向量嵌入服务<br/>text-embedding-v3"]
        end

        subgraph EngineServices["引擎服务"]
            GraphEngine["图计算引擎"]
            RAGEngine["RAG检索引擎"]
            RuleEngine["规则引擎"]
        end
    end

    subgraph DataLayer["数据层 (Data Layer)"]
        Neo4j[(Neo4j 2025.12<br/>知识图谱)]
        Milvus[(Milvus 2.6.9<br/>向量数据库)]
        PostgreSQL[(PostgreSQL 16<br/>业务数据)]
        Redis[(Redis 7<br/>缓存/任务队列)]
        MinIO[(MinIO<br/>文件存储)]
    end

    subgraph ExternalLayer["外部服务层"]
        AliyunBailian["阿里云百炼平台<br/>Qwen API"]
        CVEDatabase["CVE漏洞库"]
        ThreatIntel["威胁情报源"]
    end

    ClientLayer --> ServiceLayer
    CoreServices <--> AIServices
    CoreServices <--> EngineServices
    AIServices --> AliyunBailian
    ServiceLayer --> DataLayer
    EngineServices --> ExternalLayer

    style ClientLayer fill:#e1f5fe
    style ServiceLayer fill:#e8f5e9
    style DataLayer fill:#fce4ec
    style ExternalLayer fill:#f3e5f5
```

### 2.1.1 外部数据源集成架构

平台集成多个外部安全数据源，包括CVE漏洞库和威胁情报源，以增强威胁分析的准确性和时效性。

```mermaid
flowchart TB
    subgraph ExternalSources["外部数据源"]
        NVD["NVD<br/>美国国家漏洞库"]
        MITRE["MITRE ATT&CK<br/>for ICS/Vehicle"]
        UNR155Catalog["UN R155<br/>威胁目录"]
    end

    subgraph SyncLayer["数据同步层"]
        Scheduler["定时调度器<br/>Cron/APScheduler"]
        Fetcher["数据拉取器"]
        Transformer["数据转换器"]
        Deduplicator["去重/更新器"]
    end

    subgraph LocalStorage["本地存储层"]
        subgraph Cache["缓存层 - Redis"]
            HotCVE["热点CVE缓存"]
            ThreatCache["威胁模式缓存"]
        end

        subgraph Persistent["持久化层"]
            Milvus2["Milvus<br/>向量索引"]
            Neo4j2["Neo4j<br/>关系图谱"]
            PostgreSQL2["PostgreSQL<br/>元数据"]
        end
    end

    subgraph Application["应用层"]
        ThreatAnalysis["威胁分析服务"]
        VulnMatch["漏洞匹配服务"]
        RAGRetrieval["RAG检索服务"]
    end

    NVD --> Fetcher
    MITRE --> Fetcher
    UNR155Catalog --> Fetcher
    Scheduler --> Fetcher
    Fetcher --> Transformer
    Transformer --> Deduplicator
    Deduplicator --> Cache
    Deduplicator --> Persistent

    Cache --> Application
    Persistent --> Application

    style ExternalSources fill:#f3e5f5
    style SyncLayer fill:#e3f2fd
    style LocalStorage fill:#fff3e0
    style Application fill:#e8f5e9
```

### 2.1.2 CVE漏洞库集成设计

#### 支持的CVE数据源

| 数据源 | 描述 | 更新频率 | 数据格式 |
|-------|------|---------|---------|
| **NVD (National Vulnerability Database)** | 美国NIST维护的国家漏洞库，最全面的CVE信息源 | 实时更新 | JSON/CVE 5.0 |

#### 数据同步机制

```mermaid
flowchart LR
    subgraph SyncProcess["同步流程"]
        direction TB
        A["定时触发<br/>每6小时"] --> B["增量拉取<br/>基于last_modified"]
        B --> C{"数据变更?"}
        C -->|是| D["数据转换<br/>统一格式"]
        C -->|否| E["跳过"]
        D --> F["向量化<br/>text-embedding-v3"]
        F --> G["写入Milvus"]
        D --> H["写入Neo4j<br/>建立关联"]
        G --> I["更新缓存"]
        H --> I
    end

    subgraph IncrementalUpdate["增量更新策略"]
        direction TB
        J["记录last_sync_time"] --> K["请求modified_since"]
        K --> L["仅处理变更数据"]
        L --> M["更新or插入"]
    end

    SyncProcess ~~~ IncrementalUpdate

    style SyncProcess fill:#e3f2fd
    style IncrementalUpdate fill:#e8f5e9
```

#### 漏洞数据模型

| 字段 | 类型 | 描述 |
|-----|------|------|
| `cve_id` | string | CVE标识符，如 CVE-2024-12345 |
| `description` | text | 漏洞描述 |
| `cvss_v3_score` | float | CVSS 3.x 评分 (0-10) |
| `cvss_v3_vector` | string | CVSS 3.x 向量字符串 |
| `cwe_id` | string | CWE弱点分类标识 |
| `affected_products` | list[string] | 受影响产品CPE列表 |
| `affected_versions` | list[string] | 受影响版本范围 |
| `published_date` | datetime | 发布日期 |
| `last_modified_date` | datetime | 最后修改日期 |
| `references` | list[string] | 参考链接列表 |
| `exploit_available` | boolean | 是否有公开利用代码 |
| `patch_available` | boolean | 是否有补丁 |

#### 资产-漏洞关联匹配逻辑

```mermaid
flowchart TB
    subgraph AssetInput["资产输入"]
        Asset["软件资产<br/>name, vendor, version"]
    end

    subgraph MatchingProcess["匹配流程"]
        A["CPE构建<br/>cpe:2.3:a:vendor:product:version"] --> B["精确匹配<br/>CPE字典匹配"]
        B --> C{"匹配成功?"}
        C -->|是| D["返回CVE列表"]
        C -->|否| E["模糊匹配<br/>名称相似度"]
        E --> F["语义匹配<br/>向量相似度 > 0.85"]
        F --> G{"匹配成功?"}
        G -->|是| D
        G -->|否| H["无已知漏洞"]
    end

    subgraph Output["输出"]
        D --> I["关联CVE列表<br/>按CVSS评分排序"]
        I --> J["自动创建<br/>Vulnerability节点"]
        J --> K["建立AFFECTS关系"]
    end

    AssetInput --> A

    style AssetInput fill:#e3f2fd
    style MatchingProcess fill:#fff3e0
    style Output fill:#e8f5e9
```

### 2.1.3 威胁情报源集成设计

#### MITRE ATT&CK for ICS/Vehicle 集成

| 集成项 | 描述 | 用途 |
|-------|------|-----|
| **战术 (Tactics)** | 攻击者的高层目标，如初始访问、执行、持久化等 | 威胁场景分类 |
| **技术 (Techniques)** | 实现战术的具体方法，如钓鱼、漏洞利用等 | 威胁描述细化 |
| **子技术 (Sub-techniques)** | 技术的更细粒度分类 | 攻击步骤详述 |
| **缓解措施 (Mitigations)** | 针对技术的防御建议 | 安全建议生成 |
| **检测方法 (Detections)** | 检测攻击的方法 | 监控建议生成 |

```mermaid
flowchart LR
    subgraph ATTCKData["ATT&CK数据结构"]
        Tactic["战术<br/>TA00xx"]
        Technique["技术<br/>T1xxx"]
        SubTech["子技术<br/>T1xxx.xxx"]
        Mitigation["缓解措施<br/>M1xxx"]
    end

    subgraph Mapping["映射关系"]
        Tactic --> |"包含"| Technique
        Technique --> |"细分"| SubTech
        Mitigation --> |"缓解"| Technique
    end

    subgraph TARAIntegration["TARA集成"]
        Threat["威胁场景"]
        AttackPath["攻击路径"]
        Recommendation["安全建议"]
    end

    Technique --> |"关联"| Threat
    SubTech --> |"构成"| AttackPath
    Mitigation --> |"生成"| Recommendation

    style ATTCKData fill:#ffebee
    style Mapping fill:#e3f2fd
    style TARAIntegration fill:#e8f5e9
```

#### UN R155威胁目录集成

UN R155 Annex 5定义了车辆网络安全威胁和攻击的标准分类，平台完整集成该目录用于威胁合规性映射。

| 威胁类别 | 描述 | 示例 |
|---------|------|-----|
| **与后端服务器相关的威胁** | 针对车辆连接的云服务攻击 | 服务器欺骗、中间人攻击 |
| **与通信信道相关的威胁** | 车辆通信链路上的攻击 | 数据窃听、信号干扰 |
| **与更新程序相关的威胁** | 软件/固件更新过程的攻击 | 恶意更新、回滚攻击 |
| **与意外人为操作相关的威胁** | 人为失误导致的安全问题 | 配置错误、凭证泄露 |
| **与外部连接相关的威胁** | 外部接口上的攻击 | USB攻击、OBD-II利用 |
| **与数据/代码相关的威胁** | 针对车载数据和软件的攻击 | 数据篡改、代码注入 |
| **潜在漏洞利用** | 通用软件漏洞的利用 | 缓冲区溢出、权限提升 |

#### 情报更新机制

```mermaid
flowchart TB
    subgraph UpdateTriggers["更新触发方式"]
        Scheduled["定时更新<br/>每日凌晨"]
        Webhook["实时推送<br/>TAXII订阅"]
        Manual["手动触发<br/>管理员操作"]
    end

    subgraph UpdateProcess["更新流程"]
        A["拉取最新数据"] --> B["解析STIX/JSON"]
        B --> C["版本比对"]
        C --> D{"有更新?"}
        D -->|是| E["增量更新知识库"]
        D -->|否| F["记录检查时间"]
        E --> G["重建向量索引"]
        G --> H["刷新缓存"]
        H --> I["通知相关服务"]
    end

    subgraph ThreatLinkage["威胁关联"]
        J["新情报入库"] --> K["自动关联<br/>已有威胁场景"]
        K --> L["更新威胁描述"]
        K --> M["补充攻击技术"]
        K --> N["推送通知<br/>受影响项目"]
    end

    UpdateTriggers --> A
    I --> J

    style UpdateTriggers fill:#e3f2fd
    style UpdateProcess fill:#fff3e0
    style ThreatLinkage fill:#e8f5e9
```

#### 情报与威胁分析的关联

| 情报类型 | 关联方式 | 应用场景 |
|---------|---------|---------|
| **CVE漏洞** | 按软件组件CPE匹配 | 自动识别资产已知漏洞 |
| **ATT&CK技术** | 按威胁描述语义匹配 | 丰富威胁场景的攻击技术细节 |
| **UN R155威胁** | 按威胁类别映射 | 生成合规性报告，关联标准条款 |
| **历史案例** | 按相似度检索 | 参考历史TARA分析结果 |

### 2.2 分层架构详解

#### 2.2.1 数据接入层 (Data Ingestion Layer)

负责处理多源异构的工程数据，包括PDF格式的需求规范、Visio/PNG格式的架构图、Excel格式的信号矩阵、XML格式的ARXML文件。

```mermaid
flowchart LR
    subgraph InputFormats["输入格式"]
        PDF["PDF文档"]
        Visio["Visio图纸"]
        PNG["PNG/JPG图片"]
        Excel["Excel表格"]
        ARXML["ARXML文件"]
        DBC["DBC信号矩阵"]
    end

    subgraph Parsers["解析器集群"]
        PDFParser["PDF解析器"]
        ImageParser["图像解析器"]
        ExcelParser["Excel解析器"]
        XMLParser["XML解析器"]
    end

    subgraph AIProcessing["AI处理"]
        QwenVL["Qwen3-VL<br/>多模态理解"]
        OCR["OCR引擎"]
    end

    subgraph Output["结构化输出"]
        JSON["JSON结构"]
        GraphData["图数据"]
    end

    PDF --> PDFParser
    Visio --> ImageParser
    PNG --> ImageParser
    Excel --> ExcelParser
    ARXML --> XMLParser
    DBC --> XMLParser

    PDFParser --> QwenVL
    ImageParser --> QwenVL
    ExcelParser --> JSON
    XMLParser --> JSON
    QwenVL --> JSON
    OCR --> JSON
    JSON --> GraphData

    style AIProcessing fill:#e8f5e9
```

#### 2.2.2 知识图谱层 (Knowledge Graph Layer)

平台的"大脑"，用于存储车辆的数字孪生模型。基于Neo4j图数据库，存储资产、组件、接口、漏洞、威胁及其之间的复杂关系。

#### 2.2.3 AI推理层 (AI Reasoning Layer)

基于阿里云百炼平台的Qwen系列模型构建，包括多模态视觉理解、逻辑推理、语义检索三大能力。

#### 2.2.4 业务应用层 (Application Layer)

提供可视化交互界面，展示攻击路径图、风险热力图，并生成符合ISO 21434标准的报告。

### 2.3 组件交互图

```mermaid
C4Component
    title AI TARA 平台组件交互图

    Container_Boundary(frontend, "前端应用") {
        Component(webUI, "Web UI", "React 19.2", "用户交互界面")
        Component(graphViz, "图形可视化", "D3.js/Cytoscape", "攻击路径可视化")
        Component(reportViewer, "报告查看器", "PDF.js", "在线预览报告")
    }

    Container_Boundary(backend, "后端服务") {
        Component(apiRouter, "API路由", "FastAPI", "请求路由分发")
        Component(assetModule, "资产模块", "Python", "资产管理逻辑")
        Component(threatModule, "威胁模块", "Python", "威胁分析逻辑")
        Component(riskModule, "风险模块", "Python", "风险计算逻辑")
        Component(reportModule, "报告模块", "Python", "报告生成逻辑")
    }

    Container_Boundary(aiEngine, "AI引擎") {
        Component(visionAgent, "视觉Agent", "Qwen3-VL", "图纸解析")
        Component(reasonAgent, "推理Agent", "Qwen-Max", "威胁推理")
        Component(ragAgent, "RAG Agent", "Embedding", "知识检索")
    }

    Container_Boundary(dataStore, "数据存储") {
        ComponentDb(graphDB, "图数据库", "Neo4j", "知识图谱")
        ComponentDb(vectorDB, "向量库", "Milvus", "语义索引")
        ComponentDb(relDB, "关系数据库", "PostgreSQL", "业务数据")
        ComponentDb(cache, "缓存", "Redis", "热点数据/任务队列")
        ComponentDb(fileStore, "文件存储", "MinIO", "原始文件")
    }

    Rel(webUI, apiRouter, "HTTP/REST")
    Rel(apiRouter, assetModule, "资产操作")
    Rel(apiRouter, threatModule, "威胁分析")
    Rel(apiRouter, riskModule, "风险评估")
    Rel(apiRouter, reportModule, "报告生成")

    Rel(assetModule, visionAgent, "图纸解析")
    Rel(threatModule, reasonAgent, "威胁生成")
    Rel(threatModule, ragAgent, "知识检索")

    Rel(assetModule, graphDB, "存取资产")
    Rel(ragAgent, vectorDB, "向量检索")
    Rel(assetModule, fileStore, "文件管理")
    Rel(reportModule, relDB, "报告元数据")
    Rel(apiRouter, cache, "缓存查询")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="2")
```

---

## 3. 技术栈规范

### 3.1 后端技术栈

| 技术组件 | 版本 | 用途 | 选型理由 |
|---------|------|-----|---------|
| **Python** | 3.12+ | 后端开发语言 | 丰富的AI生态、类型提示支持 |
| **uv** | 0.9.27 | 包管理器 | Rust实现，速度极快(10-100x pip) |
| **FastAPI** | 0.128.0 | Web框架 | 高性能异步、自动OpenAPI文档 |
| **Pydantic** | 2.12.5 | 数据验证 | 类型安全、性能优异 |
| **structlog** | 25.5.0 | 结构化日志 | JSON输出、上下文绑定 |
| **Neo4j Driver** | 6.1.0 | 图数据库驱动 | 官方异步驱动 |
| **Milvus SDK** | 2.6.x | 向量数据库SDK | 高性能向量检索 |
| **DashScope SDK** | latest | 阿里云AI SDK | 调用Qwen系列模型 |

### 3.2 前端技术栈

| 技术组件 | 版本 | 用途 | 选型理由 |
|---------|------|-----|---------|
| **React** | 19.2.4 | UI框架 | Effect Events、Server Components |
| **TypeScript** | 5.9 | 开发语言 | 类型安全、IDE支持 |
| **Vite** | 7.3.1 | 构建工具 | 极速HMR、优化构建 |
| **Tailwind CSS** | 4.1.18 | CSS框架 | 原子化CSS、5x构建加速 |
| **TanStack Query** | 5.x | 数据获取 | 缓存、乐观更新 |
| **D3.js** | 7.x | 数据可视化 | 自定义图表 |
| **Cytoscape.js** | 3.x | 图可视化 | 网络图、攻击路径 |
| **Zustand** | 5.x | 状态管理 | 轻量、简洁 |

### 3.3 数据存储

| 技术组件 | 版本 | 用途 | 选型理由 |
|---------|------|-----|---------|
| **Neo4j** | 2025.12.1 | 图数据库 | 攻击路径分析、关系查询 |
| **Milvus** | 2.6.9 | 向量数据库 | RAG检索、语义搜索 |
| **PostgreSQL** | 16.x | 关系数据库 | 业务数据、用户管理 |
| **Redis** | 7.x | 缓存 | 会话管理、热点数据 |
| **MinIO** | latest | 对象存储 | 文件存储、兼容S3 |

### 3.4 AI模型

| 模型 | 用途 | 特点 |
|-----|------|-----|
| **Qwen3-VL-Max** | 架构图解析、文档OCR | 高精度视觉理解、3D定位 |
| **Qwen-Max** | 威胁推理、风险评估 | 最强逻辑推理能力 |
| **Qwen-Plus** | 文本处理、格式化 | 性价比平衡 |
| **text-embedding-v3** | 向量嵌入 | RAG检索基础 |

### 3.5 依赖版本锁定策略

```mermaid
flowchart TD
    subgraph VersionPolicy["版本管理策略"]
        Major["主版本 (Major)"]
        Minor["次版本 (Minor)"]
        Patch["补丁版本 (Patch)"]
    end

    subgraph Constraints["约束规则"]
        ProdLock["生产环境: 精确锁定"]
        DevRange["开发环境: 允许补丁更新"]
        SecurityUpdate["安全更新: 立即升级"]
    end

    Major --> ProdLock
    Minor --> DevRange
    Patch --> DevRange
    SecurityUpdate --> ProdLock

    style VersionPolicy fill:#e3f2fd
    style Constraints fill:#fff8e1
```

---

## 4. 核心模块设计

### 4.1 模块划分

```mermaid
flowchart TB
    subgraph DomainLayer["领域层 (Domain Layer)"]
        AssetDomain["资产域<br/>Asset Domain"]
        ThreatDomain["威胁域<br/>Threat Domain"]
        RiskDomain["风险域<br/>Risk Domain"]
        ReportDomain["报告域<br/>Report Domain"]
    end

    subgraph ApplicationLayer["应用层 (Application Layer)"]
        AssetService["资产服务"]
        ThreatService["威胁服务"]
        RiskService["风险服务"]
        ReportService["报告服务"]
        ProjectService["项目服务"]
    end

    subgraph InfraLayer["基础设施层 (Infrastructure Layer)"]
        GraphRepository["图仓库<br/>Neo4j"]
        VectorRepository["向量仓库<br/>Milvus"]
        FileRepository["文件仓库<br/>MinIO"]
        AIGateway["AI网关<br/>DashScope"]
    end

    AssetDomain --> AssetService
    ThreatDomain --> ThreatService
    RiskDomain --> RiskService
    ReportDomain --> ReportService

    AssetService --> GraphRepository
    AssetService --> FileRepository
    AssetService --> AIGateway
    ThreatService --> GraphRepository
    ThreatService --> VectorRepository
    ThreatService --> AIGateway
    RiskService --> GraphRepository
    ReportService --> FileRepository

    style DomainLayer fill:#e8f5e9
    style ApplicationLayer fill:#e3f2fd
    style InfraLayer fill:#fce4ec
```

### 4.2 资产管理模块

#### 4.2.1 功能描述

资产管理模块负责从多种格式的工程文档中提取、识别和管理网络安全资产。

```mermaid
flowchart LR
    subgraph Input["输入源"]
        BOM["软硬件BOM"]
        DFD["数据流图"]
        Arch["系统架构图"]
        Spec["功能规范"]
    end

    subgraph Processing["处理流程"]
        Parse["解析提取"]
        Identify["资产识别"]
        Classify["资产分类"]
        Relate["关系建立"]
    end

    subgraph Output["输出"]
        AssetGraph["资产图谱"]
        AssetList["资产清单"]
        TrustBoundary["信任边界"]
    end

    Input --> Parse
    Parse --> Identify
    Identify --> Classify
    Classify --> Relate
    Relate --> Output

    style Processing fill:#e8f5e9
```

#### 4.2.2 资产分类体系

```mermaid
mindmap
    root((资产类型))
        硬件资产
            ECU控制器
            传感器
            通信模组
            存储介质
            调试接口
        软件资产
            操作系统
            中间件
            应用程序
            第三方库
            固件
        数据资产
            用户数据
            配置数据
            密钥证书
            日志数据
            固件镜像
        接口资产
            物理接口
                USB
                OBD-II
                JTAG
            无线接口
                Bluetooth
                Wi-Fi
                Cellular
            车内总线
                CAN
                Ethernet
                LIN
```

#### 4.2.3 详细设计

##### 领域模型

资产域采用继承结构设计，基类 `Asset` 定义通用属性，各子类扩展特定属性。

```mermaid
classDiagram
    class Asset {
        <<abstract>>
        +string id
        +string name
        +AssetType asset_type
        +string description
        +SecurityProperty[] security_properties
        +dict metadata
        +datetime created_at
    }

    class HardwareAsset {
        +HardwareCategory category
        +string vendor
        +string model
        +string version
        +string[] interfaces
    }

    class SoftwareAsset {
        +string version
        +string vendor
        +string license_type
        +string[] dependencies
        +string[] cve_ids
    }

    class DataAsset {
        +string sensitivity
        +string data_format
        +string storage_location
        +string retention_period
    }

    class InterfaceAsset {
        +InterfaceCategory category
        +string protocol
        +string access_level
        +string[] data_flows
    }

    Asset <|-- HardwareAsset
    Asset <|-- SoftwareAsset
    Asset <|-- DataAsset
    Asset <|-- InterfaceAsset
```

**资产类型枚举定义**

| 枚举类型 | 枚举值 | 说明 |
|---------|-------|------|
| **AssetType** | `hardware` | 硬件资产 |
| | `software` | 软件资产 |
| | `data` | 数据资产 |
| | `interface` | 接口资产 |
| **HardwareCategory** | `ecu` | ECU控制器 |
| | `sensor` | 传感器 |
| | `comm_module` | 通信模组 |
| | `storage` | 存储介质 |
| | `debug_port` | 调试端口 |
| **InterfaceCategory** | `physical` | 物理接口 (USB, OBD-II, JTAG) |
| | `wireless` | 无线接口 (BT, WiFi, Cellular) |
| | `vehicle_bus` | 车内总线 (CAN, Ethernet, LIN) |
| **SecurityProperty** | `confidentiality` | 机密性 |
| | `integrity` | 完整性 |
| | `availability` | 可用性 |
| | `authenticity` | 真实性 |
| | `non_repudiation` | 不可否认性 |

##### 服务层设计

资产服务依赖多个基础设施组件，通过依赖注入实现松耦合。

```mermaid
classDiagram
    class AssetService {
        -AssetRepository repository
        -FileParser file_parser
        -VisionService vision_service
        -FileStorage file_storage
        -CacheService cache
        +upload_and_parse(project_id, file_content, file_name, file_type) ParseResult
        +get_asset_graph(project_id) AssetGraph
        +identify_trust_boundaries(project_id) TrustBoundary[]
        +list_assets(project_id, filters) Asset[]
        +get_asset(asset_id) Asset
    }

    class AssetRepository {
        <<interface>>
        +save(asset) string
        +get_by_id(asset_id) Asset
        +list_by_project(project_id) Asset[]
        +delete(asset_id) bool
        +update(asset) bool
        +get_relations(project_id) Relation[]
    }

    class FileParser {
        <<interface>>
        +parse(file_content, file_type) ParsedResult
    }

    class VisionService {
        <<interface>>
        +analyze_image(image) ArchitectureAnalysis
    }

    class FileStorage {
        <<interface>>
        +save(bucket, key, content) string
        +get(bucket, key) bytes
        +delete(bucket, key) bool
    }

    class CacheService {
        <<interface>>
        +get(key) any
        +set(key, value, ttl) bool
        +delete(key) bool
    }

    AssetService --> AssetRepository
    AssetService --> FileParser
    AssetService --> VisionService
    AssetService --> FileStorage
    AssetService --> CacheService
```

**服务接口契约**

| 接口 | 方法 | 输入参数 | 输出 | 说明 |
|-----|------|---------|------|------|
| **AssetRepository** | `save` | `Asset` | `string` (id) | 保存资产到Neo4j |
| | `get_by_id` | `asset_id: string` | `Asset \| None` | 按ID查询资产 |
| | `list_by_project` | `project_id: string` | `Asset[]` | 查询项目所有资产 |
| | `get_relations` | `project_id: string` | `Relation[]` | 查询资产间关系 |
| **FileParser** | `parse` | `content: bytes, type: string` | `ParsedResult` | 解析结构化文件 |
| **VisionService** | `analyze_image` | `image: bytes` | `ArchitectureAnalysis` | AI解析架构图 |
| **FileStorage** | `save` | `bucket, key, content` | `string` (path) | 存储文件到MinIO |
| **CacheService** | `get/set/delete` | `key, value, ttl` | 缓存操作 | Redis缓存操作 |

##### 资产解析流程

```mermaid
flowchart TB
    subgraph Upload["文件上传"]
        A["接收文件"] --> B["验证文件类型/大小"]
        B --> C["存储到MinIO"]
        C --> D["返回file_id"]
    end

    subgraph Parse["文件解析"]
        D --> E{"文件类型判断"}
        E -->|"图片/Visio"| F["调用VisionService<br/>Qwen3-VL解析"]
        E -->|"Excel/XML"| G["调用FileParser<br/>规则解析"]
        F --> H["提取组件/连接/边界"]
        G --> I["提取资产属性"]
    end

    subgraph Persist["数据持久化"]
        H --> J["转换为Asset实体"]
        I --> J
        J --> K["写入Neo4j图数据库"]
        K --> L["建立资产间关系"]
        L --> M["清除项目缓存"]
    end

    subgraph Return["返回结果"]
        M --> N["返回ParseResult<br/>file_id + assets"]
    end

    style Upload fill:#e3f2fd
    style Parse fill:#e8f5e9
    style Persist fill:#fff3e0
    style Return fill:#f3e5f5
```

##### 文件解析器设计

系统支持多种文件格式的解析，采用策略模式根据文件类型选择对应的解析器。

```mermaid
flowchart LR
    subgraph Parsers["解析器集群"]
        ExcelParser["Excel解析器<br/>BOM清单"]
        XMLParser["XML解析器<br/>ARXML/DBC"]
        ImageParser["图像解析器<br/>PNG/JPG/Visio"]
        PDFParser["PDF解析器<br/>规范文档"]
    end

    subgraph ParseStrategy["解析策略"]
        Strategy{"文件类型<br/>路由"}
    end

    subgraph Output["统一输出"]
        ParsedResult["ParsedResult<br/>统一数据结构"]
    end

    Strategy -->|".xlsx/.xls"| ExcelParser
    Strategy -->|".xml/.arxml/.dbc"| XMLParser
    Strategy -->|".png/.jpg/.vsdx"| ImageParser
    Strategy -->|".pdf"| PDFParser

    ExcelParser --> ParsedResult
    XMLParser --> ParsedResult
    ImageParser --> ParsedResult
    PDFParser --> ParsedResult

    style Parsers fill:#e8f5e9
    style ParseStrategy fill:#e3f2fd
```

**Excel BOM解析列映射**

| 原始列名 (中文) | 原始列名 (英文) | 映射字段 | 说明 |
|---------------|---------------|---------|------|
| 零件号 | Part Number | `part_number` | 唯一标识 |
| 名称 | Name | `name` | 资产名称 |
| 类型 | Type | `asset_type` | 资产类型 |
| 供应商 | Vendor | `vendor` | 供应商名称 |
| 版本 | Version | `version` | 版本号 |
| 描述 | Description | `description` | 详细描述 |

**资产类型自动识别规则**

| 关键词 | 识别为 |
|-------|-------|
| `硬件`, `hardware`, `ecu`, `sensor`, `mcu` | HardwareAsset |
| `软件`, `software`, `app`, `middleware`, `os` | SoftwareAsset |
| `数据`, `data`, `config`, `key` | DataAsset |
| `接口`, `interface`, `port`, `bus` | InterfaceAsset |

##### 信任边界识别

系统根据接口类型和访问级别自动识别信任边界，用于后续威胁分析。

```mermaid
flowchart TB
    subgraph Input["输入"]
        Assets["项目资产列表"]
    end

    subgraph Classification["边界分类"]
        A["筛选接口资产"] --> B{"访问级别判断"}
        B -->|"public"| C["外部网络边界<br/>level: untrusted"]
        B -->|"internal"| D["内部网络边界<br/>level: semi-trusted"]
        B -->|"restricted"| E["核心安全边界<br/>level: trusted"]
    end

    subgraph Grouping["边界分组"]
        C --> F["按协议类型分组"]
        D --> F
        E --> F
        F --> G["生成TrustBoundary实体"]
    end

    subgraph Output["输出"]
        G --> H["信任边界列表"]
    end

    Assets --> A

    style Classification fill:#ffebee
    style Grouping fill:#e8f5e9
```

**信任边界级别定义**

| 边界级别 | 访问级别 | 典型资产 | 安全要求 |
|---------|---------|---------|---------|
| **untrusted** | public | 蜂窝网络、WiFi、蓝牙 | 强认证、加密、限流 |
| **semi-trusted** | internal | CAN总线、车载以太网 | 消息认证、访问控制 |
| **trusted** | restricted | 安全启动、HSM | 最高安全等级保护 |

### 4.3 威胁分析模块

#### 4.3.1 STRIDE威胁模型

```mermaid
flowchart TB
    subgraph STRIDEModel["STRIDE威胁模型"]
        S["**S - Spoofing**<br/>身份欺骗<br/>违反: 认证性"]
        T["**T - Tampering**<br/>数据篡改<br/>违反: 完整性"]
        R["**R - Repudiation**<br/>否认<br/>违反: 不可否认性"]
        I["**I - Information Disclosure**<br/>信息泄露<br/>违反: 保密性"]
        D["**D - Denial of Service**<br/>拒绝服务<br/>违反: 可用性"]
        E["**E - Elevation of Privilege**<br/>权限提升<br/>违反: 授权"]
    end

    subgraph DataFlow["数据流元素"]
        Process["进程"]
        DataStore["数据存储"]
        DataFlowLine["数据流"]
        ExternalEntity["外部实体"]
        TrustBoundaryLine["信任边界"]
    end

    subgraph Mapping["威胁映射"]
        Process --> S & T & R & I & D & E
        DataStore --> T & I & D
        DataFlowLine --> T & I & D
        ExternalEntity --> S & R
    end

    style STRIDEModel fill:#ffebee
    style DataFlow fill:#e3f2fd
```

#### 4.3.2 威胁生成流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant API as API服务
    participant ThreatAgent as 威胁Agent
    participant RAG as RAG引擎
    participant Qwen as Qwen-Max
    participant Graph as Neo4j

    User->>API: 请求威胁分析
    API->>Graph: 查询目标资产
    Graph-->>API: 返回资产信息及关系

    API->>ThreatAgent: 启动威胁分析
    ThreatAgent->>RAG: 检索相关威胁知识
    RAG-->>ThreatAgent: 返回历史案例、CVE、ATT&CK

    ThreatAgent->>Qwen: 生成威胁场景
    Note over Qwen: 基于STRIDE模型<br/>结合资产属性<br/>参考检索知识
    Qwen-->>ThreatAgent: 返回威胁描述

    ThreatAgent->>Graph: 存储威胁实体与关系
    ThreatAgent-->>API: 返回分析结果
    API-->>User: 展示威胁列表
```

#### 4.3.3 详细设计

##### 领域模型

威胁域包含威胁实体、攻击路径和威胁场景三个核心概念。

```mermaid
classDiagram
    class Threat {
        +string id
        +string project_id
        +string description
        +StrideCategory stride_category
        +AttackVector attack_vector
        +ThreatStatus status
        +string[] target_assets
        +string[] affected_data_flows
        +string[] related_cve_ids
        +string unr155_threat_id
        +float confidence_score
        +string source
        +datetime created_at
        +datetime updated_at
    }

    class AttackPath {
        +string id
        +string threat_id
        +string entry_point
        +string target
        +string[] path_nodes
        +dict[] path_edges
        +int hop_count
        +dict feasibility_factors
    }

    class ThreatScenario {
        +Threat threat
        +AttackPath[] attack_paths
        +string[] preconditions
        +string[] attack_steps
        +string impact_description
        +dict sfop_impact
    }

    Threat "1" --> "*" AttackPath : has
    ThreatScenario --> "1" Threat : contains
    ThreatScenario --> "*" AttackPath : includes
```

**威胁相关枚举定义**

| 枚举类型 | 枚举值 | 说明 |
|---------|-------|------|
| **StrideCategory** | `spoofing` | 身份欺骗 - 违反认证性 |
| | `tampering` | 数据篡改 - 违反完整性 |
| | `repudiation` | 否认 - 违反不可否认性 |
| | `info_disclosure` | 信息泄露 - 违反保密性 |
| | `dos` | 拒绝服务 - 违反可用性 |
| | `elevation` | 权限提升 - 违反授权 |
| **ThreatStatus** | `identified` | 已识别 (AI生成) |
| | `confirmed` | 已确认 (人工审核) |
| | `mitigated` | 已缓解 (有措施) |
| | `accepted` | 已接受 (风险可接受) |
| | `rejected` | 已拒绝 (误报) |
| **AttackVector** | `network` | 网络攻击 - 远程利用 |
| | `adjacent` | 相邻网络 - 需同一网段 |
| | `local` | 本地攻击 - 需物理/逻辑访问 |
| | `physical` | 物理攻击 - 需物理接触 |

##### 服务层设计

威胁分析服务整合多个组件完成端到端的威胁识别流程。

```mermaid
classDiagram
    class ThreatService {
        -ThreatRepository threat_repository
        -AssetRepository asset_repository
        -GraphEngine graph_engine
        -RAGEngine rag_engine
        -LLMService llm_service
        -CacheService cache
        +analyze_threats(project_id, target_asset_ids) ThreatAnalysisResult
        +get_threat(threat_id) Threat
        +list_threats(project_id, filters) Threat[]
        +update_status(threat_id, status) bool
        +get_attack_paths(project_id, threat_id) AttackPath[]
    }

    class ThreatRepository {
        <<interface>>
        +save(threat) string
        +get_by_id(threat_id) Threat
        +list_by_project(project_id, status) Threat[]
        +update(threat) bool
        +delete(threat_id) bool
    }

    class GraphEngine {
        <<interface>>
        +get_data_flows(project_id) DataFlow[]
        +find_shortest_path(source_id, target_id, max_hops) Path
        +execute_cypher(query, params) list
    }

    class RAGEngine {
        <<interface>>
        +retrieve(query, collections, top_k) RetrievedDocument[]
    }

    class LLMService {
        <<interface>>
        +generate(model, system_prompt, user_prompt, response_format) string
    }

    ThreatService --> ThreatRepository
    ThreatService --> GraphEngine
    ThreatService --> RAGEngine
    ThreatService --> LLMService
```

##### 威胁分析流程

```mermaid
flowchart TB
    subgraph Input["输入"]
        ProjectId["项目ID"]
        TargetAssets["目标资产<br/>(可选)"]
    end

    subgraph AssetRetrieval["资产获取"]
        A["获取项目资产列表"] --> B["获取数据流关系"]
    end

    subgraph STRIDEAnalysis["STRIDE分析"]
        C["遍历数据流"] --> D["RAG检索<br/>相关威胁知识"]
        D --> E["构建STRIDE<br/>分析Prompt"]
        E --> F["调用Qwen-Max<br/>生成威胁"]
        G["遍历接口资产"] --> H["执行规则引擎<br/>检查"]
        H --> I["生成规则<br/>触发的威胁"]
    end

    subgraph PostProcess["后处理"]
        J["合并所有威胁"] --> K["去重/合并<br/>相似威胁"]
        K --> L["计算攻击路径"]
    end

    subgraph Persist["持久化"]
        M["保存威胁到<br/>Neo4j"] --> N["建立威胁-资产<br/>关系"]
    end

    subgraph Output["输出"]
        O["ThreatAnalysisResult<br/>威胁列表 + 统计"]
    end

    Input --> AssetRetrieval
    AssetRetrieval --> C
    AssetRetrieval --> G
    F --> J
    I --> J
    PostProcess --> Persist
    Persist --> Output

    style STRIDEAnalysis fill:#ffebee
    style PostProcess fill:#e8f5e9
```

##### 攻击路径计算流程

```mermaid
sequenceDiagram
    participant TS as ThreatService
    participant GE as GraphEngine
    participant Neo as Neo4j

    TS->>GE: 获取公开接口列表
    GE->>Neo: MATCH (i:Interface {access_level:'public'})
    Neo-->>GE: 入口点列表

    loop 对每个目标资产
        loop 对每个入口点
            TS->>GE: find_shortest_path(entry, target, max_hops=10)
            GE->>Neo: shortestPath查询
            Neo-->>GE: 路径节点和边
            GE-->>TS: Path对象
        end
    end

    TS->>TS: 创建AttackPath实体
    TS->>TS: 计算hop_count和feasibility_factors
```

##### STRIDE规则引擎设计

规则引擎基于预定义规则自动检测资产和数据流中的潜在威胁。

```mermaid
flowchart LR
    subgraph Input["输入"]
        Asset["资产/数据流"]
    end

    subgraph RuleEngine["规则引擎"]
        Rules["规则集合"]
        Evaluator["规则评估器"]
    end

    subgraph Evaluation["规则评估"]
        C1{"条件1<br/>匹配?"}
        C2{"条件2<br/>匹配?"}
        C3{"条件N<br/>匹配?"}
    end

    subgraph Output["输出"]
        ThreatList["威胁列表"]
    end

    Asset --> Evaluator
    Evaluator --> Rules
    Rules --> C1 & C2 & C3
    C1 -->|是| ThreatList
    C2 -->|是| ThreatList
    C3 -->|是| ThreatList

    style RuleEngine fill:#fff3e0
```

**内置STRIDE规则表**

| 规则ID | STRIDE类别 | 规则名称 | 触发条件 | 威胁模板 |
|-------|-----------|---------|---------|---------|
| S-001 | Spoofing | no_authentication | 公开接口 + 无认证机制 | 攻击者可能伪造{source}的身份，通过{interface}发送恶意指令 |
| S-002 | Spoofing | weak_mac | CAN/LIN总线 + 无SecOC | 攻击者可能在{bus}总线上伪造{source}发送的消息 |
| T-001 | Tampering | unprotected_storage | 敏感数据 + 未加密存储 | 攻击者可能篡改存储在{location}中的{data_name} |
| T-002 | Tampering | no_integrity_check | 数据流 + 无完整性校验 | 传输中的{data_type}可能被篡改 |
| I-001 | Info Disclosure | plaintext_transmission | 敏感数据 + 明文传输 | 敏感数据{data_type}在{source}到{target}传输过程中可能被窃取 |
| I-002 | Info Disclosure | debug_log_exposure | 调试日志 + 包含敏感信息 | 调试日志可能泄露{sensitive_data} |
| D-001 | DoS | no_rate_limiting | 公开接口 + 无限流 | 攻击者可能通过{interface}发送大量请求导致{target}服务不可用 |
| D-002 | DoS | resource_exhaustion | 无资源限制 + 用户可控输入 | 攻击者可能耗尽{resource}导致系统不可用 |
| E-001 | Elevation | debug_port_exposed | 调试端口(JTAG/UART/SWD) + 非restricted | 攻击者可能通过暴露的{protocol}调试接口获取系统最高权限 |
| E-002 | Elevation | privilege_boundary_bypass | 跨信任边界 + 无授权检查 | 攻击者可能绕过{boundary}访问高权限功能 |

##### Prompt模板设计

威胁分析使用结构化Prompt引导LLM生成符合规范的威胁场景。

**System Prompt**

> 你是一名资深汽车网络安全专家，精通ISO/SAE 21434标准和STRIDE威胁建模方法。
> 你的任务是识别汽车系统中的潜在网络安全威胁。
> 请基于提供的资产信息和上下文知识，生成准确、具体的威胁场景。
> 威胁描述应包含攻击者的具体行为、利用的漏洞或弱点、以及可能造成的影响。

**User Prompt结构**

| 段落 | 内容 | 说明 |
|-----|------|------|
| **分析目标** | 数据流名称、源、目标、协议、数据类型、描述 | 提供分析上下文 |
| **参考知识** | RAG检索返回的相关文档 | CVE、ATT&CK、历史案例 |
| **任务说明** | 基于STRIDE模型分析潜在威胁 | 明确任务要求 |
| **输出格式** | JSON数组，包含stride_category、description、attack_vector、preconditions、impact、confidence | 结构化输出便于解析 |

### 4.4 风险评估模块

#### 4.4.1 风险计算公式

$$
\text{Risk Level} = f(\text{Impact Rating}, \text{Attack Feasibility})
$$

#### 4.4.2 影响评级维度 (SFOP)

```mermaid
flowchart TB
    subgraph SFOP["影响评估维度"]
        Safety["**Safety (安全)**<br/>对人身安全的影响"]
        Financial["**Financial (财务)**<br/>经济损失"]
        Operational["**Operational (操作)**<br/>功能可用性影响"]
        Privacy["**Privacy (隐私)**<br/>个人信息泄露"]
    end

    subgraph Levels["影响等级"]
        Severe["Severe (严重)"]
        Major["Major (重大)"]
        Moderate["Moderate (中等)"]
        Negligible["Negligible (可忽略)"]
    end

    Safety --> Severe
    Financial --> Major
    Operational --> Moderate
    Privacy --> Negligible

    style SFOP fill:#fff3e0
    style Levels fill:#e8f5e9
```

#### 4.4.3 攻击可行性评估

| 评估维度 | 说明 | 评分范围 |
|---------|------|---------|
| **Elapsed Time** | 攻击所需时间 | ≤1天/≤1周/≤1月/>1月 |
| **Specialist Expertise** | 所需专业知识 | 外行/熟练/专家/多专家 |
| **Knowledge of Item** | 对目标了解程度 | 公开/受限/敏感/关键 |
| **Window of Opportunity** | 攻击窗口 | 无限/容易/中等/困难 |
| **Equipment** | 所需设备 | 标准/专业/定制/多定制 |

#### 4.4.4 风险矩阵

```mermaid
block-beta
    columns 5
    space:1 VL["Very Low"] L["Low"] M["Medium"] H["High"]
    S["Severe"]:1 S_VL["2"]:1 S_L["3"]:1 S_M["4"]:1 S_H["5 Critical"]:1
    Ma["Major"]:1 Ma_VL["1"]:1 Ma_L["2"]:1 Ma_M["3"]:1 Ma_H["4 High"]:1
    Mo["Moderate"]:1 Mo_VL["1"]:1 Mo_L["1"]:1 Mo_M["2"]:1 Mo_H["3 Medium"]:1
    N["Negligible"]:1 N_VL["1"]:1 N_L["1"]:1 N_M["1"]:1 N_H["1 Low"]:1

    style S_H fill:#d32f2f,color:#fff
    style S_M fill:#f57c00,color:#fff
    style Ma_H fill:#f57c00,color:#fff
    style S_L fill:#fbc02d
    style Ma_M fill:#fbc02d
    style Mo_H fill:#fbc02d
    style S_VL fill:#4caf50,color:#fff
    style Ma_L fill:#4caf50,color:#fff
    style Ma_VL fill:#4caf50,color:#fff
    style Mo_M fill:#4caf50,color:#fff
    style Mo_L fill:#4caf50,color:#fff
    style Mo_VL fill:#4caf50,color:#fff
    style N_H fill:#4caf50,color:#fff
    style N_M fill:#4caf50,color:#fff
    style N_L fill:#4caf50,color:#fff
    style N_VL fill:#4caf50,color:#fff
```

| 攻击可行性 \ 影响等级 | **Severe** | **Major** | **Moderate** | **Negligible** |
|---------------------|-----------|----------|-------------|---------------|
| **High** | 5 (Critical) | 4 (High) | 3 (Medium) | 1 (Low) |
| **Medium** | 4 (High) | 3 (Medium) | 2 (Low) | 1 (Low) |
| **Low** | 3 (Medium) | 2 (Low) | 1 (Low) | 1 (Low) |
| **Very Low** | 2 (Low) | 1 (Low) | 1 (Low) | 1 (Low) |

#### 4.4.5 详细设计

##### 领域模型

风险评估域包含影响评估、可行性评估和风险实体三个核心概念。

```mermaid
classDiagram
    class Risk {
        +string id
        +string threat_id
        +string project_id
        +ImpactAssessment impact
        +FeasibilityAssessment feasibility
        +RiskLevel risk_level
        +int risk_score
        +RiskTreatment treatment
        +string treatment_rationale
        +RiskLevel residual_risk_level
        +string assessed_by
        +datetime assessed_at
        +bool reviewed
        +string reviewed_by
        +datetime reviewed_at
    }

    class ImpactAssessment {
        +ImpactLevel safety
        +ImpactLevel financial
        +ImpactLevel operational
        +ImpactLevel privacy
        +string safety_rationale
        +string financial_rationale
        +string operational_rationale
        +string privacy_rationale
        +overall_impact() ImpactLevel
    }

    class FeasibilityAssessment {
        +int elapsed_time
        +int specialist_expertise
        +int knowledge_of_item
        +int window_of_opportunity
        +int equipment
        +string elapsed_time_rationale
        +string expertise_rationale
        +string knowledge_rationale
        +string window_rationale
        +string equipment_rationale
        +total_score() int
        +feasibility_level() FeasibilityLevel
    }

    Risk --> ImpactAssessment
    Risk --> FeasibilityAssessment
```

**风险相关枚举定义**

| 枚举类型 | 枚举值 | 说明 |
|---------|-------|------|
| **ImpactLevel** | `severe` | 严重 - 可能导致人身伤害 |
| | `major` | 重大 - 重大财务损失 |
| | `moderate` | 中等 - 功能降级 |
| | `negligible` | 可忽略 - 轻微影响 |
| **FeasibilityLevel** | `high` | 攻击容易实施 (总分 ≤4) |
| | `medium` | 需要一定技能和资源 (总分 5-9) |
| | `low` | 需要专业技能和特殊设备 (总分 10-14) |
| | `very_low` | 几乎不可能实施 (总分 ≥15) |
| **RiskLevel** | `critical` | 风险等级5 - 必须立即处理 |
| | `high` | 风险等级4 - 优先处理 |
| | `medium` | 风险等级3 - 计划处理 |
| | `low` | 风险等级2 - 监控 |
| | `negligible` | 风险等级1 - 可接受 |
| **RiskTreatment** | `avoid` | 规避风险 - 消除威胁源 |
| | `reduce` | 降低风险 - 实施缓解措施 |
| | `share` | 转移风险 - 保险/外包 |
| | `retain` | 接受风险 - 监控但不处理 |

##### 风险计算逻辑

风险计算基于ISO 21434标准的风险矩阵，综合影响等级和攻击可行性确定最终风险等级。

```mermaid
flowchart TB
    subgraph ImpactCalc["影响等级计算"]
        S["Safety评估"] --> Max["取最高等级"]
        F["Financial评估"] --> Max
        O["Operational评估"] --> Max
        P["Privacy评估"] --> Max
        Max --> ImpactLevel["Overall Impact"]
    end

    subgraph FeasibilityCalc["可行性等级计算"]
        ET["Elapsed Time<br/>(0-3)"] --> Sum["求和"]
        SE["Specialist Expertise<br/>(0-3)"] --> Sum
        KI["Knowledge of Item<br/>(0-3)"] --> Sum
        WO["Window of Opportunity<br/>(0-3)"] --> Sum
        EQ["Equipment<br/>(0-3)"] --> Sum
        Sum --> Score["Total Score<br/>(0-15)"]
        Score --> FeasLevel{"分级判断"}
        FeasLevel -->|"≤4"| High["High"]
        FeasLevel -->|"5-9"| Medium["Medium"]
        FeasLevel -->|"10-14"| Low["Low"]
        FeasLevel -->|"≥15"| VeryLow["Very Low"]
    end

    subgraph RiskCalc["风险等级计算"]
        ImpactLevel --> Matrix["风险矩阵<br/>查表"]
        High & Medium & Low & VeryLow --> Matrix
        Matrix --> RiskLevel["Risk Level<br/>+ Score"]
    end

    style ImpactCalc fill:#fff3e0
    style FeasibilityCalc fill:#e3f2fd
    style RiskCalc fill:#e8f5e9
```

**攻击可行性评分标准**

| 维度 | 0分 | 1分 | 2分 | 3分 |
|-----|-----|-----|-----|-----|
| **Elapsed Time** | ≤1天 | ≤1周 | ≤1月 | >1月 |
| **Specialist Expertise** | 外行即可 | 熟练工程师 | 专家 | 多领域专家 |
| **Knowledge of Item** | 公开信息 | 受限信息 | 敏感信息 | 关键内部信息 |
| **Window of Opportunity** | 无限制 | 容易获得 | 中等难度 | 困难 |
| **Equipment** | 标准设备 | 专业设备 | 定制设备 | 多种定制设备 |

**风险处置策略建议**

| 风险等级 | 建议策略 | 行动要求 |
|---------|---------|---------|
| Critical (5) | Avoid | 必须消除威胁源或重新设计 |
| High (4) | Reduce | 优先实施缓解措施 |
| Medium (3) | Reduce | 计划实施缓解措施 |
| Low (2) | Retain | 持续监控，可选缓解 |
| Negligible (1) | Retain | 接受风险，定期复审 |

##### 服务层设计

```mermaid
classDiagram
    class RiskService {
        -RiskRepository risk_repository
        -ThreatRepository threat_repository
        -RiskCalculator risk_calculator
        -LLMService llm_service
        -RAGEngine rag_engine
        -CacheService cache
        +evaluate_risks(project_id, threat_ids) RiskEvaluationResult
        +get_risk(risk_id) Risk
        +list_risks(project_id, risk_level) Risk[]
        +update_risk(risk_id, updates) bool
        +get_risk_matrix(project_id) RiskMatrix
    }

    class RiskCalculator {
        +RISK_MATRIX dict
        +calculate(impact, feasibility) tuple
        +suggest_treatment(risk_level) RiskTreatment
    }

    class RiskRepository {
        <<interface>>
        +save(risk) string
        +get_by_id(risk_id) Risk
        +list_by_project(project_id) Risk[]
        +update(risk) bool
    }

    RiskService --> RiskRepository
    RiskService --> RiskCalculator
    RiskService --> LLMService
    RiskService --> RAGEngine
```

##### 风险评估流程

```mermaid
flowchart TB
    subgraph Input["输入"]
        ProjectId["项目ID"]
        ThreatIds["威胁ID列表<br/>(可选)"]
    end

    subgraph ThreatRetrieval["威胁获取"]
        A["获取待评估威胁"] --> B{"指定威胁ID?"}
        B -->|是| C["按ID查询威胁"]
        B -->|否| D["查询CONFIRMED<br/>状态威胁"]
    end

    subgraph Assessment["逐个评估"]
        E["遍历威胁列表"]
        E --> F["AI辅助<br/>影响评估"]
        F --> G["AI辅助<br/>可行性评估"]
        G --> H["风险矩阵<br/>计算等级"]
        H --> I["建议处置策略"]
    end

    subgraph Persist["持久化"]
        I --> J["创建Risk实体"]
        J --> K["保存到数据库"]
    end

    subgraph Statistics["统计汇总"]
        K --> L["计算风险统计"]
        L --> M["生成风险分布"]
    end

    subgraph Output["输出"]
        M --> N["RiskEvaluationResult<br/>风险列表 + 统计"]
    end

    Input --> ThreatRetrieval
    ThreatRetrieval --> Assessment
    Assessment --> Persist
    Persist --> Statistics
    Statistics --> Output

    style Assessment fill:#fff3e0
    style Persist fill:#e8f5e9
```

##### AI辅助评估流程

```mermaid
sequenceDiagram
    participant RS as RiskService
    participant RAG as RAGEngine
    participant LLM as Qwen-Max
    participant RC as RiskCalculator

    Note over RS: 影响评估阶段
    RS->>RAG: 检索威胁影响案例
    RAG-->>RS: 返回相关文档
    RS->>LLM: 发送影响评估Prompt
    Note over LLM: 评估SFOP四维度<br/>返回等级+理由
    LLM-->>RS: JSON响应
    RS->>RS: 解析为ImpactAssessment

    Note over RS: 可行性评估阶段
    RS->>LLM: 发送可行性评估Prompt
    Note over LLM: 评估五个维度<br/>返回评分+理由
    LLM-->>RS: JSON响应
    RS->>RS: 解析为FeasibilityAssessment

    Note over RS: 风险计算阶段
    RS->>RC: calculate(impact, feasibility)
    RC-->>RS: (RiskLevel, Score)
    RS->>RC: suggest_treatment(risk_level)
    RC-->>RS: RiskTreatment
```

##### Prompt模板设计

**影响评估Prompt结构**

| 段落 | 内容 | 说明 |
|-----|------|------|
| **威胁信息** | 描述、STRIDE类别、攻击向量、目标资产 | 提供评估上下文 |
| **参考知识** | RAG检索返回的相关文档 | 历史案例、标准条款 |
| **任务说明** | 评估SFOP四维度影响等级 | 明确任务要求 |
| **输出格式** | JSON，包含各维度level和rationale | 结构化输出便于解析 |

**可行性评估Prompt结构**

| 段落 | 内容 | 说明 |
|-----|------|------|
| **威胁信息** | 描述、攻击向量、攻击路径跳数 | 提供评估上下文 |
| **评分标准** | 五个维度的0-3分评分说明 | 确保评分一致性 |
| **任务说明** | 对各维度打分并说明理由 | 明确任务要求 |
| **输出格式** | JSON，包含各维度score和rationale | 结构化输出便于解析 |

### 4.5 报告生成模块

```mermaid
flowchart LR
    subgraph DataSources["数据源"]
        Assets["资产数据"]
        Threats["威胁数据"]
        Risks["风险数据"]
        Paths["攻击路径"]
    end

    subgraph Templates["报告模板"]
        ISO21434["ISO 21434模板"]
        UNR155["UN R155模板"]
        Custom["自定义模板"]
    end

    subgraph Generator["报告生成器"]
        Aggregator["数据聚合"]
        Renderer["渲染引擎"]
        Exporter["导出器"]
    end

    subgraph Outputs["输出格式"]
        PDF["PDF报告"]
        Word["Word文档"]
        Excel["Excel表格"]
        JSON["JSON数据"]
    end

    DataSources --> Aggregator
    Templates --> Renderer
    Aggregator --> Renderer
    Renderer --> Exporter
    Exporter --> Outputs

    style Generator fill:#e8f5e9
```

#### 4.5.2 详细设计

##### 领域模型

报告域包含报告配置、报告实体和报告章节三个核心概念。

```mermaid
classDiagram
    class Report {
        +string id
        +string project_id
        +ReportConfig config
        +ReportStatus status
        +string file_path
        +int file_size
        +int page_count
        +string generated_by
        +datetime generated_at
        +string error_message
        +datetime created_at
    }

    class ReportConfig {
        +ReportType report_type
        +ReportFormat output_format
        +string[] include_sections
        +string language
        +bool include_charts
        +bool include_raw_data
    }

    class ReportSection {
        +string id
        +string title
        +string content
        +int order
        +ReportSection[] subsections
        +dict[] charts
        +dict[] tables
    }

    Report --> ReportConfig
    Report --> "*" ReportSection
    ReportSection --> "*" ReportSection : subsections
```

**报告相关枚举定义**

| 枚举类型 | 枚举值 | 说明 |
|---------|-------|------|
| **ReportType** | `iso21434_tara` | ISO 21434标准TARA报告 |
| | `unr155` | UN R155合规报告 |
| | `executive` | 管理层摘要报告 |
| | `technical` | 技术详细报告 |
| | `custom` | 自定义报告 |
| **ReportFormat** | `pdf` | PDF格式 |
| | `docx` | Word文档 |
| | `xlsx` | Excel表格 |
| | `html` | HTML网页 |
| | `json` | JSON数据 |
| **ReportStatus** | `pending` | 等待生成 |
| | `generating` | 生成中 |
| | `completed` | 已完成 |
| | `failed` | 生成失败 |

**默认报告章节**

| 章节ID | 章节标题(中文) | 章节标题(英文) | 说明 |
|-------|--------------|---------------|------|
| `executive_summary` | 管理层摘要 | Executive Summary | 关键发现和风险概览 |
| `scope` | 分析范围 | Scope | Item定义和系统边界 |
| `asset_inventory` | 资产清单 | Asset Inventory | 硬件/软件/数据/接口资产 |
| `threat_analysis` | 威胁分析 | Threat Analysis | 威胁场景列表 |
| `risk_assessment` | 风险评估 | Risk Assessment | 风险矩阵和详细评估 |
| `attack_paths` | 攻击路径分析 | Attack Path Analysis | 攻击路径可视化 |
| `recommendations` | 建议与缓解措施 | Recommendations | 安全建议和措施 |
| `appendix` | 附录 | Appendix | 术语、参考标准、原始数据 |

##### 服务层设计

```mermaid
classDiagram
    class ReportService {
        -ReportRepository report_repository
        -ProjectRepository project_repository
        -AssetRepository asset_repository
        -ThreatRepository threat_repository
        -RiskRepository risk_repository
        -FileStorage file_storage
        -TemplateEngine template_engine
        -PDFRenderer pdf_renderer
        -TaskQueue task_queue
        +generate_report(project_id, config) Report
        +get_report(report_id) Report
        +list_reports(project_id) Report[]
        +get_report_file(file_path) bytes
    }

    class TemplateEngine {
        <<interface>>
        +render(template_name, data) string
        +render_section(section_id, data) string
    }

    class PDFRenderer {
        <<interface>>
        +render_html_to_pdf(html) bytes
        +render_markdown_to_pdf(markdown) bytes
    }

    class TaskQueue {
        <<interface>>
        +enqueue(task_type, payload) string
        +get_status(task_id) TaskStatus
    }

    ReportService --> ReportRepository
    ReportService --> TemplateEngine
    ReportService --> PDFRenderer
    ReportService --> TaskQueue
```

##### 报告生成流程

```mermaid
flowchart TB
    subgraph Request["请求阶段"]
        A["接收生成请求"] --> B["创建Report实体<br/>status=PENDING"]
        B --> C["保存到数据库"]
        C --> D["提交异步任务"]
        D --> E["返回report_id"]
    end

    subgraph AsyncGeneration["异步生成"]
        F["任务队列消费"] --> G["更新status=GENERATING"]
        G --> H["收集报告数据"]
        H --> I["选择报告模板"]
        I --> J["渲染各章节"]
        J --> K{"包含图表?"}
        K -->|是| L["生成图表"]
        L --> M["注入图表"]
        K -->|否| M
        M --> N["导出文档"]
    end

    subgraph Export["导出阶段"]
        N --> O{"输出格式"}
        O -->|PDF| P["PDFRenderer"]
        O -->|DOCX| Q["python-docx"]
        O -->|XLSX| R["openpyxl"]
        O -->|HTML| S["Jinja2"]
        O -->|JSON| T["json.dumps"]
        P & Q & R & S & T --> U["保存到MinIO"]
    end

    subgraph Complete["完成阶段"]
        U --> V["更新status=COMPLETED"]
        V --> W["记录file_path/size"]
    end

    subgraph Error["错误处理"]
        X["捕获异常"] --> Y["更新status=FAILED"]
        Y --> Z["记录error_message"]
    end

    E -.->|异步| F
    AsyncGeneration -->|成功| Complete
    AsyncGeneration -->|失败| Error

    style Request fill:#e3f2fd
    style AsyncGeneration fill:#fff3e0
    style Export fill:#e8f5e9
    style Error fill:#ffebee
```

##### 数据收集流程

```mermaid
flowchart LR
    subgraph DataSources["数据源查询"]
        A["ProjectRepository<br/>项目信息"]
        B["AssetRepository<br/>资产列表"]
        C["ThreatRepository<br/>威胁列表"]
        D["RiskRepository<br/>风险列表"]
    end

    subgraph Statistics["统计计算"]
        E["风险统计<br/>按等级分组"]
        F["威胁统计<br/>按STRIDE分组"]
        G["资产统计<br/>按类型分组"]
    end

    subgraph Output["输出"]
        H["ReportData<br/>聚合数据对象"]
    end

    A --> H
    B --> H
    C --> H
    D --> H
    B --> G --> H
    C --> F --> H
    D --> E --> H

    style DataSources fill:#e3f2fd
    style Statistics fill:#fff3e0
```

##### 图表生成配置

| 图表ID | 图表类型 | 标题 | 数据来源 |
|-------|---------|-----|---------|
| `risk_distribution` | 饼图 (Pie) | 风险等级分布 | Risk.risk_level分组计数 |
| `stride_distribution` | 柱状图 (Bar) | STRIDE威胁分布 | Threat.stride_category分组计数 |
| `asset_distribution` | 饼图 (Pie) | 资产类型分布 | Asset.asset_type分组计数 |
| `risk_matrix_heatmap` | 热力图 (Heatmap) | 风险矩阵热力图 | Impact × Feasibility矩阵 |
| `attack_path_graph` | 网络图 (Graph) | 攻击路径图 | AttackPath节点和边 |

##### 模板系统设计

报告采用Jinja2模板引擎，支持多种报告类型的定制化输出。

```mermaid
flowchart TB
    subgraph Templates["模板层次"]
        Base["base_template.html<br/>基础布局"]
        ISO["iso21434_template.html<br/>ISO 21434模板"]
        UNR["unr155_template.html<br/>UN R155模板"]
        Exec["executive_template.html<br/>管理层摘要"]
        Tech["technical_template.html<br/>技术报告"]
    end

    subgraph Partials["章节片段"]
        Summary["_summary.html"]
        Assets["_assets.html"]
        Threats["_threats.html"]
        Risks["_risks.html"]
        Paths["_attack_paths.html"]
        Recs["_recommendations.html"]
    end

    subgraph Macros["宏定义"]
        Tables["table_macros.html<br/>表格渲染"]
        Charts["chart_macros.html<br/>图表渲染"]
        Styles["style_macros.html<br/>样式定义"]
    end

    Base --> ISO & UNR & Exec & Tech
    ISO & UNR & Exec & Tech --> Partials
    Partials --> Macros

    style Templates fill:#e8f5e9
    style Partials fill:#e3f2fd
    style Macros fill:#fff3e0
```

**ISO 21434 TARA报告模板结构**

| 章节 | 内容 | 模板变量 |
|-----|------|---------|
| **封面** | 项目名称、编号、版本、日期 | `project.name`, `project.id`, `project.version`, `report_date` |
| **1. 管理层摘要** | 关键发现、风险概览 | `executive_summary`, `threat_statistics.total`, `risk_statistics` |
| **2. 分析范围** | Item定义、系统边界 | `item_definition`, `system_boundary` |
| **3. 资产清单** | 分类资产表格 | `hardware_assets_table`, `software_assets_table`, etc. |
| **4. 威胁分析** | 威胁场景、攻击路径 | `threats_table`, `attack_paths` |
| **5. 风险评估** | 风险矩阵、详细评估 | `risk_matrix`, `detailed_risks_table` |
| **6. 建议** | 缓解措施 | `recommendations` |
| **附录** | 术语、参考标准 | `glossary`, `references` |

---

## 5. 数据模型设计

### 5.1 知识图谱本体设计

基于UCO (Unified Cybersecurity Ontology) 构建汽车安全本体。

```mermaid
erDiagram
    Project ||--o{ Item : contains
    Item ||--o{ Function : provides
    Item ||--o{ Component : includes
    Component ||--o{ Interface : exposes
    Component ||--|| ComponentType : is_type
    Interface ||--|| InterfaceType : is_type
    Function ||--o{ Data : processes
    Data ||--o{ Component : stored_in
    Component }o--o{ Component : connects_to
    Interface }o--o{ Interface : communicates_with
    TrustBoundary ||--o{ Component : contains

    Threat ||--o{ Asset : targets
    Threat ||--|| ThreatCategory : belongs_to
    Vulnerability ||--o{ Component : affects
    AttackPath ||--o{ Interface : traverses
    Risk ||--|| Threat : evaluates
    Risk ||--|| Impact : has_impact
    Risk ||--|| Feasibility : has_feasibility

    Project {
        string id PK
        string name
        string description
        datetime created_at
        string status
    }

    Item {
        string id PK
        string name
        string item_type
        string description
    }

    Function {
        string id PK
        string name
        string description
        string[] security_properties
    }

    Component {
        string id PK
        string name
        string component_type
        string version
        string vendor
    }

    Interface {
        string id PK
        string name
        string interface_type
        string protocol
        string access_level
    }

    Data {
        string id PK
        string name
        string data_type
        string sensitivity
        string[] cia_requirements
    }

    TrustBoundary {
        string id PK
        string name
        string level
        string description
    }

    Threat {
        string id PK
        string description
        string stride_category
        string attack_vector
    }

    Vulnerability {
        string id PK
        string cve_id
        float cvss_score
        string description
    }

    Risk {
        string id PK
        string impact_level
        string feasibility_level
        int risk_score
    }
```

### 5.2 图数据库节点设计

#### 5.2.1 节点类型定义

| 节点标签 | 说明 | 关键属性 |
|---------|------|---------|
| `:Project` | 分析项目 | id, name, status, created_at |
| `:Item` | 分析对象(如IVI、T-BOX) | id, name, item_type |
| `:Function` | 功能 | id, name, security_properties |
| `:Component` | 组件(软件/硬件) | id, name, type, version, vendor |
| `:Interface` | 接口 | id, name, protocol, access_level |
| `:Data` | 数据资产 | id, name, sensitivity, cia |
| `:TrustBoundary` | 信任边界 | id, name, level |
| `:Threat` | 威胁 | id, description, stride_category |
| `:Vulnerability` | 漏洞 | id, cve_id, cvss_score |
| `:Risk` | 风险评估 | id, impact, feasibility, score |
| `:Mitigation` | 缓解措施 | id, description, effectiveness |

#### 5.2.2 关系类型定义

| 关系类型 | 起点 | 终点 | 说明 |
|---------|------|------|-----|
| `CONTAINS` | Project | Item | 项目包含分析对象 |
| `PROVIDES` | Item | Function | 对象提供功能 |
| `INCLUDES` | Item/Component | Component | 包含组件 |
| `EXPOSES` | Component | Interface | 组件暴露接口 |
| `CONNECTS_TO` | Component | Component | 组件连接 |
| `COMMUNICATES_WITH` | Interface | Interface | 接口通信 |
| `PROCESSES` | Function | Data | 功能处理数据 |
| `STORED_IN` | Data | Component | 数据存储位置 |
| `WITHIN` | Component | TrustBoundary | 组件所属信任域 |
| `TARGETS` | Threat | Asset | 威胁针对资产 |
| `AFFECTS` | Vulnerability | Component | 漏洞影响组件 |
| `MITIGATES` | Mitigation | Threat | 措施缓解威胁 |

### 5.3 图数据库Schema示意

```mermaid
graph TB
    subgraph Structure["系统结构"]
        P[":Project"] --> |CONTAINS| I[":Item"]
        I --> |PROVIDES| F[":Function"]
        I --> |INCLUDES| C1[":Component<br/>(Hardware)"]
        I --> |INCLUDES| C2[":Component<br/>(Software)"]
        C1 --> |EXPOSES| IF1[":Interface<br/>(Physical)"]
        C2 --> |EXPOSES| IF2[":Interface<br/>(Logical)"]
        C1 <--> |CONNECTS_TO| C2
        IF1 <--> |COMMUNICATES_WITH| IF2
        F --> |PROCESSES| D[":Data"]
        D --> |STORED_IN| C1
    end

    subgraph Security["安全分析"]
        TB[":TrustBoundary"] --> |CONTAINS| C1
        TB --> |CONTAINS| C2
        T[":Threat"] --> |TARGETS| D
        T --> |TARGETS| F
        V[":Vulnerability"] --> |AFFECTS| C2
        R[":Risk"] --> |EVALUATES| T
        M[":Mitigation"] --> |MITIGATES| T
    end

    style Structure fill:#e3f2fd
    style Security fill:#ffebee
```

### 5.4 向量数据库Schema

Milvus集合设计用于RAG检索：

| 集合名称 | 向量维度 | 用途 |
|---------|---------|-----|
| `threat_knowledge` | 1536 | 威胁知识库检索 |
| `cve_database` | 1536 | CVE漏洞库检索 |
| `attack_patterns` | 1536 | 攻击模式检索 |
| `iso21434_clauses` | 1536 | 标准条款检索 |
| `unr155_threats` | 1536 | UN R155威胁目录 |

### 5.5 PostgreSQL数据模型

PostgreSQL用于存储业务数据、报告元数据和任务状态。

#### 5.5.1 数据库Schema

```sql
-- 项目表
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    item_name VARCHAR(255),           -- 分析对象名称
    item_type VARCHAR(50),            -- IVI, T-BOX, Gateway等
    version VARCHAR(50),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_projects_status ON projects(status);

-- 文件上传记录
CREATE TABLE uploaded_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT,
    minio_bucket VARCHAR(100) NOT NULL,
    minio_key VARCHAR(500) NOT NULL,
    parse_status VARCHAR(50) DEFAULT 'pending',
    parse_result JSONB,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_files_project ON uploaded_files(project_id);
CREATE INDEX idx_files_status ON uploaded_files(parse_status);

-- 报告表
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    output_format VARCHAR(20) NOT NULL,
    config JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    file_path VARCHAR(500),
    file_size BIGINT,
    page_count INT,
    error_message TEXT,
    generated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reports_project ON reports(project_id);
CREATE INDEX idx_reports_status ON reports(status);

-- 异步任务表
CREATE TABLE async_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    priority INT DEFAULT 0,
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 3,
    result JSONB,
    error_message TEXT,
    scheduled_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_status ON async_tasks(status);
CREATE INDEX idx_tasks_scheduled ON async_tasks(scheduled_at);
CREATE INDEX idx_tasks_type ON async_tasks(task_type);

-- 分析会话表 (用于追踪多步骤分析流程)
CREATE TABLE analysis_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL,  -- asset_parse, threat_analysis, risk_evaluation
    status VARCHAR(50) DEFAULT 'running',
    progress INT DEFAULT 0,             -- 0-100
    current_step VARCHAR(100),
    steps_completed JSONB DEFAULT '[]',
    result_summary JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_sessions_project ON analysis_sessions(project_id);
CREATE INDEX idx_sessions_status ON analysis_sessions(status);
```

#### 5.5.2 数据访问层

```python
# infrastructure/db/postgresql.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

class PostgreSQLDatabase:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        async with self.async_session() as session:
            yield session
```

### 5.6 Redis数据模型

Redis用于缓存、任务队列和会话管理。

#### 5.6.1 缓存策略

| Key Pattern | 数据类型 | TTL | 用途 |
|-------------|---------|-----|------|
| `project:{id}:assets` | Hash | 5min | 项目资产缓存 |
| `project:{id}:asset_graph` | String (JSON) | 5min | 资产图谱缓存 |
| `project:{id}:threats` | Hash | 5min | 威胁列表缓存 |
| `project:{id}:risk_matrix` | String (JSON) | 5min | 风险矩阵缓存 |
| `session:{id}:progress` | String | 1h | 分析进度 |
| `rate_limit:{ip}` | String | 1min | API限流计数 |

#### 5.6.2 任务队列设计

```python
# infrastructure/queue/redis_queue.py
import redis.asyncio as redis
import json
from dataclasses import dataclass

@dataclass
class TaskQueue:
    """基于Redis的任务队列"""
    redis_client: redis.Redis

    # 队列名称
    QUEUES = {
        "high": "task_queue:high",      # 高优先级
        "default": "task_queue:default", # 默认优先级
        "low": "task_queue:low"          # 低优先级
    }

    async def enqueue(
        self,
        task_type: str,
        payload: dict,
        priority: str = "default"
    ) -> str:
        """入队任务"""
        task_id = generate_uuid()
        task = {
            "id": task_id,
            "type": task_type,
            "payload": payload,
            "created_at": datetime.now().isoformat()
        }

        queue_name = self.QUEUES.get(priority, self.QUEUES["default"])
        await self.redis_client.lpush(queue_name, json.dumps(task))

        return task_id

    async def dequeue(self, timeout: int = 30) -> dict | None:
        """出队任务 (阻塞式，优先级顺序)"""
        result = await self.redis_client.brpop(
            [self.QUEUES["high"], self.QUEUES["default"], self.QUEUES["low"]],
            timeout=timeout
        )

        if result:
            _, task_json = result
            return json.loads(task_json)
        return None

    async def get_queue_length(self, priority: str = "default") -> int:
        """获取队列长度"""
        queue_name = self.QUEUES.get(priority, self.QUEUES["default"])
        return await self.redis_client.llen(queue_name)
```

#### 5.6.3 缓存服务

```python
# infrastructure/cache/redis_cache.py
import redis.asyncio as redis
import json
from typing import Any

@dataclass
class CacheService:
    """Redis缓存服务"""
    redis_client: redis.Redis
    default_ttl: int = 300  # 5分钟

    async def get(self, key: str) -> Any | None:
        """获取缓存"""
        value = await self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ) -> bool:
        """设置缓存"""
        ttl = ttl or self.default_ttl
        return await self.redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        return await self.redis_client.delete(key) > 0

    async def delete_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        keys = []
        async for key in self.redis_client.scan_iter(pattern):
            keys.append(key)

        if keys:
            return await self.redis_client.delete(*keys)
        return 0

    async def incr(self, key: str, ttl: int | None = None) -> int:
        """计数器自增"""
        count = await self.redis_client.incr(key)
        if ttl and count == 1:
            await self.redis_client.expire(key, ttl)
        return count
```

### 5.7 MinIO文件存储

MinIO提供S3兼容的对象存储服务。

#### 5.7.1 Bucket设计

| Bucket | 用途 | 保留策略 |
|--------|------|---------|
| `assets` | 上传的原始文件 (BOM, 架构图等) | 项目生命周期 |
| `reports` | 生成的报告文件 | 永久保留 |
| `temp` | 临时文件 (处理中间产物) | 24小时自动清理 |
| `exports` | 导出数据 | 7天自动清理 |

#### 5.7.2 文件存储服务

```python
# infrastructure/storage/minio_storage.py
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from dataclasses import dataclass

@dataclass
class MinIOStorage:
    """MinIO文件存储服务"""
    client: Minio

    async def save(
        self,
        bucket: str,
        key: str,
        content: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """保存文件"""
        # 确保bucket存在
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

        # 上传文件
        self.client.put_object(
            bucket,
            key,
            BytesIO(content),
            len(content),
            content_type=content_type
        )

        return f"{bucket}/{key}"

    async def get(self, bucket: str, key: str) -> bytes:
        """获取文件"""
        try:
            response = self.client.get_object(bucket, key)
            return response.read()
        finally:
            response.close()
            response.release_conn()

    async def delete(self, bucket: str, key: str) -> bool:
        """删除文件"""
        try:
            self.client.remove_object(bucket, key)
            return True
        except S3Error:
            return False

    async def get_presigned_url(
        self,
        bucket: str,
        key: str,
        expires: int = 3600
    ) -> str:
        """获取预签名URL (用于下载)"""
        from datetime import timedelta
        return self.client.presigned_get_object(
            bucket,
            key,
            expires=timedelta(seconds=expires)
        )

    async def list_objects(
        self,
        bucket: str,
        prefix: str = ""
    ) -> list[dict]:
        """列出对象"""
        objects = self.client.list_objects(bucket, prefix=prefix)
        return [
            {
                "key": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified
            }
            for obj in objects
        ]
```

#### 5.7.3 文件命名规范

```
assets/
├── {project_id}/
│   ├── bom/
│   │   └── {file_id}_{original_name}.xlsx
│   ├── architecture/
│   │   └── {file_id}_{original_name}.png
│   └── specs/
│       └── {file_id}_{original_name}.pdf

reports/
├── {project_id}/
│   └── {report_id}_{report_type}_{timestamp}.{format}

temp/
└── {task_id}/
    └── {step}_{timestamp}.json

exports/
└── {project_id}/
    └── {export_id}_{export_type}_{timestamp}.zip
```

---

## 6. API接口设计

### 6.1 API设计原则

- 遵循RESTful设计规范
- 使用OpenAPI 3.1规范描述
- 版本化API (v1)
- 统一的错误响应格式

### 6.2 核心API端点

```mermaid
flowchart TB
    subgraph ProjectAPI["项目管理 /api/v1/projects"]
        POST_Project["POST / - 创建项目"]
        GET_Projects["GET / - 项目列表"]
        GET_Project["GET /{id} - 项目详情"]
        PUT_Project["PUT /{id} - 更新项目"]
        DELETE_Project["DELETE /{id} - 删除项目"]
    end

    subgraph AssetAPI["资产管理 /api/v1/assets"]
        POST_Upload["POST /upload - 上传资料"]
        POST_Parse["POST /parse - 解析文件"]
        GET_Assets["GET / - 资产列表"]
        GET_Asset["GET /{id} - 资产详情"]
        GET_Graph["GET /graph - 资产图谱"]
    end

    subgraph ThreatAPI["威胁分析 /api/v1/threats"]
        POST_Analyze["POST /analyze - 启动分析"]
        GET_Threats["GET / - 威胁列表"]
        GET_Threat["GET /{id} - 威胁详情"]
        GET_Paths["GET /paths - 攻击路径"]
    end

    subgraph RiskAPI["风险评估 /api/v1/risks"]
        POST_Evaluate["POST /evaluate - 风险评估"]
        GET_Risks["GET / - 风险列表"]
        GET_Matrix["GET /matrix - 风险矩阵"]
        PUT_Risk["PUT /{id} - 更新评级"]
    end

    subgraph ReportAPI["报告生成 /api/v1/reports"]
        POST_Generate["POST /generate - 生成报告"]
        GET_Reports["GET / - 报告列表"]
        GET_Download["GET /{id}/download - 下载"]
    end

    style ProjectAPI fill:#e3f2fd
    style AssetAPI fill:#e8f5e9
    style ThreatAPI fill:#fff3e0
    style RiskAPI fill:#fce4ec
    style ReportAPI fill:#f3e5f5
```

### 6.3 详细API定义

#### 6.3.1 项目管理API

```yaml
# OpenAPI 3.1 规范
openapi: 3.1.0
info:
  title: AI TARA Platform API
  version: 1.0.0

paths:
  /api/v1/projects:
    get:
      summary: 获取项目列表
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [draft, analyzing, completed, archived]
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProjectListResponse'

    post:
      summary: 创建项目
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProjectCreateRequest'
      responses:
        '201':
          description: 创建成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProjectResponse'

  /api/v1/projects/{id}:
    get:
      summary: 获取项目详情
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProjectResponse'
        '404':
          description: 项目不存在

    put:
      summary: 更新项目
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProjectUpdateRequest'
      responses:
        '200':
          description: 更新成功

    delete:
      summary: 删除项目
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '204':
          description: 删除成功

components:
  schemas:
    ProjectCreateRequest:
      type: object
      required:
        - name
        - item_name
        - item_type
      properties:
        name:
          type: string
          maxLength: 255
        description:
          type: string
        item_name:
          type: string
          description: 分析对象名称
        item_type:
          type: string
          enum: [IVI, T-BOX, Gateway, BCM, ADAS, Other]

    ProjectResponse:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        description:
          type: string
        item_name:
          type: string
        item_type:
          type: string
        status:
          type: string
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time
```

#### 6.3.2 资产管理API

```python
# api/v1/assets.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])

class AssetResponse(BaseModel):
    id: str
    name: str
    asset_type: str
    description: str | None
    security_properties: list[str]
    metadata: dict
    created_at: datetime

    model_config = {"from_attributes": True}

class AssetGraphResponse(BaseModel):
    nodes: list[dict]
    edges: list[dict]
    trust_boundaries: list[dict]

class ParseRequest(BaseModel):
    file_id: str
    parse_options: dict = Field(default_factory=dict)

class ParseResponse(BaseModel):
    task_id: str
    status: str
    message: str

@router.post("/upload")
async def upload_file(
    project_id: str,
    file: UploadFile = File(...),
    service: AssetService = Depends(get_asset_service)
) -> dict:
    """上传资产文件"""
    if file.size > 50 * 1024 * 1024:  # 50MB限制
        raise HTTPException(400, "File too large")

    allowed_types = ["xlsx", "xls", "png", "jpg", "jpeg", "vsdx", "pdf", "xml"]
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_types:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    content = await file.read()
    result = await service.upload_file(
        project_id=project_id,
        file_name=file.filename,
        file_content=content,
        file_type=ext
    )

    return {
        "file_id": result.file_id,
        "file_name": file.filename,
        "file_size": len(content),
        "status": "uploaded"
    }

@router.post("/parse")
async def parse_file(
    request: ParseRequest,
    service: AssetService = Depends(get_asset_service)
) -> ParseResponse:
    """解析已上传的文件"""
    task_id = await service.start_parse_task(
        file_id=request.file_id,
        options=request.parse_options
    )

    return ParseResponse(
        task_id=task_id,
        status="processing",
        message="Parse task started"
    )

@router.get("/")
async def list_assets(
    project_id: str,
    asset_type: str | None = None,
    page: int = 1,
    page_size: int = 50,
    service: AssetService = Depends(get_asset_service)
) -> dict:
    """获取项目资产列表"""
    assets, total = await service.list_assets(
        project_id=project_id,
        asset_type=asset_type,
        skip=(page - 1) * page_size,
        limit=page_size
    )

    return {
        "items": [AssetResponse.model_validate(a) for a in assets],
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/graph")
async def get_asset_graph(
    project_id: str,
    service: AssetService = Depends(get_asset_service)
) -> AssetGraphResponse:
    """获取资产图谱"""
    graph = await service.get_asset_graph(project_id)
    return AssetGraphResponse(
        nodes=graph.nodes,
        edges=graph.edges,
        trust_boundaries=graph.trust_boundaries
    )

@router.get("/{asset_id}")
async def get_asset(
    asset_id: str,
    service: AssetService = Depends(get_asset_service)
) -> AssetResponse:
    """获取资产详情"""
    asset = await service.get_asset(asset_id)
    if not asset:
        raise HTTPException(404, "Asset not found")
    return AssetResponse.model_validate(asset)
```

#### 6.3.3 威胁分析API

```python
# api/v1/threats.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/threats", tags=["threats"])

class ThreatAnalyzeRequest(BaseModel):
    project_id: str
    target_asset_ids: list[str] | None = None
    analysis_options: dict = Field(default_factory=dict)

class ThreatResponse(BaseModel):
    id: str
    project_id: str
    description: str
    stride_category: str
    attack_vector: str
    status: str
    target_assets: list[str]
    related_cve_ids: list[str]
    confidence_score: float
    created_at: datetime

class AttackPathResponse(BaseModel):
    id: str
    threat_id: str
    entry_point: str
    target: str
    path_nodes: list[str]
    path_edges: list[dict]
    hop_count: int

class AnalysisStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    current_step: str | None
    result: dict | None

@router.post("/analyze")
async def start_threat_analysis(
    request: ThreatAnalyzeRequest,
    background_tasks: BackgroundTasks,
    service: ThreatService = Depends(get_threat_service)
) -> dict:
    """启动威胁分析"""
    task_id = await service.start_analysis(
        project_id=request.project_id,
        target_asset_ids=request.target_asset_ids,
        options=request.analysis_options
    )

    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Threat analysis started"
    }

@router.get("/analysis/{task_id}/status")
async def get_analysis_status(
    task_id: str,
    service: ThreatService = Depends(get_threat_service)
) -> AnalysisStatusResponse:
    """获取分析任务状态"""
    status = await service.get_analysis_status(task_id)
    return AnalysisStatusResponse(**status)

@router.get("/")
async def list_threats(
    project_id: str,
    stride_category: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
    service: ThreatService = Depends(get_threat_service)
) -> dict:
    """获取威胁列表"""
    threats, total = await service.list_threats(
        project_id=project_id,
        stride_category=stride_category,
        status=status,
        skip=(page - 1) * page_size,
        limit=page_size
    )

    return {
        "items": [ThreatResponse.model_validate(t) for t in threats],
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{threat_id}")
async def get_threat(
    threat_id: str,
    service: ThreatService = Depends(get_threat_service)
) -> ThreatResponse:
    """获取威胁详情"""
    threat = await service.get_threat(threat_id)
    if not threat:
        raise HTTPException(404, "Threat not found")
    return ThreatResponse.model_validate(threat)

@router.put("/{threat_id}/status")
async def update_threat_status(
    threat_id: str,
    status: str,
    service: ThreatService = Depends(get_threat_service)
) -> dict:
    """更新威胁状态"""
    await service.update_status(threat_id, status)
    return {"message": "Status updated"}

@router.get("/paths")
async def get_attack_paths(
    project_id: str,
    threat_id: str | None = None,
    service: ThreatService = Depends(get_threat_service)
) -> list[AttackPathResponse]:
    """获取攻击路径"""
    paths = await service.get_attack_paths(
        project_id=project_id,
        threat_id=threat_id
    )
    return [AttackPathResponse.model_validate(p) for p in paths]
```

#### 6.3.4 风险评估API

```python
# api/v1/risks.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/risks", tags=["risks"])

class RiskEvaluateRequest(BaseModel):
    project_id: str
    threat_ids: list[str] | None = None

class RiskResponse(BaseModel):
    id: str
    threat_id: str
    project_id: str
    impact_level: str
    feasibility_level: str
    risk_level: str
    risk_score: int
    treatment: str
    assessed_at: datetime

class RiskDetailResponse(RiskResponse):
    impact: dict       # 详细影响评估
    feasibility: dict  # 详细可行性评估
    treatment_rationale: str

class RiskMatrixResponse(BaseModel):
    matrix: list[list[dict]]  # 5x4矩阵
    statistics: dict

class RiskUpdateRequest(BaseModel):
    impact_level: str | None = None
    feasibility_level: str | None = None
    treatment: str | None = None
    treatment_rationale: str | None = None

@router.post("/evaluate")
async def evaluate_risks(
    request: RiskEvaluateRequest,
    service: RiskService = Depends(get_risk_service)
) -> dict:
    """执行风险评估"""
    task_id = await service.start_evaluation(
        project_id=request.project_id,
        threat_ids=request.threat_ids
    )

    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Risk evaluation started"
    }

@router.get("/")
async def list_risks(
    project_id: str,
    risk_level: str | None = None,
    page: int = 1,
    page_size: int = 50,
    service: RiskService = Depends(get_risk_service)
) -> dict:
    """获取风险列表"""
    risks, total = await service.list_risks(
        project_id=project_id,
        risk_level=risk_level,
        skip=(page - 1) * page_size,
        limit=page_size
    )

    return {
        "items": [RiskResponse.model_validate(r) for r in risks],
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/matrix")
async def get_risk_matrix(
    project_id: str,
    service: RiskService = Depends(get_risk_service)
) -> RiskMatrixResponse:
    """获取风险矩阵"""
    matrix = await service.get_risk_matrix(project_id)
    return RiskMatrixResponse(
        matrix=matrix.data,
        statistics=matrix.statistics
    )

@router.get("/{risk_id}")
async def get_risk(
    risk_id: str,
    service: RiskService = Depends(get_risk_service)
) -> RiskDetailResponse:
    """获取风险详情"""
    risk = await service.get_risk(risk_id)
    if not risk:
        raise HTTPException(404, "Risk not found")
    return RiskDetailResponse.model_validate(risk)

@router.put("/{risk_id}")
async def update_risk(
    risk_id: str,
    request: RiskUpdateRequest,
    service: RiskService = Depends(get_risk_service)
) -> dict:
    """手动调整风险评估"""
    await service.update_risk(risk_id, request.model_dump(exclude_none=True))
    return {"message": "Risk updated"}
```

#### 6.3.5 报告生成API

```python
# api/v1/reports.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

class ReportGenerateRequest(BaseModel):
    project_id: str
    report_type: str  # iso21434_tara, unr155, executive, technical
    output_format: str = "pdf"  # pdf, docx, xlsx
    include_sections: list[str] | None = None
    language: str = "zh"
    include_charts: bool = True

class ReportResponse(BaseModel):
    id: str
    project_id: str
    report_type: str
    output_format: str
    status: str
    file_size: int | None
    page_count: int | None
    generated_at: datetime | None
    created_at: datetime

@router.post("/generate")
async def generate_report(
    request: ReportGenerateRequest,
    service: ReportService = Depends(get_report_service)
) -> dict:
    """生成报告"""
    report = await service.generate_report(
        project_id=request.project_id,
        config=ReportConfig(
            report_type=ReportType(request.report_type),
            output_format=ReportFormat(request.output_format),
            include_sections=request.include_sections,
            language=request.language,
            include_charts=request.include_charts
        )
    )

    return {
        "report_id": report.id,
        "status": report.status.value,
        "message": "Report generation started"
    }

@router.get("/")
async def list_reports(
    project_id: str,
    page: int = 1,
    page_size: int = 20,
    service: ReportService = Depends(get_report_service)
) -> dict:
    """获取报告列表"""
    reports, total = await service.list_reports(
        project_id=project_id,
        skip=(page - 1) * page_size,
        limit=page_size
    )

    return {
        "items": [ReportResponse.model_validate(r) for r in reports],
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{report_id}")
async def get_report(
    report_id: str,
    service: ReportService = Depends(get_report_service)
) -> ReportResponse:
    """获取报告详情"""
    report = await service.get_report(report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return ReportResponse.model_validate(report)

@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    service: ReportService = Depends(get_report_service)
) -> StreamingResponse:
    """下载报告"""
    report = await service.get_report(report_id)
    if not report:
        raise HTTPException(404, "Report not found")

    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(400, "Report not ready")

    file_content = await service.get_report_file(report.file_path)

    # 设置文件名
    filename = f"TARA_Report_{report.project_id[:8]}.{report.config.output_format.value}"

    return StreamingResponse(
        iter([file_content]),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
```

#### 6.3.6 AI对话API

```python
# api/v1/chat.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

class ContextType(str, Enum):
    GENERAL = "general"        # 通用对话
    ASSET = "asset"            # 资产相关
    THREAT = "threat"          # 威胁相关
    RISK = "risk"              # 风险相关
    COMPLIANCE = "compliance"  # 合规相关

class ChatMessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatRequest(BaseModel):
    project_id: str
    message: str
    context_type: ContextType = ContextType.GENERAL
    context_id: str | None = None  # 关联的资产/威胁/风险ID
    conversation_id: str | None = None  # 多轮对话ID

class ChatMessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: ChatMessageRole
    content: str
    context_type: ContextType
    context_id: str | None
    references: list[dict] = []  # RAG检索的参考来源
    created_at: datetime

class ConversationResponse(BaseModel):
    id: str
    project_id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime

class SuggestionResponse(BaseModel):
    suggestions: list[str]  # 推荐的快捷问题

@router.post("/send", response_class=StreamingResponse)
async def send_message(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    发送对话消息（SSE流式响应）

    返回格式 (Server-Sent Events):
    - event: token, data: {"content": "部分响应"}
    - event: reference, data: {"source": "CVE-xxx", "content": "..."}
    - event: done, data: {"message_id": "uuid", "conversation_id": "uuid"}
    - event: error, data: {"code": "xxx", "message": "..."}
    """
    async def event_generator():
        async for event in service.chat_stream(
            project_id=request.project_id,
            message=request.message,
            context_type=request.context_type,
            context_id=request.context_id,
            conversation_id=request.conversation_id
        ):
            yield f"event: {event.type}\ndata: {event.data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.get("/conversations")
async def list_conversations(
    project_id: str,
    page: int = 1,
    page_size: int = 20,
    service: ChatService = Depends(get_chat_service)
) -> dict:
    """获取项目对话列表"""
    conversations, total = await service.list_conversations(
        project_id=project_id,
        skip=(page - 1) * page_size,
        limit=page_size
    )
    return {
        "items": [ConversationResponse.model_validate(c) for c in conversations],
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    service: ChatService = Depends(get_chat_service)
) -> dict:
    """获取对话详情及消息历史"""
    conversation = await service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(404, "Conversation not found")

    messages = await service.get_messages(conversation_id)

    return {
        "conversation": ConversationResponse.model_validate(conversation),
        "messages": [ChatMessageResponse.model_validate(m) for m in messages]
    }

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    service: ChatService = Depends(get_chat_service)
) -> dict:
    """删除对话"""
    await service.delete_conversation(conversation_id)
    return {"message": "Conversation deleted"}

@router.get("/suggestions")
async def get_suggestions(
    project_id: str,
    context_type: ContextType = ContextType.GENERAL,
    context_id: str | None = None,
    service: ChatService = Depends(get_chat_service)
) -> SuggestionResponse:
    """获取智能问题建议"""
    suggestions = await service.get_suggestions(
        project_id=project_id,
        context_type=context_type,
        context_id=context_id
    )
    return SuggestionResponse(suggestions=suggestions)
```

### 6.3 API响应格式

#### 成功响应

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2026-01-29T10:30:00Z",
    "request_id": "uuid"
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [ ... ]
  },
  "meta": {
    "timestamp": "2026-01-29T10:30:00Z",
    "request_id": "uuid"
  }
}
```

### 6.4 关键API时序图

#### 6.4.1 资产解析流程

```mermaid
sequenceDiagram
    participant Client as 前端
    participant API as API网关
    participant FileService as 文件服务
    participant Parser as 解析服务
    participant Vision as Qwen3-VL
    participant Graph as Neo4j

    Client->>API: POST /assets/upload
    API->>FileService: 存储原始文件
    FileService-->>API: 返回file_id
    API-->>Client: 返回upload_id

    Client->>API: POST /assets/parse
    API->>Parser: 启动解析任务
    Parser->>FileService: 获取文件

    alt 图片类型
        Parser->>Vision: 调用多模态解析
        Vision-->>Parser: 返回结构化JSON
    else 结构化文件
        Parser->>Parser: 直接解析
    end

    Parser->>Graph: 写入图数据库
    Graph-->>Parser: 确认写入
    Parser-->>API: 返回解析结果
    API-->>Client: 返回资产列表
```

#### 6.4.2 威胁分析流程

```mermaid
sequenceDiagram
    participant Client as 前端
    participant API as API网关
    participant ThreatSvc as 威胁服务
    participant RAG as RAG引擎
    participant Milvus as Milvus
    participant LLM as Qwen-Max
    participant Graph as Neo4j

    Client->>API: POST /threats/analyze
    API->>ThreatSvc: 启动威胁分析

    ThreatSvc->>Graph: 查询目标资产及关系
    Graph-->>ThreatSvc: 返回资产图谱

    loop 对每个资产/数据流
        ThreatSvc->>RAG: 检索相关威胁知识
        RAG->>Milvus: 向量相似度搜索
        Milvus-->>RAG: 返回Top-K结果
        RAG-->>ThreatSvc: 返回上下文知识

        ThreatSvc->>LLM: 生成STRIDE威胁
        Note over LLM: 系统Prompt:<br/>资产信息 + 检索知识<br/>+ STRIDE规则
        LLM-->>ThreatSvc: 返回威胁场景
    end

    ThreatSvc->>Graph: 存储威胁实体
    ThreatSvc-->>API: 返回分析结果
    API-->>Client: 返回威胁列表
```

---

## 7. AI推理引擎设计

### 7.1 多智能体架构

```mermaid
flowchart TB
    subgraph Orchestrator["编排层"]
        MainAgent["主控Agent<br/>任务分解与调度"]
    end

    subgraph Agents["专业Agent集群"]
        VisionAgent["**视觉解析Agent**<br/>Qwen3-VL<br/>图纸识别"]
        ThreatAgent["**威胁建模Agent**<br/>Qwen-Max<br/>威胁生成"]
        ImpactAgent["**影响评估Agent**<br/>Qwen-Max<br/>SFOP评估"]
        FeasibilityAgent["**可行性Agent**<br/>Qwen-Max<br/>攻击难度评估"]
        AuditAgent["**审计Agent**<br/>Qwen-Max<br/>结果校验"]
    end

    subgraph Tools["工具集"]
        GraphTool["图查询工具<br/>Cypher执行"]
        RAGTool["知识检索工具<br/>向量搜索"]
        CalcTool["计算工具<br/>风险矩阵"]
        ValidateTool["验证工具<br/>逻辑校验"]
    end

    MainAgent --> VisionAgent
    MainAgent --> ThreatAgent
    MainAgent --> ImpactAgent
    MainAgent --> FeasibilityAgent
    MainAgent --> AuditAgent

    VisionAgent --> ValidateTool
    ThreatAgent --> GraphTool
    ThreatAgent --> RAGTool
    ImpactAgent --> RAGTool
    FeasibilityAgent --> RAGTool
    FeasibilityAgent --> CalcTool
    AuditAgent --> ValidateTool

    style Orchestrator fill:#e3f2fd
    style Agents fill:#e8f5e9
    style Tools fill:#fff3e0
```

### 7.2 AI服务架构

AI服务采用抽象接口设计，支持多种LLM提供商的无缝切换。当前实现基于阿里云百炼平台的DashScope服务。

#### 7.2.1 服务接口设计

```mermaid
classDiagram
    class LLMProvider {
        <<interface>>
        +generate(model, messages, **kwargs) string
        +generate_with_vision(model, messages, images, **kwargs) string
        +embed(model, texts) list~list~float~~
    }

    class DashScopeLLM {
        +string api_key
        +string base_url
        +generate(model, messages, temperature, max_tokens, response_format) string
        +generate_with_vision(model, messages, images) string
        +embed(model, texts) list~list~float~~
    }

    class OpenAICompatibleLLM {
        +string api_key
        +string base_url
        +generate(model, messages, **kwargs) string
        +generate_with_vision(model, messages, images, **kwargs) string
        +embed(model, texts) list~list~float~~
    }

    LLMProvider <|.. DashScopeLLM
    LLMProvider <|.. OpenAICompatibleLLM
```

#### 7.2.2 接口方法说明

| 方法 | 输入参数 | 输出 | 说明 |
|-----|---------|------|------|
| `generate` | model: 模型ID<br/>messages: 消息列表<br/>temperature: 温度(0-1)<br/>max_tokens: 最大token数<br/>response_format: 响应格式(json/text) | string | 文本生成，支持JSON模式 |
| `generate_with_vision` | model: 多模态模型ID<br/>messages: 消息列表<br/>images: 图像字节列表 | string | 多模态生成，用于架构图解析 |
| `embed` | model: 嵌入模型ID<br/>texts: 文本列表 | list[list[float]] | 文本向量化，用于RAG检索 |

#### 7.2.3 DashScope服务调用流程

```mermaid
sequenceDiagram
    participant App as 应用层
    participant LLM as DashScopeLLM
    participant API as DashScope API

    Note over App,API: 文本生成流程
    App->>LLM: generate(model, messages, ...)
    LLM->>LLM: 构建请求payload
    LLM->>API: POST /services/aigc/text-generation/generation
    API-->>LLM: JSON响应
    LLM->>LLM: 提取content字段
    LLM-->>App: 返回生成文本

    Note over App,API: 多模态生成流程
    App->>LLM: generate_with_vision(model, messages, images)
    LLM->>LLM: Base64编码图像
    LLM->>LLM: 构建多模态消息
    LLM->>API: POST /services/aigc/multimodal-generation/generation
    API-->>LLM: JSON响应
    LLM-->>App: 返回解析结果

    Note over App,API: 向量嵌入流程
    App->>LLM: embed(model, texts)
    LLM->>API: POST /services/embeddings/text-embedding/text-embedding
    API-->>LLM: 嵌入向量列表
    LLM-->>App: 返回向量列表
```

#### 7.2.4 API端点配置

| 功能 | API端点 | 超时时间 | 说明 |
|-----|--------|---------|------|
| **文本生成** | `/services/aigc/text-generation/generation` | 120秒 | 用于威胁生成、风险评估等 |
| **多模态生成** | `/services/aigc/multimodal-generation/generation` | 180秒 | 用于架构图解析 |
| **文本嵌入** | `/services/embeddings/text-embedding/text-embedding` | 60秒 | 用于RAG向量化 |

#### 7.2.5 请求参数配置

**文本生成参数**

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| `model` | string | - | 模型ID，如 qwen-max, qwen-plus |
| `temperature` | float | 0.7 | 生成温度，0-1，越高越随机 |
| `max_tokens` | int | 4096 | 最大输出token数 |
| `response_format` | string | null | 设为"json"启用JSON模式 |

**多模态生成参数**

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| `model` | string | - | 多模态模型ID，如 qwen-vl-max |
| `images` | list[bytes] | - | 图像数据列表，自动Base64编码 |

**嵌入参数**

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| `model` | string | - | 嵌入模型ID，如 text-embedding-v3 |
| `text_type` | string | "document" | 文本类型，document或query |

#### 7.2.6 错误处理策略

```mermaid
flowchart TB
    subgraph Request["请求发送"]
        A["构建请求"] --> B["发送HTTP POST"]
    end

    subgraph Response["响应处理"]
        B --> C{"HTTP状态码"}
        C -->|200| D["解析JSON响应"]
        C -->|429| E["限流重试<br/>指数退避"]
        C -->|500+| F["服务端错误<br/>重试3次"]
        C -->|401/403| G["认证错误<br/>抛出异常"]
    end

    subgraph Extract["结果提取"]
        D --> H{"响应格式正确?"}
        H -->|是| I["提取content/embeddings"]
        H -->|否| J["解析错误<br/>记录日志"]
    end

    E --> B
    F --> B

    style Response fill:#fff3e0
    style Extract fill:#e8f5e9
```

### 7.2.7 视觉解析Agent设计

#### 7.2.1 处理流程

```mermaid
flowchart TB
    subgraph Input["输入"]
        Image["架构图/DFD"]
    end

    subgraph Preprocessing["预处理"]
        Resize["尺寸调整"]
        Split["大图切片<br/>(Sliding Window)"]
        ROI["ROI提取"]
    end

    subgraph VisionModel["Qwen3-VL处理"]
        SystemPrompt["系统Prompt注入"]
        Inference["模型推理"]
        JSONExtract["JSON提取"]
    end

    subgraph Postprocessing["后处理"]
        Merge["切片结果合并"]
        Validate["逻辑验证"]
        Correct["异常修正"]
    end

    subgraph Output["输出"]
        Components["组件列表"]
        Connections["连接关系"]
        Protocols["协议标注"]
    end

    Input --> Preprocessing
    Preprocessing --> VisionModel
    VisionModel --> Postprocessing
    Postprocessing --> Output

    style VisionModel fill:#e8f5e9
```

#### 7.2.2 System Prompt设计

```markdown
## 角色定义
你是一位资深的汽车电子系统架构师，精通ISO 26262和ISO/SAE 21434标准。

## 任务描述
分析上传的系统架构图（System Architecture Diagram）或数据流图（DFD）。

## 输出要求
1. 识别图中所有的矩形框，定义为"组件（Component）"
2. 识别所有连线，定义为"连接（Connection）"
3. 提取连线旁的文字标注，作为"协议（Protocol）"或"数据流（Data Flow）"
4. 识别无线连接图标（波浪线、天线），标记为"无线接口"
5. 识别信任边界（虚线框、颜色区分）

## 输出格式
严格输出以下JSON格式：
{
  "components": [
    {"id": "c1", "name": "组件名", "type": "hardware|software", "position": {"x": 0, "y": 0}}
  ],
  "connections": [
    {"source": "c1", "target": "c2", "protocol": "CAN", "data_flow": "诊断数据"}
  ],
  "trust_boundaries": [
    {"id": "tb1", "name": "边界名", "components": ["c1", "c2"]}
  ]
}
```

### 7.3 威胁推理Agent设计

#### 7.3.1 STRIDE规则引擎

```mermaid
flowchart TD
    subgraph Input["输入"]
        Asset["资产信息"]
        DataFlow["数据流"]
        Context["上下文知识"]
    end

    subgraph STRIDERules["STRIDE规则检查"]
        S_Check["S: 检查认证机制<br/>无MAC/签名 → 伪造威胁"]
        T_Check["T: 检查完整性保护<br/>明文传输 → 篡改威胁"]
        R_Check["R: 检查日志审计<br/>无日志 → 否认威胁"]
        I_Check["I: 检查加密措施<br/>无加密 → 泄露威胁"]
        D_Check["D: 检查限流机制<br/>无限流 → DoS威胁"]
        E_Check["E: 检查访问控制<br/>调试口开放 → 提权威胁"]
    end

    subgraph Output["输出"]
        ThreatList["威胁场景列表"]
    end

    Input --> S_Check & T_Check & R_Check & I_Check & D_Check & E_Check
    S_Check & T_Check & R_Check & I_Check & D_Check & E_Check --> ThreatList

    style STRIDERules fill:#ffebee
```

#### 7.3.2 威胁生成Prompt模板

```markdown
## 角色
你是一名汽车网络安全专家，精通ISO/SAE 21434标准和STRIDE威胁建模方法。

## 背景
资产信息：{asset_info}
数据流描述：{data_flow}
参考知识库：{retrieved_knowledge}

## 任务
基于STRIDE模型，识别该资产/数据流的潜在威胁场景。

## 约束
1. 每个STRIDE类别至少考虑一个威胁
2. 威胁描述需具体，包含攻击者行为和影响
3. 关联UN R155 Annex 5中的威胁类别（如适用）

## 输出格式
| ID | 威胁描述 | STRIDE类别 | 攻击向量 | 影响维度(SFOP) |
|----|---------|-----------|---------|---------------|
```

### 7.3.3 对话Agent设计

对话Agent是用户与AI TARA平台交互的核心接口，支持多轮对话、上下文感知和RAG增强回答。

#### 对话系统架构

```mermaid
flowchart TB
    subgraph Frontend["前端"]
        ChatPanel["对话面板"]
        ContextProvider["上下文提供器"]
    end

    subgraph ChatService["对话服务"]
        ConvManager["会话管理器"]
        ContextBuilder["上下文构建器"]
        StreamHandler["流式响应处理器"]
    end

    subgraph AILayer["AI层"]
        ChatAgent["对话Agent"]
        RAGEngine["RAG引擎"]
        LLM["Qwen-Max"]
    end

    subgraph Knowledge["知识源"]
        ProjectData["项目数据<br/>资产/威胁/风险"]
        KnowledgeBase["知识库<br/>CVE/ATT&CK/标准"]
        ConvHistory["对话历史"]
    end

    ChatPanel --> ConvManager
    ContextProvider --> ContextBuilder
    ConvManager --> ChatAgent
    ContextBuilder --> ChatAgent
    ChatAgent --> RAGEngine
    ChatAgent --> LLM
    RAGEngine --> KnowledgeBase
    ContextBuilder --> ProjectData
    ConvManager --> ConvHistory
    StreamHandler --> ChatPanel

    style ChatService fill:#e8f5e9
    style AILayer fill:#e3f2fd
```

#### 对话领域模型

```mermaid
classDiagram
    class Conversation {
        +string id
        +string project_id
        +string title
        +int message_count
        +datetime created_at
        +datetime updated_at
    }

    class ChatMessage {
        +string id
        +string conversation_id
        +ChatMessageRole role
        +string content
        +ContextType context_type
        +string context_id
        +Reference[] references
        +datetime created_at
    }

    class Reference {
        +string source
        +string source_id
        +string content
        +float score
    }

    class ChatContext {
        +string project_id
        +ContextType context_type
        +string context_id
        +Asset asset
        +Threat threat
        +Risk risk
        +ChatMessage[] history
    }

    Conversation "1" --> "*" ChatMessage
    ChatMessage --> "*" Reference
    ChatMessage ..> ChatContext
```

#### 上下文类型与处理策略

| 上下文类型 | 触发场景 | 自动注入的上下文 | RAG检索集合 |
|-----------|---------|-----------------|-------------|
| `general` | 通用提问 | 项目基本信息 | 全部知识库 |
| `asset` | 资产详情页提问 | 资产属性、关联关系、数据流 | threat_knowledge, cve_database |
| `threat` | 威胁详情页提问 | 威胁描述、STRIDE分类、攻击路径 | attack_patterns, unr155_threats |
| `risk` | 风险详情页提问 | 风险等级、SFOP评估、处置建议 | iso21434_clauses, threat_knowledge |
| `compliance` | 合规报告页提问 | UN R155/ISO 21434条款映射 | iso21434_clauses, unr155_threats |

#### 对话处理流程

```mermaid
flowchart TB
    subgraph Input["输入处理"]
        A["接收用户消息"] --> B["解析上下文类型"]
        B --> C["加载会话历史<br/>最近N轮"]
    end

    subgraph ContextBuild["上下文构建"]
        D["获取项目数据"]
        E["获取关联实体<br/>资产/威胁/风险"]
        F["构建System Prompt"]
    end

    subgraph RAGRetrieval["RAG检索"]
        G["确定检索集合"] --> H["向量化查询"]
        H --> I["多知识库并行检索"]
        I --> J["重排序取Top-K"]
    end

    subgraph Generation["生成回答"]
        K["组装完整Prompt"]
        L["调用Qwen-Max<br/>流式生成"]
        M["解析引用来源"]
    end

    subgraph Output["输出处理"]
        N["SSE流式推送"]
        O["保存消息记录"]
        P["更新会话状态"]
    end

    C --> D
    D --> E
    E --> F
    F --> G
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    O --> P

    style ContextBuild fill:#fff3e0
    style RAGRetrieval fill:#e8f5e9
    style Generation fill:#e3f2fd
```

#### System Prompt设计

**基础System Prompt**

> 你是AI TARA平台的智能助手，专注于汽车网络安全威胁分析与风险评估。
> 你精通ISO/SAE 21434标准、UN R155法规、STRIDE威胁建模和CVSS风险评估。
> 请基于提供的项目上下文和参考资料，给出专业、准确、有帮助的回答。
> 回答时请：
> 1. 使用清晰的结构化格式
> 2. 引用具体的标准条款或CVE编号（如适用）
> 3. 给出可操作的建议
> 4. 如果信息不足，明确说明需要哪些额外信息

**上下文Prompt模板**

| 上下文类型 | 注入内容 |
|-----------|---------|
| `asset` | `当前分析的资产：{asset.name}\n类型：{asset.type}\n安全属性：{asset.security_properties}\n关联接口：{asset.interfaces}` |
| `threat` | `当前分析的威胁：{threat.description}\nSTRIDE类别：{threat.stride_category}\n目标资产：{threat.target_assets}\n攻击向量：{threat.attack_vector}` |
| `risk` | `当前分析的风险：\n威胁描述：{risk.threat.description}\n影响等级：{risk.impact_level}\n可行性等级：{risk.feasibility_level}\n风险等级：{risk.risk_level}` |

#### 智能问题建议

系统根据当前上下文自动生成推荐问题：

```mermaid
flowchart LR
    subgraph ContextAnalysis["上下文分析"]
        A["分析当前页面"]
        B["获取实体属性"]
        C["检查缺失信息"]
    end

    subgraph SuggestionGeneration["建议生成"]
        D["预定义问题模板"]
        E["LLM动态生成"]
        F["历史高频问题"]
    end

    subgraph Output["输出"]
        G["排序去重"]
        H["返回Top-5建议"]
    end

    ContextAnalysis --> SuggestionGeneration
    D --> G
    E --> G
    F --> G
    G --> H

    style SuggestionGeneration fill:#e8f5e9
```

**预定义问题模板示例**

| 上下文类型 | 推荐问题模板 |
|-----------|-------------|
| `asset` | "这个{asset_type}有哪些已知的CVE漏洞？"<br/>"如何评估{asset_name}的安全属性？"<br/>"{asset_name}的主要攻击面是什么？" |
| `threat` | "这个威胁的攻击可行性如何评估？"<br/>"有哪些缓解措施可以应对{stride_category}威胁？"<br/>"这个威胁对应UN R155的哪个条款？" |
| `risk` | "为什么这个风险被评为{risk_level}级？"<br/>"有哪些类似的历史案例？"<br/>"推荐的风险处置策略是什么？" |

#### 流式响应事件格式

| 事件类型 | 数据格式 | 说明 |
|---------|---------|------|
| `token` | `{"content": "部分文本"}` | 生成的文本片段 |
| `reference` | `{"source": "CVE-2024-xxx", "type": "cve", "content": "..."}` | 引用的参考来源 |
| `suggestion` | `{"actions": [{"label": "查看详情", "url": "/threats/xxx"}]}` | 推荐的后续操作 |
| `done` | `{"message_id": "uuid", "conversation_id": "uuid"}` | 生成完成 |
| `error` | `{"code": "RATE_LIMIT", "message": "请求过于频繁"}` | 错误信息 |

### 7.4 RAG检索引擎设计

```mermaid
flowchart LR
    subgraph Query["查询处理"]
        UserQuery["用户查询/资产描述"]
        QueryEmbed["查询向量化<br/>text-embedding-v3"]
    end

    subgraph Retrieval["检索"]
        VectorSearch["向量相似度搜索<br/>Milvus"]
        Rerank["重排序<br/>Cross-Encoder"]
        TopK["Top-K结果"]
    end

    subgraph KnowledgeBases["知识库"]
        CVE["CVE漏洞库"]
        MITRE["MITRE ATT&CK<br/>for Vehicle"]
        ISO["ISO 21434<br/>标准条款"]
        UNR155["UN R155<br/>威胁目录"]
        History["历史TARA<br/>案例库"]
    end

    subgraph Generation["生成"]
        Context["上下文组装"]
        LLM["Qwen-Max<br/>生成回答"]
    end

    UserQuery --> QueryEmbed
    QueryEmbed --> VectorSearch
    VectorSearch --> KnowledgeBases
    KnowledgeBases --> Rerank
    Rerank --> TopK
    TopK --> Context
    Context --> LLM

    style Retrieval fill:#e8f5e9
    style KnowledgeBases fill:#e3f2fd
```

#### 7.4.1 RAG引擎设计

RAG (Retrieval-Augmented Generation) 引擎是威胁分析的核心组件，负责从知识库中检索相关信息并增强LLM生成的质量。

##### 组件架构

```mermaid
classDiagram
    class RAGEngine {
        -LLMProvider llm
        -VectorStore vector_store
        -string embedding_model
        -string rerank_model
        -dict knowledge_bases
        +retrieve(query, collections, top_k, filters, rerank) RetrievedDocument[]
        +generate_with_context(query, system_prompt, collections, top_k) string
    }

    class VectorStore {
        <<interface>>
        +search(collection, query_vector, top_k, filters) dict[]
        +insert(collection, vectors, documents) string[]
    }

    class MilvusVectorStore {
        +string host
        +int port
        +search(collection, query_vector, top_k, filters) dict[]
        +insert(collection, vectors, documents) string[]
    }

    class RetrievedDocument {
        +string id
        +string content
        +float score
        +dict metadata
        +string collection
    }

    RAGEngine --> VectorStore
    RAGEngine --> LLMProvider
    RAGEngine ..> RetrievedDocument
    VectorStore <|.. MilvusVectorStore
```

##### 检索流程

```mermaid
flowchart TB
    subgraph Input["查询输入"]
        Query["用户查询/<br/>资产描述"]
    end

    subgraph Embedding["向量化"]
        A["调用LLM.embed()"] --> B["获取查询向量<br/>1536维"]
    end

    subgraph MultiSearch["多知识库检索"]
        C["确定目标集合"] --> D["并行搜索"]
        D --> E1["threat_knowledge<br/>权重1.0"]
        D --> E2["cve_database<br/>权重0.8"]
        D --> E3["attack_patterns<br/>权重0.9"]
        D --> E4["iso21434_clauses<br/>权重0.7"]
        D --> E5["unr155_threats<br/>权重0.9"]
    end

    subgraph Merge["合并排序"]
        F["应用集合权重"] --> G["按score排序"]
        G --> H["取Top-K×2候选"]
    end

    subgraph Rerank["重排序"]
        I{"启用重排序?"}
        I -->|是| J["LLM重排序<br/>qwen-plus"]
        I -->|否| K["跳过"]
        J --> L["解析排序结果"]
    end

    subgraph Output["输出"]
        M["返回Top-K<br/>RetrievedDocument[]"]
    end

    Query --> Embedding
    Embedding --> MultiSearch
    E1 & E2 & E3 & E4 & E5 --> Merge
    Merge --> Rerank
    L --> M
    K --> M

    style MultiSearch fill:#e8f5e9
    style Rerank fill:#fff3e0
```

##### 知识库配置

| 知识库ID | 描述 | 检索权重 | 数据来源 |
|---------|------|---------|---------|
| `threat_knowledge` | 汽车安全威胁案例库 | 1.0 | 历史TARA分析、安全研究报告 |
| `cve_database` | CVE漏洞数据库 | 0.8 | NVD |
| `attack_patterns` | MITRE ATT&CK攻击模式 | 0.9 | ATT&CK for ICS/Vehicle |
| `iso21434_clauses` | ISO 21434标准条款 | 0.7 | 标准文档解析 |
| `unr155_threats` | UN R155威胁目录 | 0.9 | UN R155 Annex 5 |

##### 接口方法说明

| 方法 | 输入参数 | 输出 | 说明 |
|-----|---------|------|------|
| `retrieve` | query: 查询文本<br/>collections: 目标集合列表<br/>top_k: 返回数量<br/>filters: 过滤条件<br/>rerank: 是否重排序 | RetrievedDocument[] | 从知识库检索相关文档 |
| `generate_with_context` | query: 用户问题<br/>system_prompt: 系统提示<br/>collections: 目标集合<br/>top_k: 上下文文档数 | string | 检索增强生成回答 |

##### 重排序策略

```mermaid
sequenceDiagram
    participant RAG as RAGEngine
    participant LLM as Qwen-Plus

    RAG->>RAG: 获取Top-K×2候选文档
    RAG->>RAG: 截取每篇文档前500字符
    RAG->>LLM: 发送重排序Prompt
    Note over LLM: "对以下文档按相关性排序<br/>返回JSON数组 [3,1,5,2,4]"
    LLM-->>RAG: 返回排序编号列表
    RAG->>RAG: 解析JSON数组
    alt 解析成功
        RAG->>RAG: 按新顺序重排文档
    else 解析失败
        RAG->>RAG: 保持原始顺序
    end
    RAG->>RAG: 返回Top-K结果
```

##### 上下文构建

检索到的文档按以下格式组装为LLM上下文：

```
### 参考1 (来源: cve_database)
CVE-2024-xxxxx相关内容...

### 参考2 (来源: threat_knowledge)
历史威胁案例相关内容...

### 参考3 (来源: unr155_threats)
UN R155威胁目录相关内容...
```

#### 7.4.2 知识库索引构建

##### 索引构建流程

```mermaid
flowchart TB
    subgraph Input["输入"]
        Documents["原始文档列表"]
    end

    subgraph Chunking["文档分块"]
        A["遍历文档"] --> B["按chunk_size分块<br/>默认512字符"]
        B --> C["在句子边界切分<br/>优先: 。 \\n . ；"]
        C --> D["添加chunk_overlap<br/>默认50字符"]
    end

    subgraph Embedding["批量向量化"]
        E["按batch_size分批<br/>默认20"]
        E --> F["调用LLM.embed()"]
        F --> G["收集向量结果"]
    end

    subgraph Storage["存储"]
        H["调用VectorStore.insert()"]
        H --> I["写入Milvus集合"]
    end

    subgraph Output["输出"]
        J["返回chunk_count"]
    end

    Documents --> Chunking
    D --> E
    G --> H
    I --> J

    style Chunking fill:#e3f2fd
    style Embedding fill:#fff3e0
    style Storage fill:#e8f5e9
```

##### 分块策略配置

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `chunk_size` | 512 | 每个分块的最大字符数 |
| `chunk_overlap` | 50 | 相邻分块的重叠字符数 |
| `batch_size` | 20 | 向量化批处理大小 |
| `embedding_model` | text-embedding-v3 | 嵌入模型ID |

##### 句子边界检测

分块时优先在以下分隔符处切分，保持语义完整性：

| 优先级 | 分隔符 | 说明 |
|-------|-------|------|
| 1 | `。` | 中文句号 |
| 2 | `\n` | 换行符 |
| 3 | `. ` | 英文句号+空格 |
| 4 | `；` | 中文分号 |

##### 特定知识库索引

**CVE数据库索引格式**

| 字段 | 来源 | 说明 |
|-----|------|------|
| `id` | cve_id | CVE编号作为文档ID |
| `content` | 组合字段 | CVE编号+CVSS评分+影响组件+描述+缓解措施 |
| `metadata.source` | 固定值 | "cve" |
| `metadata.cvss_score` | cvss_score | CVSS评分 |
| `metadata.published_date` | published_date | 发布日期 |

**UN R155威胁目录索引格式**

| 字段 | 来源 | 说明 |
|-----|------|------|
| `id` | threat.id | 威胁ID |
| `content` | 组合字段 | 威胁ID+类别+描述+攻击向量+缓解要求 |
| `metadata.source` | 固定值 | "unr155" |
| `metadata.category` | threat.category | 威胁类别 |

##### Milvus集合Schema

每个知识库集合采用统一的Schema设计：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `id` | VARCHAR(256) | 主键，文档/分块ID |
| `embedding` | FLOAT_VECTOR(1536) | 向量嵌入 |
| `content` | VARCHAR(65535) | 文档内容 |
| `metadata` | JSON | 元数据字典 |

**索引配置**

| 参数 | 值 | 说明 |
|-----|-----|-----|
| `metric_type` | COSINE | 余弦相似度 |
| `index_type` | IVF_FLAT | IVF平面索引 |
| `nlist` | 1024 | 聚类数量 |
| `nprobe` | 16 | 搜索时探测的聚类数

---

## 8. 知识图谱设计

### 8.1 图谱构建流程

```mermaid
flowchart TB
    subgraph DataSources["数据源"]
        BOM["BOM清单"]
        DFD["数据流图"]
        Arch["架构图"]
        Spec["规范文档"]
    end

    subgraph Extraction["实体抽取"]
        AI_Extract["AI抽取<br/>Qwen-VL/Max"]
        Rule_Extract["规则抽取<br/>正则/模板"]
    end

    subgraph EntityResolution["实体消歧"]
        Dedup["去重"]
        Merge["合并"]
        Link["链接"]
    end

    subgraph GraphConstruction["图谱构建"]
        NodeCreate["节点创建"]
        RelCreate["关系创建"]
        PropEnrich["属性丰富"]
    end

    subgraph Validation["验证"]
        Schema_Check["Schema校验"]
        Logic_Check["逻辑校验"]
        Human_Review["人工审核"]
    end

    DataSources --> Extraction
    Extraction --> EntityResolution
    EntityResolution --> GraphConstruction
    GraphConstruction --> Validation

    style Extraction fill:#e8f5e9
    style GraphConstruction fill:#e3f2fd
```

### 8.2 攻击路径分析

#### 8.2.1 Cypher查询示例

```cypher
// 查找从外部蜂窝接口到车门解锁功能的最短攻击路径
MATCH (source:Interface {access_level: 'Public', type: 'Cellular'})
MATCH (target:Function {name: 'Door_Unlock'})
MATCH path = shortestPath((source)-[*..10]->(target))
WHERE ALL(r IN relationships(path) WHERE r.blocked = false)
RETURN path, length(path) as hops
ORDER BY hops
LIMIT 5
```

#### 8.2.2 攻击路径可视化

```mermaid
graph LR
    subgraph External["外部网络"]
        Cellular["蜂窝接口<br/>📡"]
    end

    subgraph TBOX["T-BOX域"]
        Modem["Modem<br/>调制解调器"]
        TBOX_MCU["T-BOX MCU"]
    end

    subgraph Gateway["网关域"]
        GW["车辆网关"]
    end

    subgraph Body["车身域"]
        BCM["车身控制器<br/>(BCM)"]
        Door["车门ECU<br/>🚪"]
    end

    Cellular -->|LTE| Modem
    Modem -->|UART| TBOX_MCU
    TBOX_MCU -->|Ethernet| GW
    GW -->|CAN| BCM
    BCM -->|LIN| Door

    style Cellular fill:#ffcdd2
    style Door fill:#c8e6c9
```

### 8.3 图谱查询优化

| 优化策略 | 说明 | 适用场景 |
|---------|------|---------|
| **索引优化** | 为高频查询属性建立索引 | 按ID、名称查询 |
| **路径长度限制** | 限制`shortestPath`深度 | 攻击路径分析 |
| **关系过滤** | 提前过滤不可达关系 | 跨信任域分析 |
| **结果缓存** | 缓存常用查询结果 | 重复性分析 |

---

## 9. 工作流程设计

### 9.1 完整TARA流程

```mermaid
flowchart TB
    subgraph Phase1["阶段1: 项目初始化"]
        P1_1["创建项目"]
        P1_2["定义分析范围<br/>(Item Definition)"]
        P1_3["上传工程资料"]
    end

    subgraph Phase2["阶段2: 资产识别"]
        P2_1["解析BOM"]
        P2_2["解析架构图"]
        P2_3["构建资产图谱"]
        P2_4["标注信任边界"]
    end

    subgraph Phase3["阶段3: 威胁分析"]
        P3_1["识别数据流"]
        P3_2["STRIDE威胁生成"]
        P3_3["攻击路径分析"]
        P3_4["威胁场景确认"]
    end

    subgraph Phase4["阶段4: 风险评估"]
        P4_1["影响评级(SFOP)"]
        P4_2["可行性评估"]
        P4_3["风险计算"]
        P4_4["风险排序"]
    end

    subgraph Phase5["阶段5: 处置与报告"]
        P5_1["制定缓解措施"]
        P5_2["生成TARA报告"]
        P5_3["合规性审核"]
        P5_4["导出归档"]
    end

    Phase1 --> Phase2 --> Phase3 --> Phase4 --> Phase5

    style Phase1 fill:#e3f2fd
    style Phase2 fill:#e8f5e9
    style Phase3 fill:#fff3e0
    style Phase4 fill:#fce4ec
    style Phase5 fill:#f3e5f5
```

### 9.2 状态机设计

```mermaid
stateDiagram-v2
    [*] --> Draft: 创建项目
    Draft --> Analyzing: 启动分析
    Analyzing --> AssetIdentification: 资产识别
    AssetIdentification --> ThreatModeling: 威胁建模
    ThreatModeling --> RiskAssessment: 风险评估
    RiskAssessment --> Review: 提交审核
    Review --> Approved: 审核通过
    Review --> ThreatModeling: 退回修改
    Approved --> Archived: 归档

    Draft --> [*]: 删除
    Analyzing --> Draft: 取消
```

### 9.3 IVI系统TARA流程示例

```mermaid
sequenceDiagram
    participant User as 安全工程师
    participant Platform as TARA平台
    participant AI as AI引擎
    participant Graph as 知识图谱

    User->>Platform: 创建IVI TARA项目
    User->>Platform: 上传IVI架构图、BOM

    Platform->>AI: 解析架构图
    AI-->>Platform: 返回组件、连接关系

    Platform->>Graph: 构建IVI资产图谱
    Note over Graph: 节点: SoC, WiFi, BT,<br/>USB, Apps...<br/>关系: 连接、依赖

    User->>Platform: 启动威胁分析
    Platform->>AI: STRIDE威胁生成
    Note over AI: 分析每个数据流<br/>生成威胁场景

    AI->>Graph: 查询攻击路径
    Graph-->>AI: 返回可达路径
    AI-->>Platform: 返回威胁+路径

    User->>Platform: 确认威胁场景
    Platform->>AI: 风险评估
    AI-->>Platform: 返回影响/可行性评级

    Platform->>Platform: 计算风险矩阵
    User->>Platform: 生成报告
    Platform-->>User: 下载TARA报告
```

---

## 10. 前端设计

### 10.1 整体架构

```mermaid
flowchart TB
    subgraph Pages["页面层"]
        Dashboard["仪表盘"]
        Projects["项目管理"]
        Assets["资产管理"]
        Threats["威胁分析"]
        Risks["风险评估"]
        Reports["报告中心"]
    end

    subgraph Components["组件层"]
        Layout["布局组件"]
        Charts["图表组件"]
        Forms["表单组件"]
        Tables["表格组件"]
        Graph["图谱组件"]
    end

    subgraph Services["服务层"]
        API["API客户端"]
        Store["状态管理"]
        Router["路由管理"]
    end

    subgraph Infra["基础设施"]
        HTTP["HTTP Client"]
        WS["WebSocket"]
        Cache["本地缓存"]
    end

    Pages --> Components
    Components --> Services
    Services --> Infra

    style Pages fill:#e3f2fd
    style Components fill:#e8f5e9
    style Services fill:#fff3e0
    style Infra fill:#fce4ec
```

### 10.2 技术栈详情

| 技术 | 版本 | 用途 |
|-----|------|-----|
| React | 19.2.4 | UI框架 |
| TypeScript | 5.9 | 类型安全 |
| Vite | 7.3.1 | 构建工具 |
| Tailwind CSS | 4.1.18 | 样式框架 |
| TanStack Query | 5.x | 数据获取/缓存 |
| TanStack Router | 1.x | 路由管理 |
| Zustand | 5.x | 状态管理 |
| Cytoscape.js | 3.x | 图谱可视化 |
| ECharts | 5.x | 图表组件 |
| React Hook Form | 7.x | 表单处理 |

### 10.3 项目结构

```
frontend/
├── src/
│   ├── app/                    # 应用入口
│   │   ├── App.tsx
│   │   ├── router.tsx          # 路由配置
│   │   └── providers.tsx       # 全局Provider
│   │
│   ├── pages/                  # 页面组件
│   │   ├── dashboard/
│   │   │   └── DashboardPage.tsx
│   │   ├── projects/
│   │   │   ├── ProjectListPage.tsx
│   │   │   └── ProjectDetailPage.tsx
│   │   ├── assets/
│   │   │   ├── AssetListPage.tsx
│   │   │   ├── AssetGraphPage.tsx
│   │   │   └── AssetUploadPage.tsx
│   │   ├── threats/
│   │   │   ├── ThreatListPage.tsx
│   │   │   ├── ThreatDetailPage.tsx
│   │   │   └── AttackPathPage.tsx
│   │   ├── risks/
│   │   │   ├── RiskListPage.tsx
│   │   │   └── RiskMatrixPage.tsx
│   │   └── reports/
│   │       ├── ReportListPage.tsx
│   │       └── ReportGeneratePage.tsx
│   │
│   ├── components/             # 通用组件
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Header.tsx
│   │   ├── charts/
│   │   │   ├── RiskPieChart.tsx
│   │   │   ├── StrideBarChart.tsx
│   │   │   └── TrendLineChart.tsx
│   │   ├── graph/
│   │   │   ├── AssetGraph.tsx
│   │   │   └── AttackPathGraph.tsx
│   │   ├── tables/
│   │   │   ├── DataTable.tsx
│   │   │   └── ThreatTable.tsx
│   │   ├── chat/               # AI对话组件
│   │   │   ├── ChatPanel.tsx       # 对话面板主组件
│   │   │   ├── ChatMessage.tsx     # 消息气泡组件
│   │   │   ├── ChatInput.tsx       # 输入框组件
│   │   │   ├── ChatHistory.tsx     # 历史记录列表
│   │   │   ├── ChatSuggestions.tsx # 快捷问题建议
│   │   │   ├── ChatReference.tsx   # 引用来源组件
│   │   │   └── ChatButton.tsx      # 悬浮触发按钮
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Modal.tsx
│   │       └── ...
│   │
│   ├── features/               # 功能模块
│   │   ├── assets/
│   │   │   ├── api.ts
│   │   │   ├── hooks.ts
│   │   │   └── types.ts
│   │   ├── threats/
│   │   │   ├── api.ts
│   │   │   ├── hooks.ts
│   │   │   └── types.ts
│   │   ├── chat/               # 对话功能模块
│   │   │   ├── api.ts              # 对话API封装
│   │   │   ├── hooks.ts            # 对话相关Hooks
│   │   │   ├── types.ts            # 对话类型定义
│   │   │   ├── context.tsx         # 对话上下文Provider
│   │   │   └── utils.ts            # SSE解析等工具
│   │   └── ...
│   │
│   ├── services/               # 服务层
│   │   ├── api/
│   │   │   ├── client.ts       # API客户端
│   │   │   └── endpoints.ts
│   │   ├── websocket/
│   │   │   └── client.ts
│   │   └── sse/                # SSE服务
│   │       └── client.ts           # SSE客户端封装
│   │
│   ├── stores/                 # 状态管理
│   │   ├── projectStore.ts
│   │   ├── uiStore.ts
│   │   └── chatStore.ts        # 对话状态管理
│   │
│   ├── hooks/                  # 通用Hooks
│   │   ├── useAsync.ts
│   │   ├── useDebounce.ts
│   │   └── useSSE.ts           # SSE Hook
│   │
│   ├── utils/                  # 工具函数
│   │   ├── format.ts
│   │   └── validation.ts
│   │
│   └── types/                  # 类型定义
│       ├── api.ts
│       └── models.ts
│
├── public/
├── index.html
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

### 10.4 核心组件设计

#### 10.4.1 API客户端

```typescript
// services/api/client.ts
import { QueryClient } from '@tanstack/react-query';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

class ApiError extends Error {
  constructor(
    public code: string,
    public message: string,
    public status: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(
      error.code || 'UNKNOWN_ERROR',
      error.message || 'An error occurred',
      response.status
    );
  }

  return response.json();
}

export const api = {
  get: <T>(endpoint: string) => fetchApi<T>(endpoint),

  post: <T>(endpoint: string, data?: unknown) =>
    fetchApi<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data?: unknown) =>
    fetchApi<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string) =>
    fetchApi<T>(endpoint, { method: 'DELETE' }),

  upload: async <T>(endpoint: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        error.code || 'UPLOAD_ERROR',
        error.message || 'Upload failed',
        response.status
      );
    }

    return response.json() as Promise<T>;
  },
};

// React Query 客户端配置
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5分钟
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

#### 10.4.2 数据获取Hooks

```typescript
// features/assets/hooks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api/client';
import type { Asset, AssetGraph, ParseResult } from './types';

// 查询Keys
export const assetKeys = {
  all: ['assets'] as const,
  lists: () => [...assetKeys.all, 'list'] as const,
  list: (projectId: string, filters?: object) =>
    [...assetKeys.lists(), projectId, filters] as const,
  details: () => [...assetKeys.all, 'detail'] as const,
  detail: (id: string) => [...assetKeys.details(), id] as const,
  graph: (projectId: string) => [...assetKeys.all, 'graph', projectId] as const,
};

// 获取资产列表
export function useAssets(projectId: string, filters?: {
  assetType?: string;
  page?: number;
  pageSize?: number;
}) {
  return useQuery({
    queryKey: assetKeys.list(projectId, filters),
    queryFn: () => {
      const params = new URLSearchParams({
        project_id: projectId,
        ...(filters?.assetType && { asset_type: filters.assetType }),
        page: String(filters?.page || 1),
        page_size: String(filters?.pageSize || 50),
      });
      return api.get<{ items: Asset[]; total: number }>(
        `/assets?${params}`
      );
    },
  });
}

// 获取资产详情
export function useAsset(assetId: string) {
  return useQuery({
    queryKey: assetKeys.detail(assetId),
    queryFn: () => api.get<Asset>(`/assets/${assetId}`),
    enabled: !!assetId,
  });
}

// 获取资产图谱
export function useAssetGraph(projectId: string) {
  return useQuery({
    queryKey: assetKeys.graph(projectId),
    queryFn: () => api.get<AssetGraph>(`/assets/graph?project_id=${projectId}`),
  });
}

// 上传资产文件
export function useUploadAsset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      projectId,
      file,
    }: {
      projectId: string;
      file: File;
    }) => {
      return api.upload<{ file_id: string }>(
        `/assets/upload?project_id=${projectId}`,
        file
      );
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: assetKeys.list(variables.projectId),
      });
    },
  });
}

// 解析资产文件
export function useParseAsset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ fileId }: { fileId: string }) => {
      return api.post<ParseResult>('/assets/parse', { file_id: fileId });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assetKeys.all });
    },
  });
}
```

#### 10.4.3 资产图谱组件

```typescript
// components/graph/AssetGraph.tsx
import { useEffect, useRef, useCallback } from 'react';
import cytoscape, { Core, NodeSingular } from 'cytoscape';
import type { AssetGraph as AssetGraphData } from '@/features/assets/types';

interface AssetGraphProps {
  data: AssetGraphData;
  onNodeClick?: (nodeId: string) => void;
  selectedNodeId?: string;
}

export function AssetGraph({
  data,
  onNodeClick,
  selectedNodeId,
}: AssetGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  // 初始化Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#4F46E5',
            label: 'data(label)',
            'text-valign': 'bottom',
            'text-margin-y': 8,
            width: 40,
            height: 40,
          },
        },
        {
          selector: 'node[type="hardware"]',
          style: { 'background-color': '#059669' },
        },
        {
          selector: 'node[type="software"]',
          style: { 'background-color': '#2563EB' },
        },
        {
          selector: 'node[type="interface"]',
          style: { 'background-color': '#D97706' },
        },
        {
          selector: 'node[type="data"]',
          style: { 'background-color': '#7C3AED' },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 3,
            'border-color': '#EF4444',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#9CA3AF',
            'target-arrow-color': '#9CA3AF',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
          },
        },
        {
          selector: '.trust-boundary',
          style: {
            'background-color': '#F3F4F6',
            'background-opacity': 0.5,
            'border-width': 2,
            'border-style': 'dashed',
            'border-color': '#6B7280',
          },
        },
      ],
      layout: {
        name: 'cose',
        animate: true,
        nodeRepulsion: 8000,
        idealEdgeLength: 100,
      },
    });

    cyRef.current = cy;

    // 节点点击事件
    cy.on('tap', 'node', (evt) => {
      const node = evt.target as NodeSingular;
      onNodeClick?.(node.id());
    });

    return () => {
      cy.destroy();
    };
  }, [onNodeClick]);

  // 更新图谱数据
  useEffect(() => {
    if (!cyRef.current || !data) return;

    const cy = cyRef.current;

    // 清空现有元素
    cy.elements().remove();

    // 添加信任边界（作为compound节点）
    data.trust_boundaries?.forEach((tb) => {
      cy.add({
        group: 'nodes',
        data: {
          id: tb.id,
          label: tb.name,
        },
        classes: 'trust-boundary',
      });
    });

    // 添加节点
    data.nodes.forEach((node) => {
      cy.add({
        group: 'nodes',
        data: {
          id: node.id,
          label: node.name,
          type: node.type,
          parent: node.trust_boundary_id,
        },
      });
    });

    // 添加边
    data.edges.forEach((edge) => {
      cy.add({
        group: 'edges',
        data: {
          id: edge.id || `${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target,
          label: edge.protocol,
        },
      });
    });

    // 运行布局
    cy.layout({ name: 'cose', animate: true }).run();
  }, [data]);

  // 高亮选中节点
  useEffect(() => {
    if (!cyRef.current || !selectedNodeId) return;

    const cy = cyRef.current;
    cy.nodes().unselect();
    cy.getElementById(selectedNodeId).select();
  }, [selectedNodeId]);

  return (
    <div
      ref={containerRef}
      className="w-full h-[600px] border border-gray-200 rounded-lg"
    />
  );
}
```

#### 10.4.4 风险矩阵组件

```typescript
// components/charts/RiskMatrix.tsx
import { useMemo } from 'react';
import type { Risk } from '@/features/risks/types';

interface RiskMatrixProps {
  risks: Risk[];
  onCellClick?: (impact: string, feasibility: string) => void;
}

const IMPACT_LEVELS = ['Severe', 'Major', 'Moderate', 'Negligible'];
const FEASIBILITY_LEVELS = ['Very Low', 'Low', 'Medium', 'High'];

const RISK_COLORS = {
  5: 'bg-red-600 text-white',      // Critical
  4: 'bg-orange-500 text-white',   // High
  3: 'bg-yellow-400 text-gray-900', // Medium
  2: 'bg-green-400 text-gray-900', // Low
  1: 'bg-green-600 text-white',    // Negligible
};

export function RiskMatrix({ risks, onCellClick }: RiskMatrixProps) {
  // 计算每个单元格的风险数量
  const cellCounts = useMemo(() => {
    const counts: Record<string, Risk[]> = {};

    risks.forEach((risk) => {
      const key = `${risk.impact_level}-${risk.feasibility_level}`;
      if (!counts[key]) counts[key] = [];
      counts[key].push(risk);
    });

    return counts;
  }, [risks]);

  const getRiskScore = (impact: string, feasibility: string): number => {
    const impactIdx = IMPACT_LEVELS.indexOf(impact);
    const feasibilityIdx = FEASIBILITY_LEVELS.indexOf(feasibility);

    // ISO 21434风险矩阵映射
    const matrix = [
      [2, 3, 4, 5], // Severe
      [1, 2, 3, 4], // Major
      [1, 1, 2, 3], // Moderate
      [1, 1, 1, 1], // Negligible
    ];

    return matrix[impactIdx]?.[feasibilityIdx] || 1;
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="p-2 border bg-gray-100">Impact / Feasibility</th>
            {FEASIBILITY_LEVELS.map((level) => (
              <th key={level} className="p-2 border bg-gray-100 text-center">
                {level}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {IMPACT_LEVELS.map((impact) => (
            <tr key={impact}>
              <td className="p-2 border bg-gray-100 font-medium">{impact}</td>
              {FEASIBILITY_LEVELS.map((feasibility) => {
                const key = `${impact.toLowerCase()}-${feasibility.toLowerCase().replace(' ', '_')}`;
                const cellRisks = cellCounts[key] || [];
                const score = getRiskScore(impact, feasibility);

                return (
                  <td
                    key={key}
                    className={`p-4 border text-center cursor-pointer hover:opacity-80 ${RISK_COLORS[score]}`}
                    onClick={() => onCellClick?.(impact, feasibility)}
                  >
                    <div className="text-lg font-bold">{cellRisks.length}</div>
                    <div className="text-xs opacity-80">
                      Risk Level: {score}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

#### 10.4.5 AI对话组件设计

AI对话组件提供智能问答界面，支持流式响应、上下文关联和引用展示。

##### 组件架构

```mermaid
graph TB
    subgraph "Chat Components"
        CB[ChatButton] -->|点击打开| CP[ChatPanel]
        CP --> CH[ChatHeader]
        CP --> CML[ChatMessageList]
        CP --> CI[ChatInput]

        CML --> CM[ChatMessage]
        CM --> CT[ChatText]
        CM --> CR[ChatReference]
        CM --> CL[ChatLoading]

        CI --> CIN[TextInput]
        CI --> CSB[SendButton]
        CI --> CSS[SuggestionChips]
    end

    subgraph "State Management"
        ZS[Zustand Store]
        ZS --> MS[messages]
        ZS --> SS[streaming]
        ZS --> CS[context]
        ZS --> HS[history]
    end

    subgraph "Hooks"
        UC[useChat]
        US[useSSE]
        UCH[useChatHistory]
    end

    CP --> UC
    UC --> ZS
    UC --> US
    UCH --> HS
```

##### ChatPanel 主面板组件

| 属性 | 类型 | 说明 |
|-----|------|------|
| `isOpen` | `boolean` | 面板是否展开 |
| `onClose` | `() => void` | 关闭回调 |
| `contextType` | `ContextType` | 上下文类型 |
| `contextId` | `string?` | 上下文关联ID |
| `position` | `'right' \| 'bottom'` | 面板位置 |

```mermaid
stateDiagram-v2
    [*] --> Collapsed: 初始状态
    Collapsed --> Expanded: 点击按钮
    Expanded --> Collapsed: 点击关闭

    state Expanded {
        [*] --> Idle
        Idle --> Composing: 输入文字
        Composing --> Sending: 点击发送
        Sending --> Streaming: 收到响应
        Streaming --> Idle: 响应完成
        Streaming --> Error: 连接失败
        Error --> Idle: 重试
    }
```

##### ChatMessage 消息组件

| 属性 | 类型 | 说明 |
|-----|------|------|
| `role` | `'user' \| 'assistant'` | 消息角色 |
| `content` | `string` | 消息内容 |
| `references` | `Reference[]?` | 引用资源列表 |
| `timestamp` | `Date` | 发送时间 |
| `isStreaming` | `boolean` | 是否正在流式输出 |

消息渲染流程：

```mermaid
flowchart LR
    subgraph "消息渲染"
        M[Message] --> R{role}
        R -->|user| UB[用户气泡]
        R -->|assistant| AB[助手气泡]

        AB --> MD[Markdown渲染]
        MD --> HL[代码高亮]
        MD --> RF[引用卡片]
        MD --> TB[表格格式化]
    end
```

##### SSE流式处理Hook

```mermaid
sequenceDiagram
    participant C as Component
    participant H as useSSE Hook
    participant E as EventSource
    participant S as Server

    C->>H: connect(url, body)
    H->>E: new EventSource
    E->>S: POST /api/v1/chat/send

    loop Streaming
        S-->>E: data: {"token": "..."}
        E-->>H: onmessage
        H-->>C: onToken callback
        C->>C: 更新显示
    end

    S-->>E: data: [DONE]
    E-->>H: onmessage
    H->>E: close()
    H-->>C: onComplete callback
```

##### 状态管理 (Zustand Store)

| State | 类型 | 说明 |
|-------|------|------|
| `messages` | `Message[]` | 当前会话消息列表 |
| `isStreaming` | `boolean` | 是否正在接收流 |
| `currentContext` | `ChatContext` | 当前上下文 |
| `sessionId` | `string?` | 会话ID |
| `error` | `Error?` | 错误状态 |

| Action | 参数 | 说明 |
|--------|------|------|
| `addMessage` | `Message` | 添加新消息 |
| `appendToLast` | `string` | 追加到最后一条消息 |
| `setContext` | `ChatContext` | 设置对话上下文 |
| `clearMessages` | - | 清空消息 |
| `setError` | `Error?` | 设置错误状态 |

##### 交互流程

```mermaid
sequenceDiagram
    participant U as User
    participant P as ChatPanel
    participant S as Store
    participant A as API
    participant AI as AI Service

    U->>P: 输入问题
    P->>S: addMessage(userMsg)
    P->>A: POST /chat/send (SSE)

    A->>AI: 调用Qwen模型

    loop Token生成
        AI-->>A: token
        A-->>P: SSE event
        P->>S: appendToLast(token)
        S-->>P: 触发重渲染
    end

    AI-->>A: 引用列表
    A-->>P: references event
    P->>S: updateReferences

    A-->>P: [DONE]
    P->>S: setStreaming(false)
```

##### 快捷建议组件

根据当前上下文动态生成建议问题：

| 上下文类型 | 建议问题示例 |
|-----------|-------------|
| `asset` | "这个资产有哪些潜在威胁？"<br>"如何提高该组件的安全性？" |
| `threat` | "这个威胁的攻击路径是什么？"<br>"有哪些缓解措施？" |
| `risk` | "为什么风险等级是高？"<br>"如何降低这个风险？" |
| `compliance` | "这符合UN R155要求吗？"<br>"需要补充哪些文档？" |

##### 引用卡片组件

```mermaid
flowchart TB
    subgraph "ChatReference"
        RT{引用类型}
        RT -->|asset| AC[AssetCard]
        RT -->|threat| TC[ThreatCard]
        RT -->|document| DC[DocCard]
        RT -->|cve| CC[CVECard]

        AC --> AL[点击跳转资产详情]
        TC --> TL[点击跳转威胁详情]
        DC --> DL[点击打开文档]
        CC --> CL[点击打开CVE链接]
    end
```

| 属性 | 类型 | 说明 |
|-----|------|------|
| `type` | `'asset' \| 'threat' \| 'document' \| 'cve'` | 引用类型 |
| `id` | `string` | 资源ID |
| `title` | `string` | 显示标题 |
| `snippet` | `string?` | 摘要片段 |
| `onClick` | `() => void` | 点击回调 |

### 10.5 页面设计

#### 10.5.1 仪表盘页面

```typescript
// pages/dashboard/DashboardPage.tsx
import { useProjects } from '@/features/projects/hooks';
import { RiskPieChart } from '@/components/charts/RiskPieChart';
import { StrideBarChart } from '@/components/charts/StrideBarChart';
import { Card } from '@/components/ui/Card';

export function DashboardPage() {
  const { data: projects, isLoading } = useProjects();

  if (isLoading) return <LoadingSpinner />;

  const stats = {
    totalProjects: projects?.total || 0,
    activeProjects: projects?.items.filter(p => p.status === 'analyzing').length || 0,
    totalThreats: 0, // 从API获取
    criticalRisks: 0, // 从API获取
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">仪表盘</h1>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="项目总数"
          value={stats.totalProjects}
          icon="folder"
        />
        <StatCard
          title="进行中"
          value={stats.activeProjects}
          icon="play"
          color="blue"
        />
        <StatCard
          title="威胁总数"
          value={stats.totalThreats}
          icon="alert-triangle"
          color="yellow"
        />
        <StatCard
          title="高危风险"
          value={stats.criticalRisks}
          icon="alert-circle"
          color="red"
        />
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="风险等级分布">
          <RiskPieChart />
        </Card>
        <Card title="STRIDE威胁分布">
          <StrideBarChart />
        </Card>
      </div>

      {/* 最近项目列表 */}
      <Card title="最近项目">
        <RecentProjectsTable projects={projects?.items.slice(0, 5) || []} />
      </Card>
    </div>
  );
}
```

### 10.6 状态管理

```typescript
// stores/projectStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ProjectState {
  currentProjectId: string | null;
  recentProjectIds: string[];
  setCurrentProject: (id: string) => void;
  addRecentProject: (id: string) => void;
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set) => ({
      currentProjectId: null,
      recentProjectIds: [],

      setCurrentProject: (id) =>
        set((state) => {
          // 同时添加到最近项目
          const recentIds = [
            id,
            ...state.recentProjectIds.filter((pid) => pid !== id),
          ].slice(0, 10);

          return {
            currentProjectId: id,
            recentProjectIds: recentIds,
          };
        }),

      addRecentProject: (id) =>
        set((state) => ({
          recentProjectIds: [
            id,
            ...state.recentProjectIds.filter((pid) => pid !== id),
          ].slice(0, 10),
        })),
    }),
    {
      name: 'project-storage',
    }
  )
);
```

---

## 11. 部署架构

### 11.1 Docker Compose部署

```mermaid
flowchart TB
    subgraph DockerCompose["Docker Compose"]
        subgraph Frontend["前端容器"]
            Nginx["Nginx<br/>静态文件服务"]
        end

        subgraph Backend["后端容器"]
            API["API服务<br/>FastAPI"]
            Worker["Worker服务<br/>后台任务"]
        end

        subgraph Storage["存储容器"]
            Neo4j["Neo4j<br/>图数据库"]
            Milvus["Milvus<br/>向量数据库"]
            PostgreSQL["PostgreSQL<br/>关系数据库"]
            Redis["Redis<br/>缓存/队列"]
            MinIO["MinIO<br/>文件存储"]
        end
    end

    subgraph External["外部服务"]
        AliyunAI["阿里云百炼<br/>Qwen API"]
    end

    Nginx --> API
    API --> Worker
    API --> Neo4j
    API --> Milvus
    API --> PostgreSQL
    API --> Redis
    API --> MinIO
    Worker --> Neo4j
    Worker --> Milvus
    Worker --> Redis
    Worker --> MinIO
    API --> AliyunAI
    Worker --> AliyunAI

    style DockerCompose fill:#e3f2fd
    style External fill:#f3e5f5
```

### 11.2 Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - api
    networks:
      - aitara-network

  # API服务
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://aitara:aitara@postgres:5432/aitara
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - REDIS_URL=redis://redis:6379/0
      - MILVUS_HOST=milvus
      - MILVUS_PORT=19530
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
    depends_on:
      - postgres
      - neo4j
      - redis
      - milvus
      - minio
    networks:
      - aitara-network
    volumes:
      - ./logs:/app/logs

  # Worker服务 (后台任务处理)
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: python -m aitara.worker
    environment:
      - DATABASE_URL=postgresql://aitara:aitara@postgres:5432/aitara
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - REDIS_URL=redis://redis:6379/0
      - MILVUS_HOST=milvus
      - MILVUS_PORT=19530
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
    depends_on:
      - postgres
      - neo4j
      - redis
      - milvus
      - minio
    networks:
      - aitara-network
    volumes:
      - ./logs:/app/logs

  # PostgreSQL数据库
  postgres:
    image: postgres:16
    environment:
      - POSTGRES_USER=aitara
      - POSTGRES_PASSWORD=aitara
      - POSTGRES_DB=aitara
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - aitara-network

  # Neo4j图数据库
  neo4j:
    image: neo4j:2025.12.1-community
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_memory_heap_initial__size=512m
      - NEO4J_dbms_memory_heap_max__size=2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    networks:
      - aitara-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - aitara-network

  # Milvus向量数据库 (standalone模式)
  etcd:
    image: quay.io/coreos/etcd:v3.5.5
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
    volumes:
      - etcd_data:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd
    networks:
      - aitara-network

  minio-milvus:
    image: minio/minio:latest
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - milvus_minio_data:/data
    command: minio server /data
    networks:
      - aitara-network

  milvus:
    image: milvusdb/milvus:v2.6.9
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio-milvus:9000
    volumes:
      - milvus_data:/var/lib/milvus
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - etcd
      - minio-milvus
    networks:
      - aitara-network

  # MinIO对象存储 (应用文件存储)
  minio:
    image: minio/minio:latest
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    networks:
      - aitara-network

volumes:
  postgres_data:
  neo4j_data:
  neo4j_logs:
  redis_data:
  etcd_data:
  milvus_data:
  milvus_minio_data:
  minio_data:

networks:
  aitara-network:
    driver: bridge
```

### 11.3 服务Dockerfile

#### 11.3.1 后端Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装uv包管理器
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync --frozen --no-dev

# 复制源代码
COPY src/ ./src/

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "aitara.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 11.3.2 前端Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package.json pnpm-lock.yaml ./

# 安装pnpm和依赖
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 构建
RUN pnpm build

# 生产镜像
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 11.3.3 Nginx配置

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # 前端SPA路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 健康检查
    location /health {
        return 200 'OK';
        add_header Content-Type text/plain;
    }
}
```

### 11.4 资源配置建议

| 组件 | CPU | 内存 | 存储 | 说明 |
|-----|-----|------|------|------|
| API服务 | 2核 | 4GB | - | 主业务服务 |
| Worker服务 | 4核 | 8GB | - | AI推理任务 |
| PostgreSQL | 2核 | 4GB | 50GB SSD | 业务数据 |
| Neo4j | 4核 | 8GB | 100GB SSD | 知识图谱 |
| Milvus | 4核 | 8GB | 200GB SSD | 向量检索 |
| Redis | 1核 | 2GB | 10GB | 缓存/队列 |
| MinIO | 1核 | 1GB | 100GB | 文件存储 |

**最低配置要求**: 16核CPU, 32GB内存, 500GB SSD

### 11.5 启动与管理

```bash
# 环境变量配置
cp .env.example .env
# 编辑 .env 文件，配置 DASHSCOPE_API_KEY 等

# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f api
docker compose logs -f worker

# 停止服务
docker compose down

# 停止并删除数据卷
docker compose down -v

# 重新构建
docker compose build --no-cache
docker compose up -d
```

### 11.6 数据备份

```bash
# PostgreSQL备份
docker compose exec postgres pg_dump -U aitara aitara > backup_postgres_$(date +%Y%m%d).sql

# Neo4j备份
docker compose exec neo4j neo4j-admin database dump neo4j --to-path=/backups

# MinIO备份 (使用mc客户端)
mc mirror minio/assets ./backup_minio/assets
mc mirror minio/reports ./backup_minio/reports
```

---

## 附录

### A. 参考标准与法规

| 标准/法规 | 全称 | 说明 |
|----------|------|-----|
| ISO/SAE 21434 | Road vehicles — Cybersecurity engineering | 汽车网络安全工程标准 |
| UN R155 | Uniform provisions concerning the approval of vehicles with regards to cyber security | 联合国车辆网络安全法规 |
| UN R156 | Software update and software update management systems | 软件更新管理法规 |
| ISO 26262 | Functional Safety | 功能安全标准 |
| MITRE ATT&CK for Vehicle | - | 汽车攻击矩阵 |

### B. 威胁知识库来源

1. **NVD (CVE Database)** - 美国国家漏洞数据库
2. **MITRE ATT&CK for Automotive** - 汽车攻击矩阵
3. **UN R155 Annex 5** - 威胁与缓解措施目录

### C. 技术版本汇总

| 组件 | 版本 | 更新日期 |
|-----|------|---------|
| Python | 3.12+ | - |
| FastAPI | 0.128.0 | 2026-01 |
| Pydantic | 2.12.5 | 2026-01 |
| structlog | 25.5.0 | 2025 |
| React | 19.2.4 | 2026-01-26 |
| TypeScript | 5.9 | 2026-01 |
| Vite | 7.3.1 | 2026-01 |
| Tailwind CSS | 4.1.18 | 2025-12 |
| Neo4j | 2025.12.1 | 2025-12 |
| Neo4j Python Driver | 6.1.0 | 2026-01-12 |
| Milvus | 2.6.9 | 2026-01 |
| uv | 0.9.27 | 2026-01-26 |
| Qwen3-VL | Latest | 2025-11 |
| Qwen-Max | 2026-01-23 | 2026-01-23 |
| text-embedding-v3 | Latest | - |

### D. 词汇表

| 英文 | 中文 | 说明 |
|-----|------|-----|
| TARA | 威胁分析与风险评估 | Threat Analysis and Risk Assessment |
| IVI | 车载信息娱乐系统 | In-Vehicle Infotainment |
| T-BOX | 远程信息处理器 | Telematics Box |
| ECU | 电子控制单元 | Electronic Control Unit |
| CAN | 控制器局域网 | Controller Area Network |
| E/E Architecture | 电子电气架构 | Electrical/Electronic Architecture |
| SDV | 软件定义汽车 | Software Defined Vehicle |
| CSMS | 网络安全管理体系 | Cyber Security Management System |
| FOTA | 固件空中升级 | Firmware Over-The-Air |
| PKI | 公钥基础设施 | Public Key Infrastructure |

---

**文档版本历史**

| 版本 | 日期 | 作者 | 变更说明 |
|-----|------|------|---------|
| 1.0.0 | 2026-01-29 | AI TARA Team | 初始版本 |

---

*本文档基于 [specs/tara-deepresearch.md](./tara-deepresearch.md) 研究报告生成*
