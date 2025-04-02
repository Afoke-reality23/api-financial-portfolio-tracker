document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("btn");
  const tableBody = document.querySelector(".tbody");
  const hamburger = document.querySelector(".hamburger");
  const clsBtn = document.querySelector(".cls-menu");
  const menu = document.querySelector(".nav-bar");
  hamburger.addEventListener("click", () => (menu.style.display = "flex"));
  clsBtn.addEventListener("click", () => (menu.style.display = "none"));
  fetchAssets();
  function fetchAssets() {
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
        // console.log(data);
        updateTable(data);
      })
      .catch((error) => {
        console.error("fetch error", error);
      });
  }
  function updateTable(datas) {
    try {
      let incrementId = 1;
      for (data of datas) {
        // console.log(data);
        const row = document.createElement("tr");
        row.classList.add("row");
        const id = document.createElement("td");
        const asset = document.createElement("td");
        const marketCap = document.createElement("td");
        const iconSymbol = document.createElement("div");
        const icon = document.createElement("img");
        const symbolMarketCap = document.createElement("div");
        const symbol = document.createElement("span");
        const marketCapNum = document.createElement("span");
        const price = document.createElement("td");
        const percentChange24h = document.createElement("td");
        id.textContent = incrementId++;
        asset.textContent = data.assets_name;
        // icon.src = data.logo;
        symbol.textContent = data.symbol;
        marketCapNum.textContent = roundMarketCap(data.market_cap).trim();
        // marketCap.setAttribute("colspan", "3");
        percentChange24h.textContent =
          Number(data.percent_change_24h.toPrecision(3)) + "%".trim();
        if (data.percent_change_24h < 0) {
          percentChange24h.style.color = "red";
        } else {
          percentChange24h.style.color = "green";
        }
        symbolMarketCap.textContent = data.symbolMarketCap;
        price.textContent = Number(data.price.toPrecision(7)).toLocaleString(
          "en-US",
          { style: "currency", currency: "USD" }
        );
        symbolMarketCap.appendChild(symbol);
        symbolMarketCap.classList.add("symbol-market-cap");
        symbolMarketCap.appendChild(marketCapNum);
        iconSymbol.appendChild(icon);
        iconSymbol.appendChild(symbolMarketCap);
        iconSymbol.classList.add("icon-symbol");
        marketCap.appendChild(iconSymbol);
        row.appendChild(id);
        row.appendChild(asset);
        row.appendChild(marketCap);
        row.appendChild(price);
        row.appendChild(percentChange24h);
        tableBody.appendChild(row);
        // return row;
      }
    } catch (error) {
      console.error(error);
    }
  }
  //add eventlistener to row to view asset details

  console.log(tableBody);
  const observer = new MutationObserver(() => {
    const rows = document.querySelectorAll(".tbody .row");
    rows.forEach((row) => {
      const tds = row.querySelectorAll("td");
      assetId = tds[0].textContent;
      row.setAttribute(
        "onclick",
        `window.location='assetdetail.html?id=${assetId}'`
      );
    });
  });
  observer.observe(tableBody, { childList: true, subtree: true });
  function roundMarketCap(value) {
    if (value > 1e12) return (value / 1e12).toPrecision(2) + "T";
    if (value > 1e9) return (value / 1e9).toPrecision(3) + "B";
    if (value > 1e6) return (value / 1e6).toPrecision(3) + "M";
    if (value > 1e5) return (value / 1e5).toPrecision(3) + "K";
    if ((value = 1e4)) return value.toPrecision(1) + "K";
  }
});
