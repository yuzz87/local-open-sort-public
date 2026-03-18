from flask import Blueprint, render_template

page_bp = Blueprint("pages", __name__)


@page_bp.get("/health")
def health():
    return "ok", 200


@page_bp.get("/")
def title():
    return render_template("title.html")


@page_bp.get("/login")
def login():
    return render_template("login.html")


@page_bp.get("/select")
def select():
    return render_template("select.html")


@page_bp.get("/game-a-Description")
def game_a_description():
    return render_template("game_a_description.html")


@page_bp.get("/game-a-Description/start")
def game_a_start():
    return render_template("game_a.html")

@page_bp.get("/game-b-Description/start")
def game_b_start():
    return render_template("game_b.html")