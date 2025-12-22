// home.js

// Функция для создания slug из имени
function createSlug(name) {
    return name.toLowerCase()
        .replace(/\|/g, '-')
        .replace(/\s+/g, '-')
        .replace(/[^\w-]/g, '')
        .replace(/--+/g, '-')
        .trim('-');
}

// Функция обновления статистики
function updateLiveStats() {
    const stats = document.querySelectorAll('.stat-value');
    stats.forEach(stat => {
        const currentValue = parseFloat(stat.textContent.replace(/[^0-9.]/g, ''));
        const change = (Math.random() * 0.5 - 0.25);
        const newValue = currentValue * (1 + change);

        if (stat.textContent.includes('$')) {
            stat.textContent = '$' + (newValue / 1000000).toFixed(1) + 'M';
        } else if (stat.textContent.includes('★')) {
            const newRating = Math.min(5, Math.max(4, parseFloat(stat.textContent) + (Math.random() * 0.1 - 0.05)));
            stat.textContent = newRating.toFixed(1) + '★';
        } else {
            const suffix = stat.textContent.replace(/[0-9.]/g, '');
            stat.textContent = Math.round(newValue) + suffix;
        }
    });
}

// Функция обновления статистики рынков
function refreshMarketStats() {
    const btn = event.target.closest('button');
    const originalText = btn.innerHTML;

    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обновление...';
    btn.disabled = true;

    // Симуляция загрузки данных
    setTimeout(() => {
        // Обновляем случайные данные в таблице
        document.querySelectorAll('.data-table tbody tr').forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 4) {
                // Объем
                const volume = parseFloat(cells[1].textContent.replace(/[^0-9.]/g, ''));
                const volumeChange = (Math.random() * 0.3 - 0.15);
                cells[1].textContent = '$' + Math.round(volume * (1 + volumeChange)).toLocaleString();

                // Предметы
                const items = parseFloat(cells[2].textContent.replace(/[^0-9.]/g, ''));
                const itemsChange = (Math.random() * 0.2 - 0.1);
                cells[2].textContent = Math.round(items * (1 + itemsChange)).toLocaleString();

                // Изменение
                const changeElement = cells[3].querySelector('span');
                const newChange = (Math.random() * 30 - 15).toFixed(2);
                if (newChange >= 0) {
                    changeElement.textContent = '▲ +' + newChange + '%';
                    changeElement.className = 'positive';
                } else {
                    changeElement.textContent = '▼ ' + newChange + '%';
                    changeElement.className = 'negative';
                }

                // Средняя цена
                const price = parseFloat(cells[4].textContent.replace(/[^0-9.]/g, ''));
                const priceChange = (Math.random() * 0.2 - 0.1);
                cells[4].textContent = '$' + (price * (1 + priceChange)).toFixed(2);
            }
        });

        btn.innerHTML = originalText;
        btn.disabled = false;

        // Показать уведомление
        showNotification('Статистика рынков обновлена', 'success');
    }, 1500);
}

// Калькулятор прибыли
function calculateProfit() {
    const buyPrice = parseFloat(document.getElementById('buy-price').value) || 0;
    const sellPrice = parseFloat(document.getElementById('sell-price').value) || 0;
    const commission = parseFloat(document.getElementById('commission').value) || 0;
    const quantity = parseInt(document.getElementById('quantity').value) || 1;

    if (buyPrice <= 0 || sellPrice <= 0) {
        return;
    }

    // Расчеты
    const totalBuy = buyPrice * quantity;
    const totalSell = sellPrice * quantity;
    const commissionAmount = (totalSell * commission) / 100;
    const afterCommission = totalSell - commissionAmount;
    const profit = afterCommission - totalBuy;
    const profitPercentage = (profit / totalBuy) * 100;

    // Обновление значений
    const profitAmount = document.getElementById('profit-amount');
    const profitPercentageElem = document.getElementById('profit-percentage');
    const afterCommissionElem = document.getElementById('after-commission');
    const commissionAmountElem = document.getElementById('commission-amount');

    if (profitAmount) profitAmount.textContent = `$${Math.max(profit, 0).toFixed(2)}`;
    if (profitPercentageElem) profitPercentageElem.textContent = `${profitPercentage.toFixed(1)}%`;
    if (afterCommissionElem) afterCommissionElem.textContent = `$${afterCommission.toFixed(2)}`;
    if (commissionAmountElem) commissionAmountElem.textContent = `$${commissionAmount.toFixed(2)}`;

    // Цветовое оформление
    if (profitAmount) {
        profitAmount.className = `result-value ${profit >= 0 ? 'positive' : 'negative'}`;
    }
    if (profitPercentageElem) {
        profitPercentageElem.className = `result-value ${profitPercentage >= 0 ? 'positive' : 'negative'}`;
    }
}

function resetCalculator() {
    const buyPriceInput = document.getElementById('buy-price');
    const sellPriceInput = document.getElementById('sell-price');
    const commissionInput = document.getElementById('commission');
    const quantityInput = document.getElementById('quantity');

    if (buyPriceInput) buyPriceInput.value = '50.00';
    if (sellPriceInput) sellPriceInput.value = '65.00';
    if (commissionInput) commissionInput.value = '13';
    if (quantityInput) quantityInput.value = '1';

    calculateProfit();
    showNotification('Калькулятор сброшен', 'info');
}

// Функция показа уведомлений
function showNotification(message, type = 'info') {
    const colors = {
        'success': '#00d09c',
        'error': '#ff4757',
        'info': '#4f7bff',
        'warning': '#ff9500'
    };

    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 15px;
        right: 15px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        font-size: 14px;
    `;

    const icon = type === 'success' ? 'check-circle' :
                type === 'error' ? 'exclamation-circle' :
                type === 'warning' ? 'exclamation-triangle' : 'info-circle';

    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        ${message}
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);

    // Добавляем стили для анимации
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Функция для обновления всех кнопок "Детали" после загрузки данных
function updateDetailsButtons() {
    // Эта функция требует window.itemsData
    if (typeof window.itemsData === 'undefined') return;

    document.querySelectorAll('.item-card').forEach((card, index) => {
        const itemName = window.itemsData[index]?.name;
        if (itemName) {
            const detailsButton = card.querySelector('.btn-details');
            if (detailsButton) {
                detailsButton.setAttribute('data-item-name', itemName);
            } else {
                // Создаем кнопку, если её нет
                const btn = document.createElement('button');
                btn.className = 'btn-small btn-details';
                btn.style.cssText = 'width: 100%; text-align: center; background: rgba(0, 208, 156, 0.1); color: #00d09c; border-color: #00d09c; margin-top: 8px;';
                btn.innerHTML = '<i class="fas fa-chart-line"></i> Детали';
                btn.setAttribute('data-item-name', itemName);
                btn.addEventListener('click', function() {
                    const slug = createSlug(itemName);
                    if (typeof window.skinDetailBaseUrl !== 'undefined') {
                        window.location.href = window.skinDetailBaseUrl.replace('{slug}', slug);
                    } else {
                        window.location.href = `/skin/${slug}/`;
                    }
                });

                const actionsDiv = card.querySelector('.item-actions');
                if (actionsDiv) {
                    actionsDiv.appendChild(btn);
                } else {
                    card.appendChild(btn);
                }
            }
        }
    });
}

// Показать категорию
function showCategory(category) {
    const categories = {
        'knives': 'Ножи - Премиум предметы с высокой ликвидностью',
        'gloves': 'Перчатки - Популярны среди коллекционеров',
        'rifles': 'Винтовки - Наиболее часто используемое оружие',
        'cases': 'Кейсы - Высокорисковые инвестиции',
        'stickers': 'Стикеры - Быстрый рост в последнее время',
        'agents': 'Агенты - Стабильные, но медленный рост'
    };

    alert(categories[category] + '\n\nДетальная статистика будет доступна в следующем обновлении!');
}

// Основная функция инициализации
function initializeHomePage() {
    // Инициализация графиков (если Chart.js доступен)
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }

    // Обработчики для тегов
    document.querySelectorAll('.tag').forEach(tag => {
        tag.addEventListener('click', function() {
            const category = this.textContent.split(' ')[0];
            alert('Фильтр по категории: ' + category + '\n\nЭта функция будет доступна в следующем обновлении!');
        });
    });

    // Анимация карточек
    const cards = document.querySelectorAll('.card, .item-card, .stat-card, .category-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.2)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
        });
    });

    // Обработчики для кнопок "Детали" на главной странице
    document.querySelectorAll('.btn-details').forEach(button => {
        button.addEventListener('click', function() {
            const itemName = this.getAttribute('data-item-name');
            if (itemName) {
                const slug = createSlug(itemName);
                if (typeof window.skinDetailBaseUrl !== 'undefined') {
                    window.location.href = window.skinDetailBaseUrl.replace('{slug}', slug);
                } else {
                    window.location.href = `/skin/${slug}/`;
                }
            }
        });
    });

    // Инициализация калькулятора
    const inputs = ['buy-price', 'sell-price', 'commission', 'quantity'];
    inputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', calculateProfit);
            element.addEventListener('change', calculateProfit);
        }
    });

    // Начальный расчет
    calculateProfit();

    // Обновление статистики каждые 30 секунд
    setInterval(updateLiveStats, 30000);

    // Обработчик изменения периода графика
    const chartPeriodSelect = document.getElementById('chart-period');
    if (chartPeriodSelect) {
        chartPeriodSelect.addEventListener('change', function() {
            if (window.marketChart) {
                updateChartPeriod(this.value);
            }
        });
    }
}

// Функция инициализации графиков
function initializeCharts() {
    const canvas = document.getElementById('marketTrendChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Данные для графика
    const labels = [];
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }));
    }

    window.marketChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Средняя цена предметов',
                data: Array.from({length: 30}, () => Math.random() * 50 + 20),
                borderColor: '#4f7bff',
                backgroundColor: 'rgba(79, 123, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }, {
                label: 'Объем торгов',
                data: Array.from({length: 30}, () => Math.random() * 1000000 + 500000),
                borderColor: '#00d09c',
                backgroundColor: 'rgba(0, 208, 156, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Цена ($)',
                        color: '#8a94a6',
                        font: { size: 12 }
                    },
                    grid: { color: 'rgba(42, 47, 61, 0.5)' },
                    ticks: {
                        color: '#8a94a6',
                        font: { size: 11 }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Объем ($)',
                        color: '#8a94a6',
                        font: { size: 12 }
                    },
                    grid: { drawOnChartArea: false },
                    ticks: {
                        color: '#8a94a6',
                        font: { size: 11 },
                        callback: function(value) {
                            if (value >= 1000000) {
                                return '$' + (value / 1000000).toFixed(1) + 'M';
                            } else if (value >= 1000) {
                                return '$' + (value / 1000).toFixed(1) + 'K';
                            }
                            return '$' + value;
                        }
                    }
                },
                x: {
                    grid: { color: 'rgba(42, 47, 61, 0.5)' },
                    ticks: {
                        color: '#8a94a6',
                        font: { size: 11 },
                        maxRotation: 0
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#b0b7c3',
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(26, 31, 46, 0.9)',
                    titleColor: '#f0f0f0',
                    bodyColor: '#b0b7c3',
                    borderColor: '#4f7bff',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label.includes('Объем')) {
                                if (context.parsed.y >= 1000000) {
                                    return label + ': $' + (context.parsed.y / 1000000).toFixed(2) + 'M';
                                } else if (context.parsed.y >= 1000) {
                                    return label + ': $' + (context.parsed.y / 1000).toFixed(2) + 'K';
                                }
                                return label + ': $' + context.parsed.y;
                            }
                            return label + ': $' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

// Функция обновления периода графика
function updateChartPeriod(period) {
    if (!window.marketChart) return;

    let newLabels = [];
    let newData1 = [];
    let newData2 = [];

    if (period === '7d') {
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            newLabels.push(date.toLocaleDateString('ru-RU', { weekday: 'short' }));
            newData1.push(Math.random() * 50 + 20);
            newData2.push(Math.random() * 1000000 + 500000);
        }
    } else if (period === '30d') {
        for (let i = 29; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            newLabels.push(date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }));
            newData1.push(Math.random() * 50 + 20);
            newData2.push(Math.random() * 1000000 + 500000);
        }
    } else if (period === '90d') {
        for (let i = 89; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            if (i % 3 === 0) {
                newLabels.push(date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }));
                newData1.push(Math.random() * 50 + 20);
                newData2.push(Math.random() * 1000000 + 500000);
            }
        }
    }

    window.marketChart.data.labels = newLabels;
    window.marketChart.data.datasets[0].data = newData1;
    window.marketChart.data.datasets[1].data = newData2;
    window.marketChart.update();
}

// Запуск при загрузке страницы
document.addEventListener('DOMContentLoaded', initializeHomePage);