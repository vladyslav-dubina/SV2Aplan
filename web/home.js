//document.getElementById("button-name").addEventListener("click", ()=>{eel.get_random_name()}, false);

eel.expose(prompt_alerts);
function prompt_alerts(description) {
    alert(description);
}

const uploadButton = document.getElementById('uploadButton');
const fileInput = document.getElementById('fileInput');


uploadButton.addEventListener('click', function () {
    fileInput.click();
});

fileInput.addEventListener('change', function () {
    const files = fileInput.files;

    if (files.length > 0) {
        console.log('Selected file:', files[0]);
    }
});


function openTab(evt, tabName, buttonId) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        if (tabcontent[i].id != tabName) {
            tabcontent[i].style.display = "none";
        }
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab


    if (previousButtonId !== null && previousButtonId !== buttonId) {
        var previousArrow = document.getElementById(previousButtonId); // Знаходимо попередню стрілку
        previousArrow.classList.remove('rotate'); // Повертаємо її у початковий стан
    }


    var currentTab = document.getElementById(tabName);
    if (currentTab.style.display === "block") {
        currentTab.style.display = "none";
        evt.currentTarget.classList.remove("active");
    } else {
        currentTab.style.display = "block";
        evt.currentTarget.classList.add("active");
        if (tabName == "FT") {
        }
        if (tabName == "IP") {
        }
    }

    previousButtonId = buttonId;
    var arrow = document.getElementById(buttonId);
    arrow.classList.toggle('rotate');
}
