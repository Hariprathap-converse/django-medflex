

document.addEventListener("DOMContentLoaded", function () {
    const wrapper = document.querySelector(".awards-images-wrapper");
    const images = document.querySelectorAll(".awards-images-wrapper img");
    const indicators = document.querySelectorAll(".indicators button");
    const leftButton = document.querySelector(".right-button");
    const rightButton = document.querySelector(".left-button");
    let currentIndex = 0;
    let interval;

    function updateSlider(index) {
        wrapper.style.transform = `translateX(-${index * 100}%)`;
        indicators.forEach((btn, i) => btn.classList.toggle("active-opacity", i === index));
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % images.length;
        updateSlider(currentIndex);
    }

    function prevSlide() {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        updateSlider(currentIndex);
    }

    function startAutoSlide() {
        interval = setInterval(nextSlide, 5000);
    }

    function stopAutoSlide() {
        clearInterval(interval);
    }

    rightButton.addEventListener("click", () => {
        stopAutoSlide();
        nextSlide();
        startAutoSlide();
    });

    leftButton.addEventListener("click", () => {
        stopAutoSlide();
        prevSlide();
        startAutoSlide();
    });

    indicators.forEach((btn, i) => {
        btn.addEventListener("click", () => {
            stopAutoSlide();
            currentIndex = i;
            updateSlider(currentIndex);
            startAutoSlide();
        });
    });

    updateSlider(currentIndex);
    startAutoSlide();
});


////
const logoutContainer = document.getElementById("profile");
const profileContainer = document.getElementById("profile-container");
const loaderContainer = document.getElementById("loading-wrapper");
const contant = document.querySelector(".contant");
const navBarIcon = document.getElementById("logo-conatiner");
const parentContainer = document.getElementById("parent-wrapper");
const navBar = document.getElementById("navbar-wrapper");
const form = document.querySelector("form");

setTimeout(function () {
  loaderContainer.id = "hidden";
}, 1000);

let isClicked = false;

logoutContainer.addEventListener("click", function () {
  isClicked = !isClicked;
  profileContainer.classList.toggle("hidden", !isClicked);
});

logoutContainer.addEventListener("mouseover", function () {
  if (!isClicked) {
    profileContainer.classList.remove("hidden");
  }
});

logoutContainer.addEventListener("mouseout", function () {
  if (!isClicked) {
    profileContainer.classList.add("hidden");
  }
});
profileContainer.addEventListener("mouseover", function () {
  profileContainer.classList.remove("hidden");
});
profileContainer.addEventListener("mouseout", function () {
  if (!isClicked) {
    profileContainer.classList.add("hidden");
  }
});
document.addEventListener("click", function (event) {
  if (
    !logoutContainer.contains(event.target) &&
    !profileContainer.contains(event.target)
  ) {
    isClicked = false;
    profileContainer.classList.add("hidden");
  }
});


navBarIcon.addEventListener("click", function (event) {
  const parentWrapper = document.getElementById("parent-wrapper");
  const mainContainer = document.querySelector(".main-container");
  if (parentWrapper && parentWrapper.classList.contains("pinned")) {
    navBar.classList.toggle("pinned-active");
    mainContainer.classList.toggle("pinned-main");
  } else {
    navBar.classList.toggle("active");
  }
});

function handleResize() {
  let width = window.innerWidth; // Use `window.innerWidth` for live updates
  const parentWrapper = document.getElementById("parent-wrapper");

  if (parentWrapper) {
    if (width >= 1200) {
      parentWrapper.classList.add("pinned");
      navBar.classList.add('active')
    } else {
      parentWrapper.classList.remove("pinned");
    }
  }
}

handleResize();

window.addEventListener("resize", handleResize);


document.querySelectorAll(".nav-container2 div").forEach((item) => {
  item.addEventListener("click", function () {
    document
      .querySelectorAll(".nav-container2 div")
      .forEach((div) => div.classList.remove("data-today"));

    this.classList.add("data-today");
  });
});


document.addEventListener("DOMContentLoaded", function () {
  const doctorMenu = document.querySelector(".doctor-main");
  const optionContainer = document.querySelector(".doctor-options");

  optionContainer.style.maxHeight = "0px";
  optionContainer.classList.remove("hidden");

  doctorMenu.addEventListener("click", function () {
    if (optionContainer.style.maxHeight === "0px") {

      doctorMenu.classList.add("active");
      optionContainer.style.overflow = "hidden"; 
      optionContainer.style.maxHeight = optionContainer.scrollHeight + "px";
    } else {
      optionContainer.style.maxHeight = optionContainer.scrollHeight + "px"; 
      optionContainer.style.overflow = "hidden"; 
      requestAnimationFrame(() => {
        optionContainer.style.maxHeight = "0px";
      });

      doctorMenu.classList.remove("active"); 
    }
  });

  optionContainer.addEventListener("transitionend", function () {
    if (optionContainer.style.maxHeight !== "0px") {
      optionContainer.style.maxHeight = "none"; 
      optionContainer.style.overflow = "visible"; 
    } else {
      optionContainer.style.overflow = "hidden"; 
    }
  });
});

