# Business OS Foundation Specification

**Version:** 1.0.0
**Status:** Draft
**Last Updated:** August 2026

---

# 1. Purpose

This document defines the architectural foundation of the Business Operating System (Business OS).

It is the single source of truth for the platform's architecture, design principles, coding conventions, module contracts, and long-term vision.

Every architectural decision must be consistent with this document.

If implementation and this document disagree, this document takes precedence until intentionally revised.

---

# 2. Vision

Business OS is a modular, multi-tenant platform designed to support many different business domains while maintaining a single consistent architecture.

The goal is not to build a single ERP system.

The goal is to build a platform capable of hosting many independent business modules.

Examples include:

- Inventory
- Sales
- CRM
- HR
- Payroll
- Accounting
- Manufacturing
- POS
- Reporting
- AI Assistants

Every business shares the same platform.

Only enabled modules differ.

---

# 3. Long-Term Goals

The platform should always prioritize:

- Simplicity
- Maintainability
- Extensibility
- Security
- Scalability
- Consistency
- Testability

Architecture decisions should never optimize for short-term convenience if they compromise these goals.

---

# 4. Core Architectural Principles

## Principle 1

Core must never contain business logic.

Core only provides platform services.

Examples:

- Authentication
- Authorization
- Configuration
- Event Bus
- Registry
- Database
- Logging
- Security
- Settings

Never:

- Inventory
- HR
- Payroll
- CRM

---

## Principle 2

Modules own business logic.

Every business rule belongs to exactly one module.

No module modifies another module's business logic.

---

## Principle 3

Modules never communicate directly.

Allowed:

Module A

↓

Event

↓

Module B

Not:

Module A

↓

Import Module B

---

## Principle 4

Configuration is preferred over customization.

Customer-specific code should never exist.

Business differences must be implemented using:

- Settings
- Feature Flags
- Workflows
- Permissions
- Templates

---

## Principle 5

Every resource belongs to one tenant.

Every database record must contain:

tenant_id

Tenant isolation is mandatory.

---

## Principle 6

Shared functionality belongs inside Shared.

Never inside business modules.

---

## Principle 7

Business logic never belongs inside routers.

Routers only:

- Validate
- Authorize
- Call services
- Return responses

---

## Principle 8

Replace implementations, not interfaces.

Interfaces should remain stable.

Implementations may evolve.

Example:

emit()

Today:

In-process

Future:

RabbitMQ

No module changes.

---

## Principle 9

Every module exposes one manifest.

Every module follows the same registration contract.

---

## Principle 10

Architecture evolves gradually.

Infrastructure should remain lightweight until complexity is justified.

Commit to interfaces early.

Delay heavyweight implementations.

---

# 5. Architecture Style

The platform follows a Modular Monolith architecture.

High-level structure:

Business OS

↓

Platform Core

↓

Shared Services

↓

Business Modules

↓

Infrastructure

The application is deployed as one system while maintaining clear module boundaries.

Microservices are not part of Version 1.

---

# 6. Design Patterns

The platform uses the following design patterns.

## Architectural Patterns

- Modular Monolith
- Domain-Driven Design (Gradual Adoption)
- Clean Architecture
- Hexagonal Architecture

---

## Behavioral Patterns

- Event Bus
- Observer
- Strategy
- State
- Chain of Responsibility

---

## Structural Patterns

- Repository
- Adapter
- Facade
- Decorator
- Factory
- Builder

---

## Platform Patterns

- Plugin Pattern
- Manifest Pattern
- Feature Toggle Pattern
- Multi-Tenant Pattern
- Configuration over Customization

---

# 7. Platform Layers

Presentation

↓

API

↓

Application

↓

Domain

↓

Infrastructure

↓

Database

Business rules never depend on infrastructure.

Infrastructure depends on business rules.

---

# 8. Folder Structure

backend/

core/

shared/

modules/

tests/

docs/

main.py

---

# 9. Core Responsibilities

Core provides:

Authentication

Authorization

Configuration

Database

Logging

Registry

Event Bus

Application Factory

Security

Settings

Core must never contain business logic.

---

# 10. Shared Responsibilities

Shared contains reusable code.

Examples:

- Base classes
- Exceptions
- Utilities
- Validators
- Schemas
- Types
- Constants
- Enums

Shared must never depend on modules.

---

# 11. Module Responsibilities

Each module owns:

Routes

Services

Models

Events

Permissions

Configuration

Tests

Each module exposes:

manifest.py

---

# 12. Module Contract

Every module must provide:

manifest.py

router.py

service.py

models.py

events.py

Future modules may include:

permissions.py

schemas.py

repositories.py

tests/

---

# 13. Module Lifecycle

Install

↓

Register

↓

Configure

↓

Initialize

↓

Run

↓

Shutdown

---

# 14. Event Contract

Events represent completed business actions.

Examples:

stock_updated

invoice_created

employee_hired

customer_registered

Events must:

- Be immutable
- Be descriptive
- Include tenant context
- Include timestamps
- Avoid implementation details

Modules emit events.

Modules subscribe to events.

Modules never call each other directly.

---

# 15. Manifest Contract

Every module exposes a manifest describing:

- Name
- Version
- Description
- Router
- Dependencies
- Permissions
- Settings

Future additions may include:

- Scheduled Jobs
- Migrations
- CLI Commands

---

# 16. Tenant Convention

Every request belongs to one tenant.

Every model contains:

tenant_id

Every query filters by:

tenant_id

Cross-tenant access is forbidden.

---

# 17. Coding Standards

Naming:

Modules:

inventory

sales

crm

Routes:

/api/inventory

/api/hr

Services:

InventoryService

Repositories:

InventoryRepository

Events:

stock_updated

invoice_paid

Permissions:

inventory.read

inventory.write

inventory.delete

---

# 18. Event Bus Rules

Current implementation:

In-process

Future implementation:

Distributed

Interface remains unchanged.

Available methods:

emit()

subscribe()

unsubscribe()

---

# 19. Registry Rules

Modules register themselves.

Future discovery may become automatic.

Current registration remains explicit.

Available methods:

register()

unregister()

list_modules()

get_module()

---

# 20. Future Evolution

Version 1

Simple

Manual registration

In-process events

Single PostgreSQL database

---

Version 2

Dynamic discovery

Background jobs

Feature Flags

AI Services

Workflow Engine

---

Version 3

Distributed Event Bus

Plugin Marketplace

Microservice extraction (only if justified)

---

# 21. Non-Negotiable Rules

✓ Modules never import other modules.

✓ Core never depends on business modules.

✓ Business logic never belongs inside routers.

✓ Shared code belongs inside Shared.

✓ Everything is tenant-aware.

✓ Interfaces remain stable.

✓ Configuration over customization.

✓ Events instead of direct coupling.

✓ Every module owns its business rules.

✓ Every architecture decision must support long-term maintainability.

---

# 22. Development Philosophy

The platform should grow through real requirements rather than speculative engineering.

We commit to stable interfaces from the beginning.

We intentionally delay heavyweight infrastructure until practical experience justifies it.

This ensures the platform remains simple while preserving a path toward future scalability.

The objective is not to build the largest architecture.

The objective is to build the most maintainable architecture.
