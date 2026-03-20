from fastapi import FastAPI, Query, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

# ------------------ DATA ------------------

movies = [
    {"id": 1, "title": "Avengers", "genre": "Action", "language": "English", "duration_mins": 150, "ticket_price": 200, "seats_available": 50},
    {"id": 2, "title": "Inception", "genre": "Action", "language": "English", "duration_mins": 140, "ticket_price": 250, "seats_available": 40},
    {"id": 3, "title": "Interstellar", "genre": "Drama", "language": "English", "duration_mins": 160, "ticket_price": 220, "seats_available": 30},
    {"id": 4, "title": "3 Idiots", "genre": "Comedy", "language": "Hindi", "duration_mins": 170, "ticket_price": 180, "seats_available": 60},
    {"id": 5, "title": "The Conjuring", "genre": "Horror", "language": "English", "duration_mins": 120, "ticket_price": 210, "seats_available": 35},
    {"id": 6, "title": "Drishyam", "genre": "Drama", "language": "Hindi", "duration_mins": 130, "ticket_price": 190, "seats_available": 45}
]

bookings = []
booking_counter = 1

holds = []
hold_counter = 1

# ------------------ MODELS ------------------

class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10)
    seat_type: str = "standard"
    promo_code: str = ""

class NewMovie(BaseModel):
    title: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)

class HoldRequest(BaseModel):
    customer_name: str
    movie_id: int
    seats: int

# ------------------ HELPERS ------------------

def find_movie(movie_id):
    for movie in movies:
        if movie["id"] == movie_id:
            return movie
    return None


def calculate_ticket_cost(base_price, seats, seat_type, promo_code=""):
    if seat_type == "premium":
        price = base_price * 1.5
    elif seat_type == "recliner":
        price = base_price * 2
    else:
        price = base_price

    total = price * seats

    discount = 0
    if promo_code == "SAVE10":
        discount = 0.1
    elif promo_code == "SAVE20":
        discount = 0.2

    discounted_total = total - (total * discount)

    return {
        "original_total": total,
        "discounted_total": discounted_total
    }


def filter_movies_logic(genre=None, language=None, max_price=None, min_seats=None):
    result = movies

    if genre is not None:
        result = [m for m in result if m["genre"].lower() == genre.lower()]

    if language is not None:
        result = [m for m in result if m["language"].lower() == language.lower()]

    if max_price is not None:
        result = [m for m in result if m["ticket_price"] <= max_price]

    if min_seats is not None:
        result = [m for m in result if m["seats_available"] >= min_seats]

    return result

# ------------------ Q1 ------------------

@app.get("/")
def home():
    return {"message": "Welcome to CineStar Booking"}

# ------------------ Q2 ------------------

@app.get("/movies")
def get_movies():
    total_seats = sum(m["seats_available"] for m in movies)
    return {
        "movies": movies,
        "total": len(movies),
        "total_seats_available": total_seats
    }

# ------------------ Q4 ------------------

@app.get("/bookings")
def get_bookings():
    total_revenue = sum(b.get("final_cost", 0) for b in bookings)
    return {
        "bookings": bookings,
        "total": len(bookings),
        "total_revenue": total_revenue
    }

# ------------------ Q10 ------------------

@app.get("/movies/filter")
def filter_movies(
    genre: str = None,
    language: str = None,
    max_price: int = None,
    min_seats: int = None
):
    filtered = filter_movies_logic(genre, language, max_price, min_seats)
    return {"total": len(filtered), "movies": filtered}

# ------------------ Q5 ------------------

@app.get("/movies/summary")
def movies_summary():
    total_seats = sum(m["seats_available"] for m in movies)
    max_price = max(m["ticket_price"] for m in movies)
    min_price = min(m["ticket_price"] for m in movies)

    genre_count = {}
    for m in movies:
        genre = m["genre"]
        genre_count[genre] = genre_count.get(genre, 0) + 1

    return {
        "total_movies": len(movies),
        "most_expensive_ticket": max_price,
        "cheapest_ticket": min_price,
        "total_seats": total_seats,
        "movies_by_genre": genre_count
    }

# ------------------ Q8 + Q9 ------------------

@app.post("/bookings")
def create_booking(request: BookingRequest):
    global booking_counter

    movie = find_movie(request.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if movie["seats_available"] < request.seats:
        return {"error": "Not enough seats available"}

    cost = calculate_ticket_cost(
        movie["ticket_price"],
        request.seats,
        request.seat_type,
        request.promo_code
    )

    movie["seats_available"] -= request.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": request.customer_name,
        "movie_title": movie["title"],
        "seats": request.seats,
        "seat_type": request.seat_type,
        "original_cost": cost["original_total"],
        "final_cost": cost["discounted_total"]
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

# ------------------ Q11 ------------------

@app.post("/movies", status_code=status.HTTP_201_CREATED)
def add_movie(movie: NewMovie):
    for m in movies:
        if m["title"].lower() == movie.title.lower():
            raise HTTPException(status_code=400, detail="Movie already exists")

    new_movie = movie.dict()
    new_movie["id"] = len(movies) + 1
    movies.append(new_movie)

    return new_movie

# ------------------ Q12 ------------------

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, ticket_price: int = None, seats_available: int = None):
    movie = find_movie(movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if ticket_price is not None:
        movie["ticket_price"] = ticket_price

    if seats_available is not None:
        movie["seats_available"] = seats_available

    return {"message": "Movie updated", "movie": movie}

# ------------------ Q13 ------------------

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    for b in bookings:
        if b["movie_title"] == movie["title"]:
            return {"error": "Cannot delete movie with existing bookings"}

    movies.remove(movie)
    return {"message": "Movie deleted"}

# ------------------ Q14 ------------------

@app.post("/seat-hold")
def create_hold(request: HoldRequest):
    global hold_counter

    movie = find_movie(request.movie_id)
    if not movie:
        return {"error": "Movie not found"}

    if movie["seats_available"] < request.seats:
        return {"error": "Not enough seats"}

    movie["seats_available"] -= request.seats

    hold = {
        "hold_id": hold_counter,
        "customer_name": request.customer_name,
        "movie_id": request.movie_id,
        "seats": request.seats
    }

    holds.append(hold)
    hold_counter += 1

    return hold


@app.get("/seat-hold")
def get_holds():
    return holds

# ------------------ Q15 ------------------

@app.post("/seat-confirm/{hold_id}")
def confirm_hold(hold_id: int):
    global booking_counter

    for hold in holds:
        if hold["hold_id"] == hold_id:
            movie = find_movie(hold["movie_id"])

            booking = {
                "booking_id": booking_counter,
                "customer_name": hold["customer_name"],
                "movie_title": movie["title"],
                "seats": hold["seats"],
                "seat_type": "standard",
                "original_cost": movie["ticket_price"] * hold["seats"],
                "final_cost": movie["ticket_price"] * hold["seats"]
            }

            bookings.append(booking)
            booking_counter += 1
            holds.remove(hold)

            return booking

    return {"error": "Hold not found"}


@app.delete("/seat-release/{hold_id}")
def release_hold(hold_id: int):
    for hold in holds:
        if hold["hold_id"] == hold_id:
            movie = find_movie(hold["movie_id"])

            movie["seats_available"] += hold["seats"]
            holds.remove(hold)

            return {"message": "Hold released"}

    return {"error": "Hold not found"}

# ------------------ Q16 ------------------

@app.get("/movies/search")
def search_movies(keyword: str):
    result = [
        m for m in movies
        if keyword.lower() in m["title"].lower()
        or keyword.lower() in m["genre"].lower()
        or keyword.lower() in m["language"].lower()
    ]

    if not result:
        return {"message": "No movies found"}

    return {"total_found": len(result), "movies": result}

# ------------------ Q17 ------------------

@app.get("/movies/sort")
def sort_movies(sort_by: str = "ticket_price", order: str = "asc"):
    valid = ["ticket_price", "title", "duration_mins", "seats_available"]

    if sort_by not in valid:
        return {"error": "Invalid field"}

    reverse = True if order == "desc" else False

    return sorted(movies, key=lambda x: x[sort_by], reverse=reverse)

# ------------------ Q18 ------------------

@app.get("/movies/page")
def paginate_movies(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit

    total = len(movies)
    total_pages = (total + limit - 1) // limit

    return {
        "total": total,
        "total_pages": total_pages,
        "movies": movies[start:end]
    }

# ------------------ Q19 ------------------

@app.get("/bookings/search")
def search_bookings(customer_name: str):
    result = [b for b in bookings if customer_name.lower() in b["customer_name"].lower()]
    return {"total": len(result), "bookings": result}


@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "final_cost"):
    return sorted(bookings, key=lambda x: x[sort_by])


@app.get("/bookings/page")
def paginate_bookings(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit

    total = len(bookings)
    total_pages = (total + limit - 1) // limit

    return {
        "total": total,
        "total_pages": total_pages,
        "bookings": bookings[start:end]
    }

# ------------------ Q20 ------------------

@app.get("/movies/browse")
def browse_movies(
    keyword: str = None,
    genre: str = None,
    language: str = None,
    sort_by: str = "ticket_price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = movies

    if keyword:
        result = [
            m for m in result
            if keyword.lower() in m["title"].lower()
            or keyword.lower() in m["genre"].lower()
            or keyword.lower() in m["language"].lower()
        ]

    if genre:
        result = [m for m in result if m["genre"].lower() == genre.lower()]

    if language:
        result = [m for m in result if m["language"].lower() == language.lower()]

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    end = start + limit

    total = len(result)
    total_pages = (total + limit - 1) // limit

    return {
        "total": total,
        "total_pages": total_pages,
        "movies": result[start:end]
    }

# ------------------ Q3 (LAST) ------------------

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = find_movie(movie_id)
    if movie:
        return movie
    return {"error": "Movie not found"}