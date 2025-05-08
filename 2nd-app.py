from flask import Flask, request, jsonify, render_template, redirect
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_mail import Mail, Message
from datetime import timedelta
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USER = os.environ.get("EMAIL_USER", "your-email@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "your-app-password")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "your-email@gmail.com")

app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "your-email@gmail.com")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "your-app-password")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
    "MAIL_DEFAULT_SENDER", "your-email@gmail.com"
)

jwt = JWTManager(app)
db.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all()


def send_email(to, subject, template):
    """Helper function to send emails"""
    msg = Message(
        subject=subject,
        recipients=[to],
        html=template,
        sender=app.config["MAIL_DEFAULT_SENDER"],
    )
    mail.send(msg)


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Send welcome email
    welcome_html = f"""
    <h1>Welcome to Our App, {name}!</h1>
    <p>Thank you for registering with us. We're excited to have you on board!</p>
    <p>If you have any questions, feel free to reach out to our support team.</p>
    """
    try:
        send_email(email, "Welcome to Our App!", welcome_html)
        print(f"[Welcome Email] Sent to {email}")
    except Exception as e:
        print(f"Error sending email to {email}: {str(e)}")

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401

    token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
    return jsonify({"token": token})


@app.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({"id": user.id, "name": user.name, "email": user.email})


@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return (
            jsonify(
                {
                    "message": "If your email exists in our system, you will receive a reset link"
                }
            ),
            200,
        )

    reset_token = create_access_token(
        identity=user.id, expires_delta=timedelta(hours=1)
    )
    reset_url = f"http://yourdomain.com/reset-password?token={reset_token}"

    reset_html = f"""
    <h1>Password Reset Request</h1>
    <p>Hello {user.name},</p>
    <p>You recently requested to reset your password. Click the link below to reset it:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>This link will expire in 1 hour.</p>
    """

    try:
        send_email(email, "Password Reset Request", reset_html)
        print(f"[Reset Email] Sent to {email}")
    except Exception as e:
        print(f"Error sending reset email to {email}: {str(e)}")

    return (
        jsonify(
            {
                "message": "If your email exists in our system, you will receive a reset link"
            }
        ),
        200,
    )


@app.route("/register", methods=["GET", "POST"])
def register_web():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            return "Email already exists"

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        welcome_html = f"""
        <h1>Welcome to Our App, {name}!</h1>
        <p>Thank you for registering with us. We're excited to have you on board!</p>
        <p>If you have any questions, feel free to reach out to our support team.</p>
        """
        try:
            send_email(email, "Welcome to Our App!", welcome_html)
            print(f"[Welcome Email] Sent to {email}")
        except Exception as e:
            print(f"Error sending email to {email}: {str(e)}")

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_web():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return "Invalid credentials"

        token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
        return f"Login successful! Token: {token}"

    return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_web():
    if request.method == "POST":
        email = request.form["email"]

        user = User.query.filter_by(email=email).first()
        if user:
            reset_token = create_access_token(
                identity=user.id, expires_delta=timedelta(hours=1)
            )
            reset_url = f"http://localhost:5000/reset-password?token={reset_token}"

            reset_html = f"""
            <h1>Password Reset Request</h1>
            <p>Hello {user.name},</p>
            <p>You recently requested to reset your password. Click the link below to reset it:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>If you did not request a password reset, please ignore this email.</p>
            <p>This link will expire in 1 hour.</p>
            """

            try:
                send_email(email, "Password Reset Request", reset_html)
                print(f"[Reset Email] Sent to {email}")
            except Exception as e:
                print(f"Error sending reset email to {email}: {str(e)}")

        return "If your email exists in our system, you will receive a reset link."

    return render_template("forgot_password.html")


@app.route("/", methods=["GET"])
def home():
    """Home page route"""
    return render_template("home.html")


@app.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    """Dashboard page - requires authentication"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return render_template("dashboard.html", user=user)


@app.route("/profile-page", methods=["GET"])
@jwt_required()
def profile_page():
    """User profile page - requires authentication"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return render_template("profile.html", user=user)


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """Password reset page"""
    token = request.args.get("token", None)
    if not token:
        return "Invalid or missing token", 400

    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            return "Passwords do not match", 400

        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return "Invalid token", 400

            user.set_password(new_password)
            db.session.commit()

            return redirect("/login")
        except Exception as e:
            print(f"Error resetting password: {str(e)}")
            return "Invalid or expired token", 400

    return render_template("reset_password.html", token=token)


@app.route("/logout", methods=["GET"])
def logout():
    """Logout route"""
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
