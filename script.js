const btn = document.getElementById("btn");
console.log(btn);

btn.addEventListener("click", () => {
  fetch(
    "http://localhost:1998/portfolio?user_id=3&asset_id=4&trans_type=SELL&trans_quantity=200&trans_price=1800",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
    .then((response) => {
      if (response.ok) {
        console.log("it works");
        return response.json();
      } else {
        console.log("request failed with status:", response.status);
      }
    })
    .then((data) => {
      console.log(data);
    })
    .catch((error) => {
      console.error("fetch error", error);
    });
});
