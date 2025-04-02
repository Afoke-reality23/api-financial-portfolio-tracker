const urlParams = new URLSearchParams(window.location.search);
const assetId = urlParams.get("id");
function fetchAssetDetail(assetId) {
  console.log("i am here");
  if (assetId) {
    fetch(`http://localhost:1998/asset_details?id=${assetId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        console.log("i am here bitches");
        if (response.ok) {
          return response.json();
        } else {
          throw new Error({
            errorCode: response.status,
            mesage: "failed to fetch resources",
          });
        }
      })
      .then((data) => {
        console.log(data);
      })
      .catch((error) => {
        console.error(error);
      });
  }
}

fetchAssetDetail(assetId);
