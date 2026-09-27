# System Architecture & Technical Stack

## 1. High-Level Architecture Diagram

```text
+-----------------------------------------------------------------------------------+
|                                 CLIENT LAYER                                      |
|                                                                                   |
|    +-------------------------------------------------------------------------+    |
|    |                      React 18 Single Page App (Vite)                    |    |
|    |  - Tailwind CSS UI Framework                                           |    |
|    |  - React Router v6 Navigation & Protected Route Guards                  |    |
|    |  - Axios HTTP Client with JWT Request Interceptors                      |    |
|    +-------------------------------------------------------------------------+    |
+------------------------------------------|----------------------------------------+
                                           | HTTP REST API (JSON)
                                           v
+-----------------------------------------------------------------------------------+
|                                 APPLICATION LAYER                                 |
|                                                                                   |
|    +-------------------------------------------------------------------------+    |
|    |                         FastAPI Application Server                      |    |
|    |                                                                         |    |
|    |  +-------------------------------------------------------------------+  |    |
|    |  | CORS & Authorization Middleware (JWT Bearer Verification)         |  |    |
|    |  +-------------------------------------------------------------------+  |    |
|    |  | API Controllers / Routers (/auth, /students, /drives, etc.)       |  |    |
|    |  +-------------------------------------------------------------------+  |    |
|    |  | Business Logic Service Layer:                                     |  |    |
|    |  |   - Auth & Security Service (passlib bcrypt, pyjwt)               |  |    |
|    |  |   - Eligibility Engine Service                                    |  |    |
|    |  |   - Application State Machine Engine                              |  |    |
|    |  +-------------------------------------------------------------------+  |    |
|    |  | Data Access Layer: SQLAlchemy 2.0 ORM + Pydantic v2 Schemas       |  |    |
|    +-------------------------------------------------------------------------+    |
+------------------------------------------|----------------------------------------+
                                           | SQL Queries
                                           v
+-----------------------------------------------------------------------------------+
|                                  DATA LAYER                                       |
|                                                                                   |
|    +-------------------------------------------------------------------------+    |
|    |                      SQLite RDBMS (Default Engine)                      |    |
|    |  - Relational Schema with Foreign Keys & Unique Constraints             |    |
|    |  - Clean Migration path to PostgreSQL via SQLAlchemy dialect swap       |    |
|    +-------------------------------------------------------------------------+    |
+-----------------------------------------------------------------------------------+
```

---

## 2. Component Design & Responsibilities

### 2.1 Backend Project Structure
```text
backend/
├── app/
│   ├── auth/            # JWT utils, password hashing, OAuth2 scheme, role dependencies
│   ├── database.py      # SQLAlchemy engine, SessionLocal base setup
│   ├── main.py          # FastAPI instance initialization, middleware, router mounts
│   ├── models/          # SQLAlchemy ORM database models
│   ├── routers/         # API endpoints (Auth, Students, Companies, Drives, Applications...)
│   ├── schemas/         # Pydantic request/response validation schemas
│   ├── services/        # Isolated business logic engines (Eligibility, State Machine)
│   └── utils/           # Helper scripts and constants
```

### 2.2 Frontend Project Structure
```text
frontend/
├── src/
│   ├── components/      # Reusable UI components (Navbar, Sidebar, Badges, Modals)
│   ├── context/         # AuthContext (user session, JWT storage, role state)
│   ├── hooks/           # Custom React hooks (useAuth, useEligibility)
│   ├── layouts/         # Layout wrappers for Admin, Student, Recruiter portals
│   ├── pages/           # Views (Login, Profile, Drives, Applications, Interviews, Offers)
│   ├── routes/          # Router setup & ProtectedRoute components
│   ├── services/        # Axios API client modules
│   └── utils/           # Date formatters, status badge helpers
```

---

## 3. Technology Rationale

1. **FastAPI**: Provides automatic OpenAPI documentation, async capability, fast execution, and native pydantic type safety.
2. **React + Vite**: Enables instant hot-module replacement, high UI responsiveness, component reusability, and simple state management.
3. **SQLAlchemy 2.0**: Abstracted ORM allowing transparent transition between SQLite for local evaluation and PostgreSQL for production deployment.
4. **JWT Security**: Stateless authentication allowing seamless client-side authorization across role-gated routes.
