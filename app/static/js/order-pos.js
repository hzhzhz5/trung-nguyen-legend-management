document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("product-search");
    const categorySelect = document.getElementById("product-category-select");
    const chips = document.querySelectorAll(".category-chip");
    const cards = document.querySelectorAll(".product-card");

    const quantityModal = document.getElementById("quantity-modal");
    const modalBackdrop = document.querySelector(".quantity-modal-backdrop");
    const closeModalBtn = document.getElementById("close-quantity-modal");
    const cancelModalBtn = document.getElementById("cancel-quantity-btn");
    const confirmModalBtn = document.getElementById("confirm-quantity-btn");
    const modalQuantityInput = document.getElementById("modal-quantity-input");
    const modalProductName = document.getElementById("quantity-product-name");
    const quickAddForm = document.getElementById("quick-add-form");

    let selectedProductId = null;
    let selectedProductName = "";

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

    function openQuantityModal(productId, productName) {
        selectedProductId = productId;
        selectedProductName = productName;

        modalProductName.textContent = `Sản phẩm: ${productName}`;
        modalQuantityInput.value = 1;
        quantityModal.classList.remove("hidden");

        setTimeout(() => {
            modalQuantityInput.focus();
            modalQuantityInput.select();
        }, 50);
    }

    function closeQuantityModal() {
        quantityModal.classList.add("hidden");
        selectedProductId = null;
        selectedProductName = "";
    }

    function submitQuickAdd() {
        const quantity = parseInt(modalQuantityInput.value, 10);

        if (!quantity || quantity < 1) {
            alert("Số lượng không hợp lệ.");
            modalQuantityInput.focus();
            return;
        }

        quickAddForm.querySelector('select[name="product_id"]').value = selectedProductId;
        quickAddForm.querySelector('input[name="quantity"]').value = quantity;
        quickAddForm.submit();
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
            openQuantityModal(productId, productName);
        });
    });

    if (closeModalBtn) {
        closeModalBtn.addEventListener("click", closeQuantityModal);
    }

    if (cancelModalBtn) {
        cancelModalBtn.addEventListener("click", closeQuantityModal);
    }

    if (modalBackdrop) {
        modalBackdrop.addEventListener("click", closeQuantityModal);
    }

    if (confirmModalBtn) {
        confirmModalBtn.addEventListener("click", submitQuickAdd);
    }

    if (modalQuantityInput) {
        modalQuantityInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                submitQuickAdd();
            }
        });
    }

    filterProducts();
});