document.addEventListener("DOMContentLoaded", function () {
  const hamburger = document.getElementById("hamburger");
  const hdcross = document.getElementById("hdcross");
  const navMenu = document.getElementById("navMenu");

  if (hamburger && hdcross && navMenu) {
    hamburger.addEventListener("click", () => {
      navMenu.classList.add("active");
      hamburger.style.display = "none";
      hdcross.style.display = "inline";
    });

    hdcross.addEventListener("click", () => {
      navMenu.classList.remove("active");
      hamburger.style.display = "inline";
      hdcross.style.display = "none";
    });
  } else {
    console.warn("Menu toggle elements not found in DOM.");
  }
});
