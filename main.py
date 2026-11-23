from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from pwdlib import PasswordHash

import models
from database import Base, engine, get_db


app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)

password_hash = PasswordHash.recommended()

app.add_middleware(
    SessionMiddleware,
    secret_key="change-this-secret-key-before-deployment"
)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"message": None}
    )


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {}
    )



@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"message": None}
    )


@app.post("/register", response_class=HTMLResponse)
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"message": "Username already exists."}
        )

    existing_email = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if existing_email:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"message": "Email already exists."}
        )

    hashed_password = password_hash.hash(password)

    new_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse(
    url="/login",
    status_code=303
)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"message": None}
    )


@app.post("/login", response_class=HTMLResponse)
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if not user or not password_hash.verify(
        password, user.hashed_password
    ):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"message": "Invalid username or password."}
        )

    request.session["user_id"] = user.id

    return RedirectResponse(
    url="/vote",
    status_code=303
)


@app.get("/vote", response_class=HTMLResponse)
def voting_page(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"message": "Please log in before voting."}
        )

    candidates = db.query(models.Candidate).all()

    if not candidates:
        candidates = [
            models.Candidate(
                name="Candidate 1",
                description="First candidate"
            ),
            models.Candidate(
                name="Candidate 2",
                description="Second candidate"
            )
        ]

        db.add_all(candidates)
        db.commit()

        candidates = db.query(models.Candidate).all()

    return templates.TemplateResponse(
        request,
        "vote.html",
        {
            "candidates": candidates,
            "message": None
        }
    )
    
    
@app.post("/vote", response_class=HTMLResponse)
def cast_vote(
    request: Request,
    candidate_id: int = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    # Check whether the user is logged in
    if not user_id:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"message": "Please log in before voting."}
        )

    # Check whether this user has already voted
    existing_vote = db.query(models.Vote).filter(
        models.Vote.user_id == user_id
    ).first()

    if existing_vote:
        return templates.TemplateResponse(
            request,
            "vote.html",
            {
                "candidates": db.query(models.Candidate).all(),
                "message": "You have already voted!"
            }
        )

    # Find the selected candidate
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()

    if not candidate:
        return templates.TemplateResponse(
            request,
            "vote.html",
            {
                "candidates": db.query(models.Candidate).all(),
                "message": "Invalid candidate selected."
            }
        )

    # Save the vote
    new_vote = models.Vote(
        user_id=user_id,
        candidate_id=candidate_id
    )

    db.add(new_vote)
    db.commit()

    return templates.TemplateResponse(
        request,
        "vote.html",
        {
            "candidates": db.query(models.Candidate).all(),
            "message": f"Your vote for {candidate.name} was successful!"
        }
    )
    

@app.get("/results", response_class=HTMLResponse)
def election_results(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    candidates = db.query(models.Candidate).all()

    votes = db.query(models.Vote).all()

    for candidate in candidates:
        candidate.vote_count = len(candidate.votes)

    return templates.TemplateResponse(
        request,
        "results.html",
        {
            "candidates": candidates,
            "votes": votes
        }
    )

@app.get("/logout")
def logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )
