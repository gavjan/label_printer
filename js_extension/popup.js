// content.js
const url = window.location.href;

document.addEventListener("keydown", function (event) {
  if (event.ctrlKey && event.shiftKey && event.key === "S") {
    const button = document.querySelector(".details-buy button");
    if(button) {
        button.click();
    }
  }
});

const button = document.createElement("button");
button.style.backgroundColor = "blue";
button.style.color = "white";
button.style.fontSize = "18px";  // Adjust the font size as needed
button.style.padding = "10px";   // Add some padding for a bigger button
button.style.display = "block";  // Move to a new line
button.textContent = "Print Label";
button.title = "Ctrl + Shift + S";
button.onclick = function () {
    if (button.disabled) return;
    button.disabled = true;
    button.style.backgroundColor = "gray";

  fetch("https://192.168.1.102:6969", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ url: url, trailing_blank: trailingBlank.checked ? 1:0})
  })
    .then(response => {
      if (!response.ok) {
          if (response.status === 409) throw new Error("Server busy");
          if (response.status === 500)
              return response.json().then(data => {throw new Error("Internal Error: " + JSON.stringify(data))});
          else throw new Error("Bad response");
      }
      return response.json();
    })
    .then(data => {
        button.style.backgroundColor = "blue";
        button.disabled = false;
        console.log("Response from server:", data);
    })
  .catch(error => {
      if (error.message === "Server busy") alert("Already printing");
      else if(error.message === "Failed to fetch") alert("Server offline");
      else if (error.message.indexOf("Internal Error:") !== -1) {
          console.error(error.message);
          alert("Server Error occurred. Check console for details.");
      }
      button.style.backgroundColor = "blue";
      button.disabled = false;
  });
};

// Create the trailingBlank element
const trailingBlank = document.createElement("input");
trailingBlank.type = "checkbox";
trailingBlank.textContent = "Trailing blank";
chrome.storage.sync.get(['trailing_blank'], function(result) {
    if (!result || result.trailing_blank === undefined)
        chrome.storage.sync.set({ trailing_blank: false }, () => trailingBlank.checked = false);
    else
        trailingBlank.checked = result.trailing_blank || false;
});
trailingBlank.addEventListener("change", function() {
  const trailing_flag = trailingBlank.checked;
  chrome.storage.sync.set({ trailing_blank: trailing_flag }, function() {
    console.log('Trailing Blank:', trailing_flag);
  });
});





const labelElement = document.createElement("label");
labelElement.textContent = "Trailing blank";



const detailsBuyDiv = document.querySelector(".details-buy");
detailsBuyDiv.appendChild(button);
detailsBuyDiv.appendChild(trailingBlank);
detailsBuyDiv.appendChild(labelElement);


