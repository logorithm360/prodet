# Business OS — Architecture & Design Patterns

> Reference document. Read this before adding any new module or core capability.
> Principle: **commit to the interface now, keep the implementation minimal until it needs to grow.**

---

## 1. Vision

A single platform ("Business OS") that serves many kinds of businesses (retail, school,
factory, etc.) by enabling only the modules each tenant needs. Same core, different
modules, different configuration — not a separate codebase per customer.

This is a **modular monolith**, not microservices. It's designed so individual modules
*could* be extracted into services later, but we don't pay that operational cost until
there's a real reason to.

---

## 2. Layered structure

```
Client Applications (Web / API / VS Code extension / etc.)
            │
      API / Gateway Layer (FastAPI)
            │
        Platform Core   ← never depends on any module
            │
   ┌────────┴────────┐
Shared Services    Business Modules
   └────────┬────────┘
       Event Bus / Interfaces
            │
      PostgreSQL + Cache + Storage
```

- **Platform Core**: auth, organizations, users, permissions, event bus, module
  registry, config, database session, security. Knows nothing about business logic.
- **Shared Services**: capabilities any module can call — AI, email, file storage,
  search, reports. Infrastructure, not business rules.
- **Business Modules**: inventory, CRM, HR, accounting, etc. Each is independent,
  owns its own data and logic, and never imports another module directly.

---

## 3. Folder structure (current, minimal)

```
backend/
├── core/
│   ├── app.py          # creates FastAPI app, registers modules
│   ├── events.py        # in-process event bus
│   ├── registry.py      # Manifest dataclass + register()
│   ├── database.py      # SQLAlchemy base, TenantMixin
│   └── config.py        # env-based settings
│
├── modules/
│   └── <module_name>/
│       ├── manifest.py   # declares name, router, prefix, dependencies
│       ├── models.py     # SQLAlchemy models (inherit TenantMixin)
│       ├── router.py     # FastAPI APIRouter (HTTP layer only)
│       ├── service.py    # business logic
│       └── events.py     # emits domain events via core.events.emit
│
├── main.py
└── requirements.txt
```

No DDD-style `api/application/domain/infrastructure` split yet. One
`router.py` + `service.py` + `models.py` per module is enough until a module's
complexity genuinely demands more layers. Don't add layers speculatively.

---

## 4. Core design patterns

### 4.1 Event-driven communication (no direct module imports)

**Rule:** modules never call another module's service functions directly.
They `emit()` a named event; other modules `on()` subscribe if they care.

```python
# core/events.py
_handlers = defaultdict(list)

def on(event_name: str):
    def decorator(fn):
        _handlers[event_name].append(fn)
        return fn
    return decorator

def emit(event_name: str, **payload):
    for fn in _handlers[event_name]:
        fn(**payload)
```

Why: keeps modules decoupled so one can be modified, replaced, or later
extracted into its own service without touching others. The in-process
implementation above is intentionally trivial — swap it for Redis/RabbitMQ
pub-sub later without changing any module code, since modules only ever know
about `emit`/`on`.

**Naming convention:** `past_tense_event`, e.g. `stock_updated`,
`invoice_created`, `user_registered`. Payload is passed as keyword args, not
a raw dict, so signatures stay explicit.

### 4.2 Manifest-based module registration

Every module exposes a `manifest.py` describing itself:

```python
@dataclass
class Manifest:
    name: str
    router: object
    prefix: str
    dependencies: list = field(default_factory=list)
```

`core/app.py` imports each module's manifest explicitly and registers it:

```python
for manifest in [inventory_manifest, crm_manifest]:
    register(app, manifest)
```

Why: gives every module the same registration shape from day one. Adding a
module later = write its manifest + add one line — no risk of guessing wrong
on dynamic filesystem discovery before it's needed. Automatic discovery can
replace this list later without changing individual modules.

### 4.3 Multi-tenancy via `tenant_id`

```python
class TenantMixin:
    tenant_id = Column(Integer, nullable=False, index=True)
```

Every module's models inherit `TenantMixin`. Every query is scoped by
`tenant_id` from request context. Chosen over schema-per-tenant or
database-per-tenant for simplicity; revisit only for very large enterprise
customers with strict isolation requirements.

### 4.4 Configuration over customization

Customer differences are handled through **settings and feature flags**, not
forked code or one-off customer branches.

```
Inventory settings:
  ✓ barcode
  ✓ auto_reorder
  ✗ serial_numbers
```

Same module, different behavior per tenant. Never let one customer's request
turn into a code fork.

### 4.5 AI as a shared service, not a module

AI is called by modules (`ai_service.summarize(...)`), it does not own
business logic or live inside a specific module. Keeps AI capability reusable
across CRM, inventory, HR, reporting, etc.

---

## 5. What NOT to build yet

These are real infrastructure investments — expensive to build and easy to
get wrong before real usage tells you the right shape. Defer until there's
concrete pain:

- Dynamic module discovery / dependency version resolution
- Distributed event bus (Redis/RabbitMQ) — in-process `emit`/`on` is enough
- Workflow engine / workflow DSL
- Feature-flag admin UI
- Schema-per-tenant or database-per-tenant isolation
- DDD-style layered folders inside modules

Build the simple version first. Upgrade only when a second module or a real
customer creates friction that the simple version can't handle.

---

## 6. Adding a new module — checklist

1. `mkdir modules/<name>` with `manifest.py`, `models.py`, `router.py`,
   `service.py`, `events.py`.
2. Models inherit `TenantMixin`.
3. Business logic lives in `service.py`; `router.py` stays thin (HTTP only).
4. If this module needs to react to another module's activity, subscribe via
   `core.events.on(...)` — never import the other module's service directly.
5. If this module changes state other modules might care about, `emit()` a
   named, past-tense event.
6. Add the manifest to the registration list in `core/app.py`.
7. Any customer-specific behavior → a setting/feature flag, not a branch.

---

## 7. Design principles (summary)

1. **Platform first** — reusable operating system, not one-off apps.
2. **Modular by default** — every business capability is an independent package.
3. **Configuration over customization** — settings/flags/workflows, not forked code.
4. **Event-driven communication** — modules never import each other directly.
5. **Strong tenant isolation** — every organization's data stays separate.
6. **Domain ownership** — each module owns its data, rules, API, permissions.
7. **Shared infrastructure** — AI, storage, notifications, reports are platform
   services consumed by modules, not reimplemented per module.
8. **Evolutionary architecture** — start as a modular monolith; extract a
   module into a microservice only when there's clear operational need, made
   possible by the fact that modules already talk through events/interfaces.