# smile
nhóm 3 người
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# Dữ liệu phim đầy đủ
movies = [
    {
        "id": 1,
        "title": "Deadpool & Wolverine",
        "poster": "🎥",
        "date": "25/06/2026",
        "time": "18:00",
        "price": 130000,
        "hall": "Phòng 1",
        "actors": "Ryan Reynolds, Hugh Jackman",
        "desc": "Hai anh hùng hợp sức trong cuộc phiêu lưu hài hước và hành động đỉnh cao."
    },
    {
        "id": 2,
        "title": "Inside Out 2",
        "poster": "🎭",
        "date": "25/06/2026",
        "time": "20:30",
        "price": 110000,
        "hall": "Phòng 2",
        "actors": "Amy Poehler, Maya Hawke",
        "desc": "Câu chuyện cảm xúc mới của Riley và những cảm xúc bên trong."
    },
    {
        "id": 3,
        "title": "Despicable Me 4",
        "poster": "🤖",
        "date": "26/06/2026",
        "time": "16:00",
        "price": 95000,
        "hall": "Phòng 3",
        "actors": "Steve Carell, Kristen Wiig",
        "desc": "Gru và Minions tiếp tục những cuộc phiêu lưu hài hước."
    }
]

snacks = [
    {"name": "Bỏng ngô lớn", "price": 45000},
    {"name": "Bỏng ngô vừa", "price": 35000},
    {"name": "Coca Cola", "price": 25000},
    {"name": "Pepsi", "price": 25000},
    {"name": "Combo Bỏng + Nước", "price": 65000}
]

bookings = []

def open_movie_detail(movie):
    detail_win = tk.Toplevel(root)
    detail_win.title(movie["title"])
    detail_win.geometry("700x600")
    detail_win.configure(bg="#1f2937")

    tk.Label(detail_win, text=movie["poster"], font=("Arial", 60), bg="#1f2937").pack(pady=10)
    tk.Label(detail_win, text=movie["title"], font=("Arial", 18, "bold"), bg="#1f2937", fg="white").pack()
    tk.Label(detail_win, text=f"{movie['date']} | {movie['time']} | {movie['hall']}", bg="#1f2937", fg="#9ca3af").pack()
    tk.Label(detail_win, text=f"Diễn viên: {movie['actors']}", bg="#1f2937", fg="#eab308", font=("Arial", 11)).pack(pady=5)
    tk.Label(detail_win, text=movie["desc"], bg="#1f2937", fg="#d1d5db", wraplength=650, justify="left").pack(pady=10)

    # Chọn ghế
    tk.Label(detail_win, text="Chọn ghế ngồi", font=("Arial", 12, "bold"), bg="#1f2937", fg="white").pack(anchor="w", padx=20, pady=5)
    seat_frame = tk.Frame(detail_win, bg="#1f2937")
    seat_frame.pack(pady=5)
    selected_seats = []

    def toggle_seat(seat):
        if seat in selected_seats:
            selected_seats.remove(seat)
        else:
            selected_seats.append(seat)
        update_total()

    for i in range(1, 9):
        seat = f"A{i}"
        btn = tk.Button(seat_frame, text=seat, width=5, bg="#4b5563", fg="white", command=lambda s=seat: toggle_seat(s))
        btn.grid(row=0, column=i-1, padx=3, pady=3)

    # Đặt bỏng nước
    tk.Label(detail_win, text="🍿 Đặt đồ ăn", font=("Arial", 12, "bold"), bg="#1f2937", fg="white").pack(anchor="w", padx=20, pady=(15,5))
    snack_var = []
    for snack in snacks:
        var = tk.IntVar()
        snack_var.append((snack, var))
        tk.Checkbutton(detail_win, text=f"{snack['name']} - {snack['price']:,}đ", variable=var, bg="#1f2937", fg="#9ca3af", selectcolor="#ef4444").pack(anchor="w", padx=30)

    def confirm():
        total = len(selected_seats) * movie["price"]
        selected_snacks = [s[0]["name"] for s in snack_var if s[1].get() == 1]
        total += sum(s[0]["price"] for s in snack_var if s[1].get() == 1)

        booking = {
            "movieTitle": movie["title"],
            "date": movie["date"],
            "time": movie["time"],
            "seats": selected_seats,
            "snacks": selected_snacks,
            "total": total,
            "bookingDate": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        bookings.append(booking)
        messagebox.showinfo("Thành công", "Đặt vé thành công!")
        detail_win.destroy()
        show_bookings()

    tk.Button(detail_win, text="XÁC NHẬN ĐẶT VÉ", bg="#ef4444", fg="white", font=("Arial", 12, "bold"), command=confirm).pack(pady=20)

def update_total():
    pass  # Có thể mở rộng sau

def show_movies():
    for widget in movie_frame.winfo_children():
        widget.destroy()
    for movie in movies:
        frame = tk.Frame(movie_frame, bg="#1f2937", relief="raised", bd=2)
        frame.pack(fill="x", pady=8, padx=10)
        tk.Label(frame, text=movie["poster"], font=("Arial", 40), bg="#1f2937").pack(side="left", padx=15)
        tk.Label(frame, text=movie["title"], font=("Arial", 14, "bold"), bg="#1f2937", fg="white").pack(anchor="w")
        tk.Label(frame, text=f"{movie['date']} | {movie['time']}", bg="#1f2937", fg="#9ca3af").pack(anchor="w")
        tk.Button(frame, text="Chi tiết & Đặt vé", bg="#ef4444", fg="white", command=lambda m=movie: open_movie_detail(m)).pack(side="right", padx=10, pady=8)

def show_bookings():
    for widget in history_frame.winfo_children():
        widget.destroy()
    if not bookings:
        tk.Label(history_frame, text="Chưa có vé nào.", bg="#111827", fg="#9ca3af").pack(pady=30)
        return
    for b in bookings:
        frame = tk.Frame(history_frame, bg="#1f2937", relief="ridge")
        frame.pack(fill="x", pady=6, padx=10)
        tk.Label(frame, text=b["movieTitle"], font=("Arial", 12, "bold"), bg="#1f2937", fg="white").pack(anchor="w", padx=10)
        tk.Label(frame, text=f"Ghế: {', '.join(b.get('seats', ['N/A']))}", bg="#1f2937", fg="#eab308").pack(anchor="w", padx=10)
        tk.Label(frame, text=f"Tổng: {b['total']:,} VNĐ".replace(",", "."), bg="#1f2937", fg="#22c55e").pack(anchor="w", padx=10)

root = tk.Tk()
root.title("Cinema Ticket Booking System")
root.geometry("1000x700")
root.configure(bg="#111827")

tk.Label(root, text="🎬 CINEMA TICKET BOOKING SYSTEM", font=("Arial", 26, "bold"), bg="#111827", fg="#ef4444").pack(pady=20)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=10)

movie_tab = tk.Frame(notebook, bg="#111827")
notebook.add(movie_tab, text="🎥 Danh sách Phim")
movie_frame = tk.Frame(movie_tab, bg="#111827")
movie_frame.pack(fill="both", expand=True)

history_tab = tk.Frame(notebook, bg="#111827")
notebook.add(history_tab, text="📜 Lịch sử Đặt Vé")
history_frame = tk.Frame(history_tab, bg="#111827")
history_frame.pack(fill="both", expand=True)

show_movies()
show_bookings()

root.mainloop()
