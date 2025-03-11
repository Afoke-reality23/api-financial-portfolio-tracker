const btn = document.getElementById("btn");
console.log(btn);

btn.addEventListener("click", () => {
  fetch("http://localhost:1998", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (response.ok) {
        console.log("it works");
      } else {
        console.log("request failed with status:", response.status);
      }
    })
    .catch((error) => {
      console.error("fetch error", error);
    });
});
