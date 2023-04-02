document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".collapsible");
    
    [...buttons].forEach(element => {
        element.addEventListener("click", () => {
            element.classList.toggle("active");

            const content = element.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    })
  });