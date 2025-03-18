const btn = document.getElementById("btn");
const tale_data = document.querySelector(".id");
const tale_body = document.querySelector(".tbody");
console.log(tale_body);

btn.addEventListener("click", () => {
  fetch("http://localhost:1998/assets", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
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
      updateTable(data);
    })
    .catch((error) => {
      console.error("fetch error", error);
    });
});

function updateTable(datas) {
  for (data of datas) {
    const row = document.createElement("tr");
    const coin_id = document.createElement("th");
    coin_id.textContent = data.assets_id;
    const coin_log_symbol = document.createElement("th");
    coin_log_symbol.textContent = data.symbol;
    const price = document.createElement("th");
    price.textContent = data.price;
    // const last24Hr = document.createElement("th");
    row.appendChild(coin_id);
    row.appendChild(coin_log_symbol);
    row.appendChild(price);
    // row.appendChild(last24Hr);
    tale_body.appendChild(row);
  }
}
