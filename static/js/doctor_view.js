
const logoutContainer = document.getElementById("profile");
const profileContainer = document.getElementById("profile-container");
const loaderContainer = document.getElementById("loading-wrapper");
const contant = document.querySelector(".contant");
const navBarIcon = document.getElementById("logo-conatiner");
const parentContainer = document.getElementById("parent-wrapper");
const navBar = document.getElementById("navbar-wrapper");

console.log(navBarIcon);
console.log(navBar);
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



document.addEventListener("DOMContentLoaded", function () {
  let paginationLinks = document.querySelectorAll(".pagination a");

  paginationLinks.forEach(function (link) {
    link.addEventListener("click", function (event) {
    

      let url = this.getAttribute("href");
      window.location.href = url; 
    });
  });
});

let debounceTimer;
document.getElementById("search-input").addEventListener("input", function () {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    let searchValue = this.value;
    let url = new URL(window.location.href);
    url.searchParams.set("search", searchValue);
    window.location.href = url.href;
  }, 300);
});

let searchInput = document.getElementById("search-input");
if (searchInput.value.trim() !== "") {

  searchInput.focus();
}
function sortTable(column) {
  let url = new URL(window.location.href);
  let currentOrder = url.searchParams.get("order") || "asc";
  let newOrder = currentOrder === "asc" ? "desc" : "asc";

  url.searchParams.set("sort_by", column);
  url.searchParams.set("order", newOrder);

  window.location.href = url.href; // Refresh the page with the new sorting parameters
}

document.querySelectorAll('.nav-container2 div').forEach(item => {
  item.addEventListener('click', function() {

    document.querySelectorAll('.nav-container2 div').forEach(div => div.classList.remove('data-today'));

    this.classList.add('data-today');
  });
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


document.addEventListener("DOMContentLoaded", function () {
  const doctorMenu = document.querySelector(".doctor-main");
  const optionContainer = document.querySelector(".doctor-options");

  // Ensure it's hidden initially
  optionContainer.style.maxHeight = "0px";
  optionContainer.classList.remove("hidden");

  doctorMenu.addEventListener("click", function () {
    if (optionContainer.style.maxHeight === "0px") {
      // Opening smoothly
      doctorMenu.classList.add("active");
      optionContainer.style.overflow = "hidden"; // Prevent content flashing
      optionContainer.style.maxHeight = optionContainer.scrollHeight + "px";
    } else {
      // Closing smoothly
      optionContainer.style.maxHeight = optionContainer.scrollHeight + "px"; // Set current height
      optionContainer.style.overflow = "hidden"; 
      requestAnimationFrame(() => {
        optionContainer.style.maxHeight = "0px"; // Collapse smoothly
      });

      doctorMenu.classList.remove("active"); // Remove active class when closed
    }
  });

  // Reset maxHeight after opening to allow dynamic content resizing
  optionContainer.addEventListener("transitionend", function () {
    if (optionContainer.style.maxHeight !== "0px") {
      optionContainer.style.maxHeight = "none"; 
      optionContainer.style.overflow = "visible"; 
    } else {
      optionContainer.style.overflow = "hidden"; 
    }
  });
});



