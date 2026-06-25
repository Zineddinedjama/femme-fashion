document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        document.querySelectorAll('.flash').forEach(function(el) {
            el.style.transition = 'opacity 0.5s';
            el.style.opacity = '0';
            setTimeout(function() { el.remove(); }, 500);
        });
    }, 4000);

    // Product page quantity +/- and total display
    var qtyDisplay = document.getElementById('qty-display');
    var qtyInput = document.getElementById('quantity');
    var totalDisplay = document.getElementById('produit-total');
    if (qtyDisplay && qtyInput && totalDisplay) {
        var priceEl = document.querySelector('.price-lg');
        var price = 0;
        if (priceEl) {
            price = parseFloat(priceEl.textContent.trim().replace(' DA', ''));
        }

        function updateQtyAndTotal(newQty) {
            if (newQty < 1) newQty = 1;
            qtyDisplay.textContent = newQty;
            qtyInput.value = newQty;
            totalDisplay.textContent = (price * newQty).toFixed(2) + ' DA';
        }

        document.getElementById('qty-plus').addEventListener('click', function() {
            updateQtyAndTotal(parseInt(qtyDisplay.textContent) + 1);
        });
        document.getElementById('qty-minus').addEventListener('click', function() {
            updateQtyAndTotal(parseInt(qtyDisplay.textContent) - 1);
        });
    }
});
