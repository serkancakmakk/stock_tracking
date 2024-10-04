document.addEventListener('DOMContentLoaded', function() {
    // HTML içinde tanımlanan verileri kullan
    var minStockProductNames = window.minStockProductNames;
    var minStockProductStocks = window.minStockProductStocks;
    
    var ctx = document.getElementById('minStockChart').getContext('2d');
    var minStockChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: minStockProductNames,
            datasets: [{
                label: 'Stok Miktarı',
                data: minStockProductStocks,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
