# CLAUDE.md - AI TARA Platform Development Constitution

This document defines the coding standards, architectural principles, and development practices for the AI TARA (Threat Analysis and Risk Assessment) platform.

## Project Overview

An intelligent automotive cybersecurity platform implementing automated TARA based on ISO/SAE 21434 and UN R155 regulations. The platform leverages graph databases and multi-modal AI to analyze threats for IVI (In-Vehicle Infotainment) and T-BOX (Telematics Control Unit) systems.

---

## Tech Stack

### Backend
- **Language**: Python 3.12+
- **Package Manager**: uv
- **Framework**: FastAPI
- **Database**: Neo4j (Graph Database)
- **AI Models** (Alibaba Cloud Bailian):
  - Qwen-VL-Max: Multi-modal vision-language model
  - Qwen-Max: Advanced LLM for reasoning
  - Qwen-Embedding / text-embedding-v3: RAG retrieval
- **Vector Database**: Milvus

### Frontend
- **Framework**: React 18+
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Language**: TypeScript

---

## Design Principles

### SOLID Principles

#### Single Responsibility Principle (SRP)
```python
# Good: Each class has one responsibility
class ThreatGenerator:
    """Generates threat scenarios based on assets."""
    def generate(self, asset: Asset) -> list[Threat]: ...

class RiskCalculator:
    """Calculates risk scores from threats."""
    def calculate(self, threat: Threat) -> RiskScore: ...

# Bad: Mixed responsibilities
class ThreatAnalyzer:
    def generate_threats(self): ...
    def calculate_risk(self): ...
    def save_to_database(self): ...
    def send_notification(self): ...
```

#### Open/Closed Principle (OCP)
```python
# Good: Open for extension, closed for modification
class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: bytes) -> ParsedResult: ...

class VisioParser(BaseParser):
    def parse(self, content: bytes) -> ParsedResult: ...

class PDFParser(BaseParser):
    def parse(self, content: bytes) -> ParsedResult: ...
```

#### Liskov Substitution Principle (LSP)
```python
# Subtypes must be substitutable for their base types
class Asset(ABC):
    @abstractmethod
    def get_security_properties(self) -> SecurityProperties: ...

class HardwareAsset(Asset):
    def get_security_properties(self) -> SecurityProperties:
        # Must return valid SecurityProperties, not raise or return None
        return SecurityProperties(...)
```

#### Interface Segregation Principle (ISP)
```python
# Good: Specific interfaces
class Parseable(Protocol):
    def parse(self) -> dict: ...

class Validatable(Protocol):
    def validate(self) -> bool: ...

# Bad: Fat interface
class DocumentProcessor(Protocol):
    def parse(self) -> dict: ...
    def validate(self) -> bool: ...
    def render(self) -> bytes: ...
    def compress(self) -> bytes: ...
```

#### Dependency Inversion Principle (DIP)
```python
# Good: Depend on abstractions
class ThreatService:
    def __init__(self, repository: ThreatRepository):
        self._repository = repository

# Bad: Depend on concretions
class ThreatService:
    def __init__(self):
        self._repository = Neo4jThreatRepository()
```

### DRY (Don't Repeat Yourself)
- Extract common logic into utility functions or base classes
- Use configuration files for repeated values
- Create shared types and schemas

### KISS (Keep It Simple, Stupid)
- Prefer straightforward solutions over clever ones
- Avoid premature optimization
- Write code that is easy to read and understand

### YAGNI (You Aren't Gonna Need It)
- Only implement features when they are actually needed
- Avoid speculative generality
- Remove unused code promptly

---

## Error Handling

**Non-negotiable: All errors must be explicitly handled.**

### Backend Error Handling

#### Custom Exception Hierarchy
```python
# core/exceptions.py
class AITARAError(Exception):
    """Base exception for all AITARA errors."""
    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code
        super().__init__(message)

class ValidationError(AITARAError):
    """Input validation failed."""
    pass

class NotFoundError(AITARAError):
    """Resource not found."""
    pass

class ExternalServiceError(AITARAError):
    """External service (Qwen API, Neo4j) failed."""
    pass

class ParsingError(AITARAError):
    """File parsing failed."""
    pass
```

#### FastAPI Exception Handlers
```python
# api/deps.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(AITARAError)
async def aitara_exception_handler(request: Request, exc: AITARAError):
    return JSONResponse(
        status_code=400,
        content={"error": exc.code, "message": exc.message}
    )

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "NOT_FOUND", "message": exc.message}
    )
```

#### Result Pattern for Operations
```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E

Result = Ok[T] | Err[E]

# Usage
def parse_bom(content: bytes) -> Result[BOMData, ParsingError]:
    try:
        data = _parse_internal(content)
        return Ok(data)
    except Exception as e:
        return Err(ParsingError(f"Failed to parse BOM: {e}"))
```

### Frontend Error Handling

```typescript
// services/api.ts
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

async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.json();
    throw new ApiError(error.code, error.message, response.status);
  }

  return response.json();
}

// Component usage with error boundary
function AssetList() {
  const { data, error, isLoading } = useQuery(['assets'], fetchAssets);

  if (error) {
    return <ErrorDisplay error={error} />;
  }

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return <AssetTable assets={data} />;
}
```

---

## Logging

### Backend Logging (structlog)

```python
# config/logging.py
import structlog

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Usage
logger = structlog.get_logger(__name__)

async def analyze_asset(asset_id: str):
    logger.info("starting_asset_analysis", asset_id=asset_id)
    try:
        result = await _perform_analysis(asset_id)
        logger.info("asset_analysis_completed", asset_id=asset_id, threats_found=len(result.threats))
        return result
    except Exception as e:
        logger.error("asset_analysis_failed", asset_id=asset_id, error=str(e), exc_info=True)
        raise
```

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational events
- **WARNING**: Unexpected but handled situations
- **ERROR**: Errors that need attention
- **CRITICAL**: System failures

---

## Concurrency

### Backend (asyncio)

```python
# Async database operations
class Neo4jRepository:
    async def find_attack_paths(
        self,
        source: str,
        target: str
    ) -> list[AttackPath]:
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH path = shortestPath((s:Interface {id: $source})-[*]->(t:Function {id: $target}))
                RETURN path
                """,
                source=source,
                target=target
            )
            return [self._map_path(record) async for record in result]

# Concurrent AI calls
async def analyze_multiple_assets(assets: list[Asset]) -> list[AnalysisResult]:
    tasks = [analyze_single_asset(asset) for asset in assets]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### Frontend (React)

```typescript
// Use React Query for data fetching with automatic caching and deduplication
const { data, isLoading, error } = useQuery({
  queryKey: ['threats', assetId],
  queryFn: () => fetchThreats(assetId),
  staleTime: 5 * 60 * 1000, // 5 minutes
});

// Optimistic updates for mutations
const mutation = useMutation({
  mutationFn: updateThreat,
  onMutate: async (newThreat) => {
    await queryClient.cancelQueries({ queryKey: ['threats'] });
    const previous = queryClient.getQueryData(['threats']);
    queryClient.setQueryData(['threats'], (old) => [...old, newThreat]);
    return { previous };
  },
  onError: (err, newThreat, context) => {
    queryClient.setQueryData(['threats'], context.previous);
  },
});
```

---

## API Design

### RESTful Conventions

```python
# api/v1/threats.py
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/threats", tags=["threats"])

@router.get("/", response_model=list[ThreatResponse])
async def list_threats(
    asset_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
    service: ThreatService = Depends(get_threat_service)
) -> list[ThreatResponse]:
    """List all threats, optionally filtered by asset."""
    return await service.list_threats(asset_id=asset_id, skip=skip, limit=limit)

@router.get("/{threat_id}", response_model=ThreatResponse)
async def get_threat(
    threat_id: str,
    service: ThreatService = Depends(get_threat_service)
) -> ThreatResponse:
    """Get a specific threat by ID."""
    threat = await service.get_threat(threat_id)
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    return threat

@router.post("/", response_model=ThreatResponse, status_code=status.HTTP_201_CREATED)
async def create_threat(
    request: ThreatCreateRequest,
    service: ThreatService = Depends(get_threat_service)
) -> ThreatResponse:
    """Create a new threat."""
    return await service.create_threat(request)
```

### Response Models (Pydantic)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"

class ThreatResponse(BaseModel):
    id: str
    asset_id: str
    description: str
    stride_category: str
    impact_rating: str
    feasibility_rating: str
    risk_level: RiskLevel
    created_at: datetime

    model_config = {"from_attributes": True}
```

---

## Testing

### Backend Tests (pytest)

```python
# tests/unit/test_risk_calculator.py
import pytest
from aitara.domain.services.risk_service import RiskCalculator

class TestRiskCalculator:
    def test_high_impact_high_feasibility_returns_critical(self):
        calculator = RiskCalculator()
        result = calculator.calculate(
            impact="severe",
            feasibility="high"
        )
        assert result.level == RiskLevel.CRITICAL
        assert result.score == 5

    def test_negligible_impact_returns_low_risk(self):
        calculator = RiskCalculator()
        result = calculator.calculate(
            impact="negligible",
            feasibility="high"
        )
        assert result.level == RiskLevel.LOW

# tests/integration/test_threat_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_threat(client: AsyncClient, test_asset):
    response = await client.post(
        "/api/v1/threats/",
        json={
            "asset_id": test_asset.id,
            "description": "Test threat",
            "stride_category": "spoofing"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["asset_id"] == test_asset.id
```

### Frontend Tests (Vitest + React Testing Library)

```typescript
// tests/components/ThreatCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ThreatCard } from '@/components/threats/ThreatCard';

describe('ThreatCard', () => {
  it('displays threat information correctly', () => {
    const threat = {
      id: '1',
      description: 'SQL Injection vulnerability',
      riskLevel: 'high',
    };

    render(<ThreatCard threat={threat} />);

    expect(screen.getByText('SQL Injection vulnerability')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toHaveClass('text-red-600');
  });
});
```

---

## Git & Version Control

### Conventional Commits

**Format**: `<type>(<scope>): <subject>`

#### Types
| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, semicolons, etc.) |
| `refactor` | Code refactoring (no feature/fix) |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `build` | Build system or dependencies |
| `ci` | CI/CD configuration |
| `chore` | Other maintenance tasks |

#### Scope (optional)
- `api` - Backend API changes
- `ui` - Frontend UI changes
- `db` - Database changes
- `ai` - AI/ML related changes
- `parser` - File parser changes
- `auth` - Authentication changes

#### Examples
```
feat(api): add threat generation endpoint
fix(parser): handle malformed BOM files gracefully
docs: update API documentation for v1
refactor(ui): extract ThreatCard into separate component
test(api): add integration tests for asset endpoints
build(deps): upgrade fastapi to 0.110.0
ci: add automated security scanning
```

### Branch Naming
```
feature/<ticket-id>-<short-description>
bugfix/<ticket-id>-<short-description>
hotfix/<ticket-id>-<short-description>
```

### Pull Request Guidelines
1. Reference related issues
2. Provide clear description of changes
3. Include test coverage for new features
4. Ensure CI passes before merge
5. Request review from at least one team member

---

## Security Guidelines

### Input Validation
```python
from pydantic import BaseModel, Field, validator

class AssetCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    asset_type: AssetType

    @validator('name')
    def sanitize_name(cls, v):
        # Prevent injection attacks
        if any(char in v for char in ['<', '>', '&', '"', "'"]):
            raise ValueError('Invalid characters in name')
        return v.strip()
```

### Secrets Management
- Never commit secrets to version control
- Use environment variables for configuration
- Use `.env` files for local development (add to `.gitignore`)

### API Security
- Implement rate limiting
- Use HTTPS in production
- Validate and sanitize all inputs
- Implement proper authentication/authorization

---

## Performance Guidelines

### Database Queries
- Use indexes for frequently queried fields
- Paginate large result sets
- Use connection pooling
- Profile slow queries

### API Response Times
- Target < 200ms for simple queries
- Use caching for expensive operations
- Implement proper pagination

### Frontend
- Lazy load components and routes
- Optimize bundle size
- Use React.memo for expensive components
- Implement virtual scrolling for large lists

---

## Documentation

### Code Comments
- Write self-documenting code; add comments only when necessary
- Document "why", not "what"
- Keep comments up-to-date with code changes

### API Documentation
- Use OpenAPI/Swagger for API documentation
- Include request/response examples
- Document error responses

### Type Hints
```python
# Always use type hints for function signatures
async def analyze_threats(
    asset: Asset,
    config: AnalysisConfig | None = None
) -> list[Threat]:
    ...
```

```typescript
// Always use TypeScript types
interface ThreatAnalysisResult {
  threats: Threat[];
  riskScore: number;
  analyzedAt: Date;
}

function analyzeThreats(asset: Asset): Promise<ThreatAnalysisResult> {
  // ...
}
```
