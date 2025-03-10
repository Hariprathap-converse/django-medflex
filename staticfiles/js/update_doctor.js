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

form.addEventListener("submit", function (event) {
  event.preventDefault();
});

function validateForm() {
  let isValid = true;

  function showError(input, message) {
    if (input == "male") {
      const genderContainer = document.querySelector(".gender-container");

      genderContainer.previousElementSibling.classList.remove("hidden");
      genderContainer.previousElementSibling.textContent = message;
      isValid = false;
      document.querySelectorAll('input[name="gender"]').forEach((radio) => {
        radio.addEventListener("change", function () {
          genderContainer.previousElementSibling.classList.add("hidden");
          genderContainer.previousElementSibling.textContent = "";
        });
      });
    } else {
      const data = document.getElementById(input.id);

      data.parentNode.classList.add("error-border");
      const c = data.parentNode;
      c.previousElementSibling.classList.remove("hidden");
      c.previousElementSibling.textContent = message;
      input.focus();
      isValid = false;

      input.addEventListener("input", function () {
        input.parentNode.classList.remove("error-border");
        c.previousElementSibling.classList.add("hidden");
        c.previousElementSibling.textContent = "";
      });
    }
  }

  const firstName = document.getElementById("first-name");
  if (!firstName.value.trim()) showError(firstName, "First Name is Required");

  const lastName = document.getElementById("last-name");
  if (!lastName.value.trim()) showError(lastName, "Last Name is Required");

  const age = document.getElementById("age");

  if (!age.value) {
    showError(age, "Please select your Age");
  } else {
    const ageValue = parseInt(age.value, 10); // Convert input to number

    if (isNaN(ageValue) || ageValue < 23 || ageValue >= 100) {
      showError(
        age,
        "Please provide a valid age (must be above 23 and below 100)."
      );
    }
  }

  const gender = document.querySelector("input[name='gender']:checked");
  console.log(gender);
  if (!gender) showError("male", "Please select Your Gender");

  const createId = document.getElementById("create-id");
  if (!createId.value.trim()) showError(createId, "Create ID is Required");

  const email = document.getElementById("email");
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email.value.trim()) {
    showError(email, "Email field is Required");
  } else if (!emailPattern.test(email.value)) {
    showError(email, "Enter a valid Email ID");
  }

  const mobile = document.getElementById("mobile");
  const countryCode = document.getElementById("country-code");

  if (!mobile.value.trim()) {
    showError(mobile, "Mobile number is required");
  } else if (mobile.value.length !== 10) {
    showError(mobile, "Enter a valid 10-digit Mobile Number");
  } else if (!countryCode.value) {
    countryCode.focus();
    console.log("countryCode", countryCode);
    showError(mobile, "Please select a country code");
  } else {
    const fullMobileNumberInput = document.getElementById("full_mobile_number");
    const fullMobileNumber = countryCode.value + mobile.value;
    console.log("Full Mobile Number:", fullMobileNumber);

    fullMobileNumberInput.value = fullMobileNumber;
  }

  const bloodGroup = document.getElementById("blood");
  if (bloodGroup.value == "")
    showError(bloodGroup, "Please Select a Blood Group");

  return isValid;
}

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

for (var item of document.querySelectorAll(".nav-options li")) {
  item.addEventListener(
    "click",
    function (evt) {
      evt.target.classList.toggle("active");
    },
    false
  );
}

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-upload");

dropzone.addEventListener("click", function () {
  fileInput.click();
});

const personalDetailsForm = document.querySelector(".personal-details");
const profileContainerForm = document.querySelector(".profile-details");
const availableContainerForm = document.querySelector(".available-details");
const accountContainerForm = document.querySelector(".account-details");
const profileNav = document.getElementById("profile-nav");
const personalNav = document.getElementById("personal-nav");
const availableNav = document.getElementById("available-nav");
const accountNav = document.getElementById("account-nav");

function toggleForms(clickedElement) {
  if (clickedElement.classList.contains("personal-nav")) {
    personalDetailsForm.classList.remove("hidden");
    profileContainerForm.classList.add("hidden");
    profileNav.classList.remove("active");
    personalNav.classList.add("active");
    availableNav.classList.remove("active");
    availableContainerForm.classList.add("hidden");
    accountNav.classList.remove("active");
    accountContainerForm.classList.add("hidden");
  } else if (clickedElement.classList.contains("profile-nav")) {
    personalDetailsForm.classList.add("hidden");
    profileContainerForm.classList.remove("hidden");
    initializeQuill();
    profileNav.classList.add("active");
    personalNav.classList.remove("active");
    availableNav.classList.remove("active");
    availableContainerForm.classList.add("hidden");
    accountNav.classList.remove("active");
    accountContainerForm.classList.add("hidden");
  } else if (clickedElement.classList.contains("available-nav")) {
    accountNav.classList.remove("active");
    accountContainerForm.classList.add("hidden");
    personalDetailsForm.classList.add("hidden");
    profileContainerForm.classList.add("hidden");
    profileNav.classList.remove("active");
    personalNav.classList.remove("active");
    availableNav.classList.add("active");
    availableContainerForm.classList.remove("hidden");
  } else if (clickedElement.classList.contains("account-nav")) {
    accountNav.classList.add("active");
    accountContainerForm.classList.remove("hidden");
    personalDetailsForm.classList.add("hidden");
    profileContainerForm.classList.add("hidden");
    profileNav.classList.remove("active");
    personalNav.classList.remove("active");
    availableNav.classList.remove("active");
    availableContainerForm.classList.add("hidden");
  }
}

// Function to initialize Quill only when needed
function initializeQuill() {
  console.log("initializeQuill() is running..."); // Debugging log

  if (typeof Quill === "undefined") {
    console.error("Quill.js is not loaded properly.");
    return;
  }

  console.log("Quill.js is loaded successfully!");

  var editorContainer = document.querySelector("#editor-container");
  var toolbar = document.querySelector("#toolbar");
  var bioInput = document.querySelector("#bio-input");
  var form = profileContainerForm;

  if (!editorContainer || !toolbar || !bioInput || !form) {
    console.error(
      "Required elements (editor, toolbar, bio-input, or form) are missing."
    );
    return;
  }

  var quill = new Quill("#editor-container", {
    theme: "snow",
    placeholder: "Write something...",
    modules: {
      toolbar: "#toolbar",
    },
  });

  document.getElementById("profile-details").onsubmit = async function (e) {
    e.preventDefault();
    document.getElementById("bio-input").value = quill.root.innerHTML;

    let formData = new FormData(profileContainerForm);
    let step = this.dataset.step;
    console.log("step", step);
    formData.append("step", step);
    let response = await fetch(profileContainerForm.action, {
      method: "PUT",
      body: formData,
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
    });

    if (response.ok) {
      profileNav.classList.remove("active");
      profileContainerForm.classList.add("hidden");
      availableNav.classList.add("active");
      availableContainerForm.classList.remove("hidden");
    } else {
      alert("Error: " + JSON.stringify(response));
      console.log(response.error);
    }
  };
}

profileNav.addEventListener("click", function () {
  toggleForms(this);
});

personalNav.addEventListener("click", function () {
  toggleForms(this);
});

availableNav.addEventListener("click", function () {
  toggleForms(this);
});

accountNav.addEventListener("click", function () {
  toggleForms(this);
});

availableContainerForm.addEventListener("submit", async function (event) {
  event.preventDefault();
  const formData = new FormData(availableContainerForm);
  let step = this.dataset.step;
  console.log("step", step);
  formData.append("step", step);

  try {
    const response = await fetch(availableContainerForm.action, {
      method: "PUT",
      body: formData,
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
    });
    console.log(response);
    if (response.ok) {
      availableNav.classList.remove("active");
      availableContainerForm.classList.add("hidden");
      accountNav.classList.add("active");
      accountContainerForm.classList.remove("hidden");
    } else {
      availableContainerForm.submit();
    }
  } catch (error) {
    console.error("Error submitting form:", error);
  }
});

personalDetailsForm.addEventListener("submit", async function (event) {
    event.preventDefault();
  
    if (validateForm()) {
      const formData = new FormData(personalDetailsForm);
      let step = this.dataset.step;
      formData.append("step", step);
  
      try {
        const response = await fetch(personalDetailsForm.action, {
          method: "PUT",
          body: formData,
          headers: {
            "X-CSRFToken": getCSRFToken(), 
          },
        });
  
        const responseData = await response.json();
        console.log("Response Data:", responseData);
  
        if (response.ok && responseData.success) {
          personalDetailsForm.classList.add("hidden");
          profileContainerForm.classList.remove("hidden");
          initializeQuill();
          profileNav.classList.add("active");
          personalNav.classList.remove("active");
        } else {
          console.error("Update failed:", responseData.errors );
        }
      } catch (error) {
        console.error("Error submitting form:", error);
      }
    }
  });
  

function getCSRFToken() {
  let cookieValue = null;
  let cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    let cookie = cookies[i].trim();
    if (cookie.startsWith("csrftoken=")) {
      cookieValue = cookie.substring("csrftoken=".length, cookie.length);
      break;
    }
  }
  return cookieValue;
}

document
  .getElementById("file-upload")
  .addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const clickMessage = document.querySelector(".dz-message");
        clickMessage.innerHTML = "";
        const img = document.getElementById("preview-image");
        img.src = e.target.result;
        img.classList.remove("hidden");
      };
      reader.readAsDataURL(file);
    }
  });

document.getElementById("eye-icon").addEventListener("click", function () {
  const passwordContainer = document.getElementById("password");
  const closeEye = document.querySelector(".eye-open");
  if (passwordContainer.type == "password") {
    passwordContainer.type = "text";
    closeEye.classList.remove("ri-eye-off-line");
    closeEye.classList.add("ri-eye-line");
  } else {
    passwordContainer.type = "password";
    closeEye.classList.add("ri-eye-off-line");
    closeEye.classList.remove("ri-eye-line");
  }
});



document.getElementById("eye-icon1").addEventListener("click", function () {
  const passwordContainer = document.getElementById("confirm_password");
  const closeEye = document.querySelector(".eye-close");
  if (passwordContainer.type == "password") {
    passwordContainer.type = "text";
    closeEye.classList.remove("ri-eye-off-line");
    closeEye.classList.add("ri-eye-line");
  } else {
    passwordContainer.type = "password";
    closeEye.classList.add("ri-eye-off-line");
    closeEye.classList.remove("ri-eye-line");
  }
});



accountContainerForm.addEventListener("submit", async function (event) {
  event.preventDefault();
  console.log("enter");
  const formData = new FormData(accountContainerForm);
  let step = this.dataset.step;
  console.log("step", step);
  formData.append("step", step);
  console.log("formData", formData);

  try {
    const response = await fetch(accountContainerForm.action, {
      method: "PUT",
      body: formData,
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
    });

    console.log("response out", response);

    if (response.ok) {
      alert("Updated successfully!");
    } else {
      console.log("first");
      const data = await response.json();
      for (const field in data.errors) {
        const errorElement = document.getElementById(`${field}_error`);
        const inputField = document.getElementById(field);

        if (errorElement) {
          errorElement.innerText = data.errors[field][0];
        }
        if (inputField) {
          errorElement.nextElementSibling.classList.add("error-border");

          inputField.addEventListener("input", function () {
            if (errorElement) errorElement.innerText = "";
            errorElement.nextElementSibling.classList.remove("error-border");
          });
        }
      }
    }
  } catch (error) {
    console.log("Error submitting form:", error);
  }
});


document.querySelectorAll(".nav-container2 div").forEach((item) => {
  item.addEventListener("click", function () {
    document
      .querySelectorAll(".nav-container2 div")
      .forEach((div) => div.classList.remove("data-today"));

    this.classList.add("data-today");
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

