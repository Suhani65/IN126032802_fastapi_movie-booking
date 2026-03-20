# 🎬 FastAPI Movie Ticket Booking System

## 📌 Overview
This project is a complete backend system built using **FastAPI** for managing a movie ticket booking platform.  
It demonstrates real-world API development with proper structure, validation, and workflows.

---

## 🚀 Key Features

### 🎥 Movie Management
- View all movies
- Get movie by ID
- Movie summary (price, seats, genre stats)
- Add, update, and delete movies (CRUD)

### 🎟 Booking System
- Create bookings with validation
- Seat availability checks
- Ticket cost calculation with seat types
- Promo code discounts (SAVE10, SAVE20)

### 🔄 Multi-Step Workflow
- Seat Hold system
- Confirm booking from hold
- Release hold (restore seats)

### 🔍 Advanced APIs
- Search movies (title, genre, language)
- Sort movies (price, duration, seats, title)
- Pagination for movies and bookings
- Combined browsing (search + filter + sort + paginate)

---

## 🧠 Concepts Implemented

- REST API development using FastAPI
- Pydantic models & validation
- Helper functions for business logic
- CRUD operations
- Multi-step workflows
- Query parameters & filtering
- Search, sorting, pagination
- Swagger UI testing

---

## 🛠 Tech Stack

- **Python**
- **FastAPI**
- **Uvicorn**
- **Pydantic**

---

## ▶️ How to Run

```bash
uvicorn main:app --reload
