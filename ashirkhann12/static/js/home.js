document.addEventListener("DOMContentLoaded", function () {
  const hamburger = document.getElementById("hamburger");
  const hdcross = document.getElementById("hdcross");
  const headerbar = document.getElementById("headerbar");

  hamburger.addEventListener("click", () => {
    headerbar.classList.add("active");
    hamburger.style.display = "none";
    hdcross.style.display = "inline";
  });

  hdcross.addEventListener("click", () => {
    headerbar.classList.remove("active");
    hamburger.style.display = "inline";
    hdcross.style.display = "none";
  });
});
