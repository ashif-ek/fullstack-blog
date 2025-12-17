# React + Django Blog Application

A production-ready full-stack Blog Application built with **Django REST Framework** and **React (Vite)**. Features secure **JWT authentication**, a responsive **Tailwind CSS UI**, and complete CRUD functionality for blog posts. Unified user management ensures seamless interaction between the Django admin and the React frontend.

## Features
- **Full-Stack Architecture**: Django (Backend) + React (Frontend).
- **Secure Authentication**: JWT (JSON Web Tokens) for secure, stateless login.
- **Unified User System**: Custom User model works for both Admin and Web users.
- **Modern UI**: Built with Tailwind CSS for a responsive, clean design.
- **Blog Management**: Create, Read, Update, and Delete posts via the React UI.

## Tech Stack
- **Backend**: Python, Django, Django REST Framework, SimpleJWT.
- **Frontend**: JavaScript, React, Vite, Tailwind CSS, Axios.
- **Database**: SQLite (Default) / PostgreSQL ready.

## Getting Started

### Prerequisites
- Python 3.x
- Node.js & npm

### Installation

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://127.0.0.1:8000`
