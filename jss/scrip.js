function chooseSeat(seat, button) {
    document.getElementById("selectedSeat").value = seat;
    document.getElementById("seatText").innerText = seat;

    let buttons = document.querySelectorAll(".seat-btn");

    buttons.forEach(function(btn) {
        btn.classList.remove("btn-success");
        btn.classList.add("btn-outline-primary");
    });

    button.classList.remove("btn-outline-primary");
    button.classList.add("btn-success");
}
