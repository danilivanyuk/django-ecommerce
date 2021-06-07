let updateBtns = document.querySelectorAll(".update-cart");
let size = document.querySelectorAll(".sizes");
updateBtns.forEach((btn) => {
  btn.addEventListener("click", function () {
    let productId = this.dataset.product;
    let action = this.dataset.action;
    let product_size = get_selected_product_size(productId);
    let cart_product_size = this.dataset.size;
    if (!cart_product_size) {
      cart_product_size = "";
    }
    console.log(cart_product_size);
    if (user === "AnonymousUser") {
      addCookieItem(productId, product_size, action);
    } else {
      updateUserOrder(productId, product_size, action, cart_product_size);
    }
  });
});

function get_selected_product_size(productId) {
  let product_container = document.querySelector(
    `[data-product='${productId}']`
  ).parentElement.parentElement;

  let product_size_container = product_container.querySelector(".sizes");

  if (product_container.contains(product_size_container)) {
    let product_size = "";
    if (product_size_container.value == undefined) {
      product_size =
        product_size_container.innerText ||
        product_size_container.options[product_size_container.selectedIndex]
          .innerText;
      product_size = product_size.replace(/(\r\n|\n|\r\s)/gm, "");
      return product_size;
    } else {
      product_size =
        product_size_container.value ||
        product_size_container.options[product_size_container.selectedIndex]
          .value;
      product_size = product_size.replace(/(\r\n|\n|\r)/gm, "");
      return product_size;
    }
  } else {
    return "";
  }
}

function addCookieItem(productId, product_size, action) {
  console.log(productId, product_size, action);
  if (action == "add") {
    if (cart[productId] == undefined) {
      cart[productId] = { quantity: 1, size: product_size };
    } else {
      cart[productId]["quantity"] += 1;
    }
  }
  if (action == "remove") {
    cart[productId]["quantity"] -= 1;
    if (cart[productId]["quantity"] <= 0) {
      delete cart[productId];
    }
  }
  location.reload();
  document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
}

function updateUserOrder(productId, product_size, action, cart_product_size) {
  let url = "/update_item/";
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({
      productId: productId,
      size: product_size,
      action: action,
      cart_product_size: cart_product_size,
    }),
  })
    .then((response) => {
      console.log(response);
      return response.json();
    })
    .then((data) => {
      location.reload();
      console.log("data:", data);
    });
}
