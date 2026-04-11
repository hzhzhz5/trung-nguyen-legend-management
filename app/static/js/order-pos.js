document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("product-search");
    const categorySelect = document.getElementById("product-category-select");
    const chips = document.querySelectorAll(".category-chip");
    const cards = document.querySelectorAll(".product-card");

    function normalize(text) {
        return (text || "").toLowerCase().trim();
    }

    function filterProducts() {
        const keyword = normalize(searchInput ? searchInput.value : "");
        const selectedCategory = normalize(categorySelect ? categorySelect.value : "");

        cards.forEach((card) => {
            const name = normalize(card.dataset.name);
            const code = normalize(card.dataset.code);
            const category = normalize(card.dataset.category);

            const matchKeyword = !keyword || name.includes(keyword) || code.includes(keyword);
            const matchCategory = !selectedCategory || category === selectedCategory;

            card.style.display = matchKeyword && matchCategory ? "" : "none";
        });
    }

    if (searchInput) {
        searchInput.addEventListener("input", filterProducts);
    }

    if (categorySelect) {
        categorySelect.addEventListener("change", function () {
            const selected = categorySelect.value;

            chips.forEach((chip) => {
                chip.classList.toggle("active", chip.dataset.category === selected);
            });

            filterProducts();
        });
    }

    chips.forEach((chip) => {
        chip.addEventListener("click", function () {
            const category = chip.dataset.category || "";
            if (categorySelect) {
                categorySelect.value = category;
            }

            chips.forEach((item) => item.classList.remove("active"));
            chip.classList.add("active");

            filterProducts();
        });
    });

    document.querySelectorAll(".product-add-btn").forEach((button) => {
        button.addEventListener("click", function () {
            const productId = button.dataset.productId;
            const productName = button.dataset.productName;
            const stock = parseInt(button.dataset.stock || "0", 10);

            if (stock <= 0) {
                alert("Sản phẩm đã hết hàng.");
                return;
            }

            const quantityText = prompt(`Nhập số lượng cho "${productName}"`, "1");
            if (quantityText === null) return;

            const quantity = parseInt(quantityText, 10);
            if (!quantity || quantity < 1) {
                alert("Số lượng không hợp lệ.");
                return;
            }

            const form = document.getElementById("quick-add-form");
            form.querySelector('select[name="product_id"]').value = productId;
            form.querySelector('input[name="quantity"]').value = quantity;
            form.submit();
        });
    });

    filterProducts();
});