function updateCountdowns() {
  const countdowns = document.querySelectorAll(".countdown");
  const now = new Date();

  countdowns.forEach((el) => {
    const createdStr = el.getAttribute("data-created");
    const createdDate = new Date(createdStr);

    const expirationDate = new Date(createdDate.getTime() + 30 * 60000);
    const diff = expirationDate - now;

    if (diff <= 0) {
      el.textContent = "Expired";
      el.classList.remove("countdown-active");
      el.classList.add("countdown-expired");
    } else {
      const minutes = Math.floor(diff / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);
      el.textContent =
        minutes + "m " + (seconds < 10 ? "0" : "") + seconds + "s";
      el.classList.remove("countdown-expired");
      el.classList.add("countdown-active");
    }
  });
}

setInterval(updateCountdowns, 1000);
updateCountdowns();
