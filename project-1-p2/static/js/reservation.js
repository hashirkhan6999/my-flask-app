const dateInput = document.getElementById("date");
const timeInput = document.getElementById("time");

const today = new Date();
dateInput.min = today.toISOString().split("T")[0];

dateInput.addEventListener("change", () => {
  const selectedDate = new Date(dateInput.value);
  const now = new Date();

  let minTime = "09:00";
  let maxTime = "19:00";

  if (selectedDate.toDateString() === now.toDateString()) {
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const formattedCurrentTime = `${String(currentHour).padStart(
      2,
      "0"
    )}:${String(currentMinute).padStart(2, "0")}`;

    if (currentHour >= 9 && currentHour < 19) {
      minTime = formattedCurrentTime;
    } else if (currentHour >= 19) {
      minTime = "19:00";
    }
  }

  timeInput.min = minTime;
  timeInput.max = maxTime;
});
