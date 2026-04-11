function clearSelectedTable() {
    document.querySelectorAll(".table-card").forEach((card) => {
        card.classList.remove("selected");
    });
}

function toggleOrderFields() {
    const orderType = document.getElementById("order_type").value;

    const tableBlock = document.getElementById("table_block");
    const customerNameBlock = document.getElementById("customer_name_block");
    const customerPhoneBlock = document.getElementById("customer_phone_block");
    const deliveryAddressBlock = document.getElementById("delivery_address_block");
    const tableIdInput = document.getElementById("table_id");

    if (orderType === "dine_in") {
        tableBlock.style.display = "block";
        customerNameBlock.style.display = "none";
        customerPhoneBlock.style.display = "none";
        deliveryAddressBlock.style.display = "none";
    } else if (orderType === "takeaway") {
        tableBlock.style.display = "none";
        customerNameBlock.style.display = "block";
        customerPhoneBlock.style.display = "block";
        deliveryAddressBlock.style.display = "none";
        tableIdInput.value = 0;
        clearSelectedTable();
    } else if (orderType === "delivery") {
        tableBlock.style.display = "none";
        customerNameBlock.style.display = "block";
        customerPhoneBlock.style.display = "block";
        deliveryAddressBlock.style.display = "block";
        tableIdInput.value = 0;
        clearSelectedTable();
    }
}

function bindTableSelection() {
    const tableIdInput = document.getElementById("table_id");
    const cards = document.querySelectorAll(".table-card");

    cards.forEach((card) => {
        card.addEventListener("click", function () {
            if (card.dataset.disabled === "true") {
                return;
            }

            clearSelectedTable();
            card.classList.add("selected");
            tableIdInput.value = card.dataset.tableId;
        });
    });
}

function restoreSelectedTable() {
    const currentValue = String(window.ORDER_CREATE_INITIAL_TABLE_ID || "0");
    if (!currentValue || currentValue === "0") {
        return;
    }

    const selectedCard = document.querySelector(`.table-card[data-table-id="${currentValue}"]`);
    if (selectedCard) {
        selectedCard.classList.add("selected");
        document.getElementById("table_id").value = currentValue;
    }
}

document.addEventListener("DOMContentLoaded", function () {
    toggleOrderFields();
    bindTableSelection();
    restoreSelectedTable();

    document.getElementById("order_type").addEventListener("change", toggleOrderFields);
});