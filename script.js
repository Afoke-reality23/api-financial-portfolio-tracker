const btn = document.getElementById("btn");
const tableBody = document.querySelector(".tbody");
console.log(tableBody);

// const num = 138369849;
// num3 = Math.floor(num, 2);

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
  try {
    for (data of datas) {
      console.log(data);
      const row = document.createElement("tr");
      const id = document.createElement("th");
      const marketCap = document.createElement("th");
      const iconSymbol = document.createElement("div");
      const symbol = document.createElement("span");
      const icon = document.createElement("img");
      const price = document.createElement("th");
      const percentChange24h = document.createElement("th");
      percentChange24h.textContent =
        Number((data.percent_change_24h / 100).toPrecision(3)) + "%";
      data.percent_change_24h;
      // icon.src = data.logo;
      id.textContent = data.id;
      symbol.textContent = data.symbol;
      price.textContent = Number(data.price.toPrecision(7)).toLocaleString(
        "en-US",
        { style: "currency", currency: "USD" }
      );
      iconSymbol.appendChild(icon);
      iconSymbol.appendChild(symbol);
      marketCap.appendChild(iconSymbol);
      row.appendChild(id);
      row.appendChild(marketCap);
      row.appendChild(price);
      row.appendChild(percentChange24h);
      tableBody.appendChild(row);
    }
  } catch (error) {
    console.error(error);
  }
}

// function data.percent_change_24hvalues) {
//   console.log(values);
//   if (values > 1e12) {
//     console.log("i am here ");
//     const value = (values / 1e12).toPrecision(2) + "T";
//     console.log(value);
//   }
//   // if (values >= 1e9) return (values / 1e12).toPrecision(2) + "B";
//   // if (values >= 1e6) return (values / 1e6).toPrecision(3) + "M";
//   // if (values >= 1e6) return (values / 1e5).toPrecision(3) + "k";
// }
