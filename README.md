# Full-Stack Blog Application

A production-ready, full-stack Blog Application designed with modern architecture principles. Built using **Django REST Framework** for a robust backend and **React (Vite)** for a high-performance frontend. This project features secure JWT authentication, session management, and a seamless CRUD experience for blog posts.

## 🚀 Features

### Core
- **Full-Stack Architecture**: Decoupled usage of Django (Backend) and React (Frontend).
- **Dockerized Setup**: Ready-to-use `docker-compose.yml` for database, backend, and frontend services.
- **PostgreSQL Database**: Configured for robust data handling (switchable to SQLite for dev).

### Backend (Django + DRF)
- **Secure Authentication**: 
  - JWT (JSON Web Token) authentication via `simplejwt`.
  - Custom User model extending `AbstractUser`.
  - Session management (view active sessions, logout specific or all devices).
  - Password change and profile management endpoints.
- **API Documentation**: Auto-generated Swagger and Redoc documentation via `drf-spectacular`.
- **Blog Management**: ViewSet-based CRUD operations for blog posts.

### Frontend (React + Vite)
- **Modern UI**: Built with **Tailwind CSS** for responsive and utility-first styling.
- **State Management**: Context API or efficient prop drilling (based on current inspection).
- **Client-Side Routing**: `react-router-dom` for seamless page transitions.
- **Axios Interceptor**: Centralized API request handling with auto-token attachments.

---

## 🛠 Tech Stack

### Backend
- **Framework**: Django 5.x, Django REST Framework
- **Auth**: djangorestframework-simplejwt
- **Docs**: drf-spectacular
- **Database**: PostgreSQL (Production/Docker), SQLite (Local Dev)
- **Container**: Docker, Docker Compose

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Routing**: React Router DOM v7

---

## 📂 Project Structure

```bash
├── backend/                # Django Backend
│   ├── accounts/           # User authentication & profile management
│   ├── blog/               # Blog post logic
│   ├── config/             # Project settings & URL routing
│   ├── Dockerfile          # Backend container definition
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Full page views
│   │   └── Main.jsx        # App entry point
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
│
└── docker-compose.yml      # Orchestration for DB, Backend, Frontend
```

---

## ⚡ Getting Started

### Option 1: Docker (Recommended)
Run the entire stack with a single command.

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd django-login-register
   ```

2. **Setup Environment Variables**:
   Create a `.env` file in `backend/` (see [Configuration](#-configuration)).

3. **Build and Run**:
   ```bash
   docker-compose up --build
   ```
   - Frontend: `http://localhost:5173`
   - Backend: `http://localhost:8000`
   - API Docs: `http://localhost:8000/api/schema/swagger-ui/`

### Option 2: Manual Installation

#### Backend
1. Navigate to backend:
   ```bash
   cd backend
   ```
2. Create virtual environment & install deps:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run migrations & start server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

#### Frontend
1. Navigate to frontend:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start development server:
   ```bash
   npm run dev
   ```

---

## ⚙ Configuration

### Backend `.env`
Create `backend/.env` with the following keys (adjust as needed):

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
# Database (if using Postgres manually)
DB_NAME=blog_db
DB_USER=blog_user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

---

## 🔗 API Endpoints

### Authentication (`/api/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register/` | Register a new user |
| POST | `/token/` | Obtain Access & Refresh tokens (Login) |
| POST | `/token/refresh/` | Refresh Access token |
| GET/PUT | `/profile/` | Get or Update user profile |
| POST | `/change-password/` | Change current user password |
| GET | `/sessions/` | List active sessions |
| POST | `/logout/` | Logout from current device |
| POST | `/logout-all/` | Logout from all devices |

### Blog (`/api/blog/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/posts/` | List all posts |
| POST | `/posts/` | Create a new post |
| GET | `/posts/{id}/` | Retrieve a specific post |
| PUT | `/posts/{id}/` | Update a post |
| DELETE | `/posts/{id}/` | Delete a post |

---

## 🧪 Testing

### Backend Tests
Run the standard Django test suite:
```bash
cd backend
python manage.py test
```

### Frontend Linting
Check code quality:
```bash
cd frontend
npm run lint
```

---

## 🤝 Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.
