const btn = document.getElementById("btn");
console.log(btn);

btn.addEventListener("click", () => {
  fetch("http://localhost:1998/transaction?user_id=1&asset=Bitcoin", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    // body: JSON.stringify({
    //   user_id: 1,
    //   asset_id: 1,
    //   trans_type: "SELL",
    //   trans_quantity: 10,
    //   trans_price: 100,
    // })
  })
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
