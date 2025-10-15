from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import database
import auth

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_current_user(request):
    token = request.cookies.get("auth_token")
    if token and auth.verify_token(token):
        email = auth.get_email_from_token(token)
        db = database.get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()
        return user
    return None

@app.get("/")
def home(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    
    db = database.get_db()
    
    if user['role'] == 'admin':
        tickets = db.execute("""
            SELECT t.*, u.full_name 
            FROM tickets t 
            JOIN users u ON t.user_id = u.id 
            ORDER BY t.created_at DESC
        """).fetchall()
    else:
        tickets = db.execute("""
            SELECT * FROM tickets 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user['id'],)).fetchall()
    
    db.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "tickets": tickets
    })

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(request: Request, full_name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    db = database.get_db()
    
    existing_user = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing_user:
        db.close()
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email already taken"
        })
    
    hashed_password = auth.hash_password(password)
    db.execute(
        "INSERT INTO users (email, password, full_name, role) VALUES (?, ?, ?, 'user')",
        (email, hashed_password, full_name)
    )
    db.commit()
    db.close()
    
    return RedirectResponse("/login")

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    db = database.get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    db.close()
    
    if user and auth.check_password(password, user['password']):
        token = auth.create_token(email)
        response = RedirectResponse("/")
        response.set_cookie(key="auth_token", value=token)
        return response
    
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "error": "Invalid email or password"
    })

@app.post("/create_ticket")
def create_ticket(request: Request, title: str = Form(...), description: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    
    db = database.get_db()
    db.execute(
        "INSERT INTO tickets (title, description, user_id) VALUES (?, ?, ?)",
        (title, description, user['id'])
    )
    db.commit()
    db.close()
    
    return RedirectResponse("/")

@app.post("/close_ticket/{ticket_id}")
def close_ticket(ticket_id: int, request: Request):
    user = get_current_user(request)
    if not user or user['role'] != 'admin':
        return RedirectResponse("/login")
    
    db = database.get_db()
    db.execute("UPDATE tickets SET status = 'Closed' WHERE id = ?", (ticket_id,))
    db.commit()
    db.close()
    
    return RedirectResponse("/")

# ADDED DELETE TICKET ROUTE
@app.post("/delete_ticket/{ticket_id}")
def delete_ticket(ticket_id: int, request: Request):
    user = get_current_user(request)
    if not user or user['role'] != 'admin':
        return RedirectResponse("/login")
    
    db = database.get_db()
    db.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    db.commit()
    db.close()
    
    return RedirectResponse("/")

@app.get("/logout")
def logout():
    response = RedirectResponse("/login")
    response.delete_cookie("auth_token")
    return response

@app.post("/")
def handle_post_home(request: Request):
    user = get_current_user(request)
    if not user:
        # If no user, redirect to GET /login instead of showing dashboard
        return RedirectResponse("/login")
    
    # Rest of your existing code...
    db = database.get_db()
    
    if user['role'] == 'admin':
        tickets = db.execute("""
            SELECT t.*, u.full_name 
            FROM tickets t 
            JOIN users u ON t.user_id = u.id 
            ORDER BY t.created_at DESC
        """).fetchall()
    else:
        tickets = db.execute("""
            SELECT * FROM tickets 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user['id'],)).fetchall()
    
    db.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "tickets": tickets
    })
