from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask("movie_booking")
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_db_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        port=Config.MYSQL_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )


def is_admin():
    return session.get("role") == "admin"


@app.route("/")
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies ORDER BY id DESC")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", movies=movies)


@app.route("/movies")
def movies():
    keyword = request.args.get("q", "")

    conn = get_db_connection()
    cursor = conn.cursor()

    if keyword:
        cursor.execute(
            "SELECT * FROM movies WHERE title LIKE %s OR genre LIKE %s ORDER BY id DESC",
            (f"%{keyword}%", f"%{keyword}%")
        )
    else:
        cursor.execute("SELECT * FROM movies ORDER BY id DESC")

    movies = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("movies.html", movies=movies, keyword=keyword)


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies WHERE id=%s", (movie_id,))
    movie = cursor.fetchone()

    cursor.close()
    conn.close()

    if movie is None:
        return "Không tìm thấy phim"

    return render_template("movie_detail.html", movie=movie)


@app.route("/booking/<int:movie_id>", methods=["GET", "POST"])
def booking(movie_id):
    if "user_id" not in session:
        flash("Bạn cần đăng nhập để đặt vé!", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies WHERE id=%s", (movie_id,))
    movie = cursor.fetchone()

    if movie is None:
        cursor.close()
        conn.close()
        return "Không tìm thấy phim"

    cursor.execute("SELECT seat FROM tickets WHERE movie_id=%s", (movie_id,))
    booked_rows = cursor.fetchall()
    booked_seats = [row["seat"].upper() for row in booked_rows]

    if request.method == "POST":
        showtime = request.form["showtime"]
        seat = request.form["seat"].upper()

        if not seat:
            flash("Bạn chưa chọn ghế!", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for("booking", movie_id=movie_id))

        if seat in booked_seats:
            flash("Ghế này đã được đặt!", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for("booking", movie_id=movie_id))

        cursor.execute(
            """
            INSERT INTO tickets(user_id, movie_id, showtime, seat)
            VALUES(%s, %s, %s, %s)
            """,
            (session["user_id"], movie_id, showtime, seat)
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash("Đặt vé thành công!", "success")
        return redirect(url_for("history"))

    cursor.close()
    conn.close()

    return render_template(
        "booking.html",
        movie=movie,
        booked_seats=booked_seats
    )


@app.route("/history")
def history():
    if "user_id" not in session:
        flash("Bạn cần đăng nhập để xem lịch sử đặt vé!", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT tickets.*, movies.title
        FROM tickets
        JOIN movies ON tickets.movie_id = movies.id
        WHERE tickets.user_id = %s
        ORDER BY tickets.booking_time DESC
        """,
        (session["user_id"],)
    )

    tickets = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("history.html", tickets=tickets)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            flash("Email đã tồn tại!", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users(fullname, email, phone, password, role)
            VALUES(%s, %s, %s, %s, %s)
            """,
            (fullname, email, phone, hashed_password, "user")
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["fullname"] = user["fullname"]
            session["role"] = user["role"]

            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("home"))

        flash("Sai email hoặc mật khẩu!", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất!", "info")
    return redirect(url_for("home"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Bạn cần đăng nhập!", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, fullname, email, phone, role FROM users WHERE id=%s",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("profile.html", user=user)


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        flash("Bạn cần đăng nhập!", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("Mật khẩu xác nhận không khớp!", "danger")
            return redirect(url_for("change_password"))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
        user = cursor.fetchone()

        if not check_password_hash(user["password"], old_password):
            flash("Sai mật khẩu cũ!", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for("change_password"))

        hashed = generate_password_hash(new_password)

        cursor.execute(
            "UPDATE users SET password=%s WHERE id=%s",
            (hashed, session["user_id"])
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash("Đổi mật khẩu thành công!", "success")
        return redirect(url_for("profile"))

    return render_template("change_password.html")


@app.route("/admin")
def admin_dashboard():
    if not is_admin():
        flash("Bạn không có quyền truy cập trang Admin!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM movies")
    total_movies = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM users")
    total_users = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM tickets")
    total_tickets = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM tickets WHERE status='Đã đặt'")
    total_booked = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return render_template(
        "admin/dashboard.html",
        total_movies=total_movies,
        total_users=total_users,
        total_tickets=total_tickets,
        total_booked=total_booked
    )


@app.route("/admin/movies")
def admin_movies():
    if not is_admin():
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies ORDER BY id DESC")
    movies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/movies.html", movies=movies)


@app.route("/admin/movies/add", methods=["GET", "POST"])
def admin_add_movie():
    if not is_admin():
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        duration = request.form["duration"]
        release_date = request.form["release_date"]
        description = request.form["description"]
        poster = request.form["poster"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO movies(title, genre, duration, release_date, description, poster)
            VALUES(%s, %s, %s, %s, %s, %s)
            """,
            (title, genre, duration, release_date, description, poster)
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash("Thêm phim thành công!", "success")
        return redirect(url_for("admin_movies"))

    return render_template("admin/add_movie.html")


@app.route("/admin/movies/edit/<int:movie_id>", methods=["GET", "POST"])
def admin_edit_movie(movie_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies WHERE id=%s", (movie_id,))
    movie = cursor.fetchone()

    if movie is None:
        cursor.close()
        conn.close()
        flash("Không tìm thấy phim!", "danger")
        return redirect(url_for("admin_movies"))

    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        duration = request.form["duration"]
        release_date = request.form["release_date"]
        description = request.form["description"]
        poster = request.form["poster"]

        cursor.execute(
            """
            UPDATE movies
            SET title=%s, genre=%s, duration=%s, release_date=%s, description=%s, poster=%s
            WHERE id=%s
            """,
            (title, genre, duration, release_date, description, poster, movie_id)
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash("Cập nhật phim thành công!", "success")
        return redirect(url_for("admin_movies"))

    cursor.close()
    conn.close()

    return render_template("admin/edit_movie.html", movie=movie)


@app.route("/admin/movies/delete/<int:movie_id>")
def admin_delete_movie(movie_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tickets WHERE movie_id=%s", (movie_id,))
    cursor.execute("DELETE FROM movies WHERE id=%s", (movie_id,))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Xóa phim thành công!", "success")
    return redirect(url_for("admin_movies"))


@app.route("/admin/tickets")
def admin_tickets():
    if not is_admin():
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT tickets.*, movies.title, users.fullname, users.email
        FROM tickets
        JOIN movies ON tickets.movie_id = movies.id
        JOIN users ON tickets.user_id = users.id
        ORDER BY tickets.booking_time DESC
        """
    )

    tickets = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/tickets.html", tickets=tickets)


@app.route("/admin/tickets/delete/<int:ticket_id>")
def admin_delete_ticket(ticket_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tickets WHERE id=%s", (ticket_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Xóa vé thành công!", "success")
    return redirect(url_for("admin_tickets"))


@app.route("/admin/users")
def admin_users():
    if not is_admin():
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, fullname, email, phone, role FROM users ORDER BY id DESC")
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/users.html", users=users)


@app.route("/admin/users/set-admin/<int:user_id>")
def admin_set_admin(user_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET role='admin' WHERE id=%s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Đã cấp quyền Admin!", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/set-user/<int:user_id>")
def admin_set_user(user_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET role='user' WHERE id=%s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Đã chuyển về quyền User!", "success")
    return redirect(url_for("admin_users"))


if __name__ == "__main__":
    app.run(debug=True)
