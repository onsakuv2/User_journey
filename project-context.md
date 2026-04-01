# Project Context: User Journey Task Manager

## Overview
A web-based task management application built with **FastAPI** (Python) using server-side rendered HTML templates (Jinja2) and **SQLite** as the database backend via **SQLAlchemy** ORM.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend Framework | FastAPI |
| Templating | Jinja2 (`fastapi.templating`) |
| ORM | SQLAlchemy |
| Database | SQLite (`tasks.db`) |
| Auth | Cookie-based session (plain-text passwords) |
| Language | Python |

## Architecture
- **Monolithic** single-file application (`main.py`)
- Server-side rendering with HTML templates in `./templates/` directory
- SQLite file-based database (`./tasks.db`)
- No API-only endpoints — all routes serve HTML or perform redirects

## Data Models

### User
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK, indexed |
| username | String | indexed |
| email | String | unique, indexed |
| password | String | plain text |

### Task
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK, indexed |
| user_id | Integer | FK → users.id |
| name | String | — |
| description | Text | — |
| start_date | Date | — |
| end_date | Date | — |
| category | String | — |

## Routes
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/` | Landing page (login/register) | No |
| POST | `/login` | Authenticate user, set cookie | No |
| POST | `/register` | Create new user account | No |
| GET | `/logout` | Clear auth cookie, redirect | Yes |
| GET | `/home` | Dashboard — list user's tasks | Yes |
| GET | `/task` | Task create/edit form (via `?task_id=`) | Yes |
| POST | `/task` | Save (create or update) a task | Yes |

## Authentication
- Cookie-based: `user_id` cookie stores the user's DB ID
- No hashing — passwords stored in plain text
- No CSRF protection
- Helper: `get_current_user(request, db)` reads cookie and queries DB

## Seed Data
On startup, seeds a default user (`sam@sam.com` / `pass`) with one sample task if not already present.

## Expected Templates (in `./templates/`)
- `landing.html` — login & registration forms
- `home.html` — task list dashboard (context: `user`, `tasks`)
- `task.html` — task create/edit form (context: `user`, `task`)

## Key Notes
- **No password hashing** — this is a simple/demo app
- **No middleware** for auth — manual cookie check per route
- Uses `RedirectResponse` with status `302` for POST-redirect-GET pattern
- SQLAlchemy `declarative_base()` usage (deprecated in newer SQLAlchemy; consider `DeclarativeBase`)
- `TemplateResponse` uses the newer keyword-argument style (`request=request, name=...`)
- `seed_data()` runs at module load time (not via a startup event)