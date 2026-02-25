"""
Configurações declarativas dos padrões arquiteturais.
"""

from .models import PatternConfig

# ─── Padrões Pragmáticos ──────────────────────────────────────────────────────

SIMPLE_MODULAR = PatternConfig(
    name="Simple Modular Structure",
    description="Estrutura modular simples e pragmática (src, utils, lib)",
    dir_weights={
        "src": 0.3,
        "utils": 0.15,
        "lib": 0.15,
        "helpers": 0.1,
        "config": 0.1,
        "common": 0.1,
        "shared": 0.1,
        "core": 0.15,
    },
    threshold=0.3,
)

FEATURE_BASED = PatternConfig(
    name="Feature-Based Architecture",
    description="Organização por features/módulos funcionais",
    dir_weights={
        "features": 0.5,
        "modules": 0.5,
        "packages": 0.4,
        "apps": 0.4,
    },
    threshold=0.3,
)

BASIC_LAYERED = PatternConfig(
    name="Basic Layered Architecture",
    description="Separação em camadas básicas (services, models, routes)",
    dir_weights={
        "routes": 0.2,
        "api": 0.2,
        "services": 0.25,
        "models": 0.2,
        "database": 0.15,
        "db": 0.15,
        "middleware": 0.1,
        "validators": 0.1,
        "schemas": 0.1,
    },
    file_keywords=["service", "model", "route", "controller"],
    min_dir_matches=2,
    threshold=0.3,
)

FRONTEND_STANDARD = PatternConfig(
    name="Frontend Standard Structure",
    description="Estrutura padrão de projeto frontend",
    dir_weights={
        "components": 0.3,
        "pages": 0.25,
        "views": 0.25,
        "hooks": 0.15,
        "styles": 0.1,
        "assets": 0.1,
        "public": 0.1,
        "static": 0.1,
        "store": 0.15,
        "redux": 0.15,
        "context": 0.1,
    },
    file_keywords=[".jsx", ".tsx", ".vue", ".svelte", "component", ".css", ".scss", ".sass"],
    threshold=0.3,
)

BACKEND_STANDARD = PatternConfig(
    name="Backend Standard Structure",
    description="Estrutura padrão de projeto backend",
    dir_weights={
        "controllers": 0.25,
        "routes": 0.25,
        "api": 0.2,
        "models": 0.2,
        "middleware": 0.15,
        "database": 0.15,
        "migrations": 0.1,
        "seeders": 0.05,
        "validators": 0.1,
        "auth": 0.1,
    },
    file_keywords=["server", "app.py", "main.py", "index.js", "app.js"],
    min_dir_matches=2,
    threshold=0.3,
)

# ─── Padrões Arquiteturais Formais ────────────────────────────────────────────

MVC = PatternConfig(
    name="MVC (Model-View-Controller)",
    description="Separação clara entre Model, View e Controller",
    dir_weights={
        "models": 0.2,
        "views": 0.2,
        "controllers": 0.2,
        "model": 0.2,
        "view": 0.2,
        "controller": 0.2,
    },
    file_keywords=["controller", "model", "view"],
    min_dir_matches=2,
    threshold=0.3,
)

CLEAN_ARCHITECTURE = PatternConfig(
    name="Clean Architecture",
    description="Camadas com dependências unidirecionais",
    dir_weights={
        "domain": 0.25,
        "application": 0.25,
        "infrastructure": 0.25,
        "presentation": 0.15,
        "entities": 0.2,
        "usecases": 0.25,
        "use_cases": 0.25,
    },
    file_keywords=["interface", "port", "adapter", "gateway", "boundary"],
    min_dir_matches=3,
    threshold=0.3,
)

DDD = PatternConfig(
    name="Domain-Driven Design (DDD)",
    description="Organização por domínios de negócio",
    dir_weights={
        "domain": 0.3,
        "entities": 0.2,
        "valueobjects": 0.2,
        "value_objects": 0.2,
        "aggregates": 0.2,
        "repositories": 0.1,
        "services": 0.1,
        "factories": 0.1,
    },
    file_keywords=["entity", "valueobject", "aggregate", "domainservice", "specification"],
    min_dir_matches=3,
    threshold=0.3,
)

HEXAGONAL = PatternConfig(
    name="Hexagonal Architecture (Ports & Adapters)",
    description="Arquitetura de portas e adaptadores",
    dir_weights={
        "ports": 0.4,
        "adapters": 0.4,
        "inbound": 0.2,
        "outbound": 0.2,
        "primary": 0.2,
        "secondary": 0.2,
    },
    file_keywords=["port", "adapter", "inbound", "outbound"],
    min_dir_matches=2,
    threshold=0.3,
)

# ─── Padrões Estruturais ──────────────────────────────────────────────────────

MICROSERVICES = PatternConfig(
    name="Microservices",
    description="Serviços independentes e desacoplados",
    dir_weights={},   # lógica customizada no detector
    threshold=0.3,
)

REPOSITORY_PATTERN = PatternConfig(
    name="Repository Pattern",
    description="Abstração da camada de dados",
    dir_weights={},   # lógica baseada em file_names
    file_keywords=["repository", "irepository", "repository_interface", "repositoryinterface", "base_repository"],
    threshold=0.3,
)

EVENT_DRIVEN = PatternConfig(
    name="Event-Driven Architecture",
    description="Comunicação via eventos assíncronos",
    dir_weights={},   # lógica customizada
    file_keywords=["event", "handler", "listener", "subscriber", "publisher", "consumer"],
    threshold=0.3,
)

MONOREPO = PatternConfig(
    name="Monorepo Structure",
    description="Múltiplos projetos em um único repositório",
    dir_weights={
        "packages": 0.5,
        "apps": 0.5,
        "libs": 0.4,
        "services": 0.3,
        "projects": 0.3,
    },
    threshold=0.3,
)

# ─── Configurações de Frameworks ──────────────────────────────────────────────

FRAMEWORK_INDICATORS: dict[str, dict[str, list[str]]] = {
    "frontend": {
        "Next.js":  ["next.config", "next-env"],
        "Nuxt.js":  ["nuxt.config"],
        "Vue.js":   ["vue.config", ".vue"],
        "Angular":  ["angular.json"],
        "React":    [".jsx", ".tsx"],
        "Svelte":   ["svelte.config"],
    },
    "backend": {
        "Express.js":   ["express"],
        "FastAPI":      ["fastapi"],
        "Django":       ["django", "manage.py"],
        "Flask":        ["flask"],
        "NestJS":       ["nestjs", "nest-cli"],
        "Spring Boot":  ["spring", "application.properties"],
    },
    "database": {
        "Prisma":       ["prisma"],
        "TypeORM":      ["typeorm"],
        "Sequelize":    ["sequelize"],
        "Mongoose":     ["mongoose"],
        "SQLAlchemy":   ["sqlalchemy"],
    },
    "testing": {
        "Jest":     ["jest.config", "jest"],
        "Pytest":   ["pytest", "pytest.ini"],
        "Vitest":   ["vitest"],
        "Cypress":  ["cypress"],
    },
    "deployment": {
        "Docker":       ["docker"],
        "Kubernetes":   ["kubernetes", "k8s"],
        "Terraform":    ["terraform"],
        "Vercel":       ["vercel.json"],
        "Netlify":      ["netlify"],
    },
}

# ─── Recomendações por Padrão ─────────────────────────────────────────────────

PATTERN_RECOMMENDATIONS: dict[str, list[str]] = {
    "Simple Modular": [
        "✓ Estrutura simples e pragmática. Considere adicionar camadas conforme o projeto cresce.",
    ],
    "Repository": [
        "✓ Repository Pattern detectado. Considere adicionar Unit of Work se ainda não houver.",
    ],
    "DDD": [
        "✓ DDD detectado. Garanta que bounded contexts estejam bem definidos.",
        "✓ Considere usar Value Objects para conceitos de domínio imutáveis.",
    ],
    "Clean Architecture": [
        "✓ Clean Architecture bem estruturada. Mantenha dependências apontando para o domínio.",
    ],
    "Microservices": [
        "✓ Arquitetura de microserviços. Garanta observabilidade e resiliência.",
        "✓ Considere implementar circuit breakers e service mesh.",
    ],
    "Frontend Standard": [
        "✓ Estrutura frontend organizada. Considere adicionar state management se necessário.",
    ],
    "Backend Standard": [
        "✓ Backend estruturado. Considere adicionar validação e tratamento de erros robusto.",
    ],
    "Feature-Based": [
        "✓ Organização por features facilita escalabilidade. Evite dependências circulares entre features.",
    ],
    "Event-Driven": [
        "✓ Arquitetura event-driven. Implemente idempotência nos handlers de eventos.",
        "✓ Considere dead letter queues para eventos com falha.",
    ],
}
