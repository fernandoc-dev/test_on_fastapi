# Project Management Platform with Multi-Source Integration

## Project Overview

A comprehensive project management platform that unifies tasks from multiple sources (local database, GitHub, and Trello) into a single, cohesive view. Built with Clean Architecture principles, this application demonstrates integration with external APIs, authentication/authorization, and composite data models.

## Core Features

- **Multi-source task aggregation**: Combine local tasks, GitHub issues, and Trello cards
- **OAuth integration**: Secure authentication with GitHub and Trello APIs
- **User authentication**: JWT-based authentication for platform users
- **Unified project view**: Single endpoint to view all project-related data
- **Real-time synchronization**: Sync data from external APIs
- **Clean Architecture**: Separation of concerns with domain, use cases, infrastructure, and presentation layers

## Technical Requirements

### Architecture

- **Clean Architecture** with clear separation:
  - **Domain Layer**: Entities and business logic
  - **Use Cases Layer**: Application-specific business rules
  - **Infrastructure Layer**: Database, external APIs, authentication
  - **Presentation Layer**: FastAPI endpoints and DTOs

### External APIs

1. **GitHub API**
   - Authentication: OAuth 2.0
   - Endpoints: Repositories, Issues, Pull Requests, Commits
   - Documentation: https://docs.github.com/en/rest

2. **Trello API**
   - Authentication: OAuth 1.0a / API Key
   - Endpoints: Boards, Lists, Cards, Checklists
   - Documentation: https://developer.atlassian.com/cloud/trello/

### Database (PostgreSQL)

Stores:
- Users and authentication data
- Projects
- Local tasks
- OAuth tokens for GitHub and Trello integrations
- User preferences and settings

### Composite Data Model

A **Project** entity combines:
- **Local data** (from database): name, description, status, dates, local tasks
- **GitHub data** (from API): open issues, pending PRs, recent commits
- **Trello data** (from API): active cards, board progress

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login (JWT)
- `POST /auth/github/connect` - Connect GitHub account (OAuth flow)
- `POST /auth/trello/connect` - Connect Trello account (OAuth flow)
- `GET /auth/integrations` - Get user's connected integrations
- `DELETE /auth/integrations/{provider}` - Disconnect integration

### Projects
- `GET /projects` - List user's projects
- `GET /projects/{id}` - Get project with unified data (local + GitHub + Trello)
- `POST /projects` - Create new project
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project
- `POST /projects/{id}/sync` - Manually trigger data synchronization

### Tasks
- `GET /projects/{id}/tasks` - Get unified task view (local + GitHub + Trello)
- `POST /projects/{id}/tasks` - Create local task
- `PUT /tasks/{id}` - Update local task
- `DELETE /tasks/{id}` - Delete local task

### Summary & Analytics
- `GET /projects/{id}/summary` - Get project summary with combined metrics
- `GET /projects/{id}/stats` - Get statistics (task counts, completion rates, etc.)

## Development Checklist

### Phase 1: Project Setup & Foundation
- [ ] Define domain entities (User, Project, Task, Integration)
- [ ] Set up database schema and migrations
- [ ] Configure SQLAlchemy models
- [ ] Set up Alembic for migrations
- [ ] Create base repository interfaces
- [ ] Configure environment variables for database

### Phase 2: Authentication & Authorization
- [ ] Implement user registration
- [ ] Implement JWT authentication
- [ ] Create user repository
- [ ] Add password hashing (bcrypt)
- [ ] Implement login endpoint
- [ ] Add JWT token refresh mechanism
- [ ] Create authentication middleware
- [ ] Add role-based access control (if needed)

### Phase 3: Domain Layer
- [ ] Define User entity
- [ ] Define Project entity
- [ ] Define Task entity (local)
- [ ] Define Integration entity (GitHub/Trello tokens)
- [ ] Define value objects (Email, ProjectStatus, etc.)
- [ ] Create domain exceptions
- [ ] Define domain services

### Phase 4: Use Cases Layer
- [ ] CreateProject use case
- [ ] GetProject use case
- [ ] ListProjects use case
- [ ] CreateTask use case
- [ ] SyncProjectData use case
- [ ] ConnectGitHubIntegration use case
- [ ] ConnectTrelloIntegration use case
- [ ] GetUnifiedTasks use case
- [ ] GetProjectSummary use case

### Phase 5: Infrastructure - Database
- [ ] Implement UserRepository (PostgreSQL)
- [ ] Implement ProjectRepository (PostgreSQL)
- [ ] Implement TaskRepository (PostgreSQL)
- [ ] Implement IntegrationRepository (PostgreSQL)
- [ ] Add database connection pooling
- [ ] Implement transaction management
- [ ] Add database indexes for performance

### Phase 6: Infrastructure - External APIs
- [ ] Create GitHub API client
- [ ] Implement GitHub OAuth flow
- [ ] Create methods to fetch repositories
- [ ] Create methods to fetch issues
- [ ] Create methods to fetch pull requests
- [ ] Create Trello API client
- [ ] Implement Trello OAuth flow
- [ ] Create methods to fetch boards
- [ ] Create methods to fetch cards
- [ ] Add error handling for API failures
- [ ] Implement rate limiting handling
- [ ] Add retry logic for failed requests
- [ ] Cache API responses (optional)

### Phase 7: Infrastructure - Data Synchronization
- [ ] Create sync service for GitHub data
- [ ] Create sync service for Trello data
- [ ] Implement background job for periodic sync
- [ ] Add sync status tracking
- [ ] Handle sync conflicts
- [ ] Add sync error logging

### Phase 8: Presentation Layer
- [ ] Create FastAPI routers
- [ ] Define request/response DTOs (Pydantic models)
- [ ] Implement authentication endpoints
- [ ] Implement project endpoints
- [ ] Implement task endpoints
- [ ] Implement integration endpoints
- [ ] Add request validation
- [ ] Add response serialization
- [ ] Implement error handling middleware
- [ ] Add API documentation (OpenAPI/Swagger)

### Phase 9: Composite Data Aggregation
- [ ] Implement project data aggregator service
- [ ] Combine local + GitHub + Trello data
- [ ] Create unified task view
- [ ] Implement project summary calculation
- [ ] Add data transformation logic
- [ ] Handle missing/invalid external data

### Phase 10: Testing
- [ ] Unit tests for domain entities
- [ ] Unit tests for use cases
- [ ] Unit tests for repositories
- [ ] Unit tests for API clients (mocked)
- [ ] Integration tests for database operations
- [ ] Integration tests for API endpoints
- [ ] E2E tests for complete flows
- [ ] Test OAuth flows
- [ ] Test data synchronization
- [ ] Load tests for critical endpoints

### Phase 11: Documentation & Deployment
- [ ] Complete API documentation
- [ ] Add code comments and docstrings
- [ ] Create deployment guide
- [ ] Set up CI/CD pipeline
- [ ] Configure production environment variables
- [ ] Add monitoring and logging
- [ ] Performance optimization
- [ ] Security audit

## Project Structure

```
app/
├── domain/
│   ├── entities/
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── integration.py
│   ├── value_objects/
│   │   ├── email.py
│   │   └── project_status.py
│   └── exceptions.py
├── use_cases/
│   ├── projects/
│   │   ├── create_project.py
│   │   ├── get_project.py
│   │   └── sync_project_data.py
│   ├── tasks/
│   │   ├── create_task.py
│   │   └── get_unified_tasks.py
│   └── integrations/
│       ├── connect_github.py
│       └── connect_trello.py
├── infrastructure/
│   ├── database/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── migrations/
│   ├── external_apis/
│   │   ├── github_client.py
│   │   └── trello_client.py
│   ├── auth/
│   │   ├── jwt_handler.py
│   │   └── oauth_handlers.py
│   └── sync/
│       ├── github_sync.py
│       └── trello_sync.py
├── presentation/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   └── tasks.py
│   ├── dto/
│   │   ├── requests/
│   │   └── responses/
│   └── middleware/
└── main.py
```

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose), OAuth 2.0
- **HTTP Client**: httpx
- **Testing**: pytest, pytest-asyncio
- **Validation**: Pydantic

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback

# Trello OAuth
TRELLO_API_KEY=your-trello-api-key
TRELLO_API_SECRET=your-trello-api-secret
TRELLO_REDIRECT_URI=http://localhost:8000/auth/trello/callback
```

## Development Workflow (TDD)

1. **Red**: Write failing tests for a feature
2. **Green**: Implement minimal code to make tests pass
3. **Refactor**: Improve code while keeping tests green
4. **Repeat**: Move to next feature

## Getting Started

1. Set up environment variables
2. Run database migrations
3. Start the application
4. Register a user
5. Connect GitHub/Trello accounts
6. Create a project
7. Associate repositories/boards
8. View unified project data

## Notes

- All external API calls should be async
- Implement proper error handling for API failures
- Cache external API responses when appropriate
- Use background tasks for data synchronization
- Implement rate limiting for external APIs
- Add comprehensive logging for debugging

