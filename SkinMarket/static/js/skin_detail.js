// skin_detail.js

// Инициализация графика цен
function initPriceChart() {
    const canvas = document.getElementById('priceChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Данные за 7 дней (по умолчанию)
    const labels = ['27-09', '28-09', '29-09', '30-09', '01-10', '02-10', '03-10'];
    const data = [79.09, 92.44, 76.79, 76.60, 79.31, 86.03, 85.72];

    window.priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Цена ($)',
                data: data,
                borderColor: '#4f7bff',
                backgroundColor: 'rgba(79, 123, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#4f7bff',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 1,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(26, 31, 46, 0.9)',
                    titleColor: '#f0f0f0',
                    bodyColor: '#b0b7c3',
                    borderColor: '#4f7bff',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return `$${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: 'rgba(42, 47, 61, 0.5)' },
                    ticks: {
                        color: '#8a94a6',
                        font: { size: 11 },
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                },
                x: {
                    grid: { color: 'rgba(42, 47, 61, 0.5)' },
                    ticks: {
                        color: '#8a94a6',
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

// Обновление графика по периодам
function updateChart(period) {
    if (!window.priceChart) return;

    const chart = window.priceChart;
    let labels = [];
    let data = [];

    switch(period) {
        case '7d':
            labels = ['27-09', '28-09', '29-09', '30-09', '01-10', '02-10', '03-10'];
            data = [79.09, 92.44, 76.79, 76.60, 79.31, 86.03, 85.72];
            break;

        case '30d':
            for (let i = 29; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                if (i % 4 === 0) {
                    labels.push(date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }));
                    data.push(Math.random() * 50 + 60);
                }
            }
            break;

        case '90d':
            for (let i = 89; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                if (i % 12 === 0) {
                    labels.push(date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }));
                    data.push(Math.random() * 70 + 30);
                }
            }
            break;

        case 'all':
            labels = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен'];
            data = [29.47, 32.15, 38.02, 42.50, 48.52, 52.30, 60.63, 65.80, 118.51];
            break;
    }

    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.update();

    showNotification(`График обновлен: ${getPeriodName(period)}`);
}

// Обновление информации при смене износа
function updateWearInfo(wear) {
    const wearData = {
        'factory-new': {
            price: '$118.51',
            change: '+2.3%',
            changeClass: 'positive'
        },
        'minimal-wear': {
            price: '$30.44',
            change: '-1.2%',
            changeClass: 'negative'
        },
        'field-tested': {
            price: '$11.85',
            change: '+0.8%',
            changeClass: 'positive'
        },
        'well-worn': {
            price: '$7.32',
            change: '+3.1%',
            changeClass: 'positive'
        },
        'battle-scarred': {
            price: '$5.81',
            change: '-0.5%',
            changeClass: 'negative'
        }
    };

    const data = wearData[wear];
    if (data) {
        const priceElement = document.querySelector('.current-price');
        if (priceElement) {
            priceElement.textContent = data.price;
        }
        showNotification(`Выбран износ: ${getWearName(wear)}`);
    }
}

// Обновление цен при включении StatTrak
function updatePrices(isStatTrak) {
    const wearVariants = document.querySelectorAll('.wear-variant');
    const statTrakMultiplier = 1.8; // Множитель для StatTrak цен

    wearVariants.forEach(variant => {
        const priceElement = variant.querySelector('.wear-price');
        if (!priceElement) return;

        const currentPrice = parseFloat(priceElement.textContent.replace('$', ''));
        if (isNaN(currentPrice)) return;

        let newPrice;
        if (isStatTrak) {
            newPrice = currentPrice * statTrakMultiplier;
        } else {
            newPrice = currentPrice / statTrakMultiplier;
        }

        priceElement.textContent = `$${newPrice.toFixed(2)}`;
    });
}

// Вспомогательные функции
function getWearName(wear) {
    const names = {
        'factory-new': 'Примо с завода',
        'minimal-wear': 'Минимальный износ',
        'field-tested': 'Полевые испытания',
        'well-worn': 'Сильно изношено',
        'battle-scarred': 'С боевыми следами'
    };
    return names[wear] || wear;
}

function getPeriodName(period) {
    const names = {
        '7d': '7 дней',
        '30d': '30 дней',
        '90d': '90 дней',
        'all': 'Вся история'
    };
    return names[period] || period;
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 15px;
        right: 15px;
        background: #4f7bff;
        color: white;
        padding: 10px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        font-weight: 500;
        font-size: 13px;
    `;

    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => notification.remove(), 300);
    }, 2000);

    // Добавляем стили для анимации
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

// Основная функция инициализации
function initializeSkinDetailPage() {
    // Переключение StatTrak
    const statTrakToggle = document.getElementById('stattrakToggle');
    if (statTrakToggle) {
        const toggleSwitch = statTrakToggle.querySelector('.toggle-switch');
        if (toggleSwitch) {
            statTrakToggle.addEventListener('click', function() {
                toggleSwitch.classList.toggle('active');
                const isActive = toggleSwitch.classList.contains('active');
                showNotification(`Режим StatTrak ${isActive ? 'включен' : 'выключен'}`);
                updatePrices(isActive);
            });
        }
    }

    // Переключение вариантов износа
    const wearVariants = document.querySelectorAll('.wear-variant');
    wearVariants.forEach(variant => {
        variant.addEventListener('click', function() {
            wearVariants.forEach(v => v.classList.remove('active'));
            this.classList.add('active');

            const wear = this.dataset.wear;
            updateWearInfo(wear);
        });
    });

    // Показать/скрыть больше текста
    const showMoreBtn = document.getElementById('showMore');
    const moreText = document.getElementById('moreText');
    
    if (showMoreBtn && moreText) {
        showMoreBtn.addEventListener('click', function() {
            if (moreText.style.display === 'none') {
                moreText.style.display = 'inline';
                this.textContent = 'Показать меньше';
            } else {
                moreText.style.display = 'none';
                this.textContent = 'Показать больше';
            }
        });
    }

    // Переключение периодов графика
    const periodBtns = document.querySelectorAll('.period-btn');
    periodBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            periodBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const period = this.dataset.period;
            updateChart(period);
        });
    });

    // Фильтры истории цен
    const historyFilters = document.querySelectorAll('.history-filter');
    historyFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            historyFilters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Фильтры износа
    const wearFilters = document.querySelectorAll('.wear-filter');
    wearFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            wearFilters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Инициализация графика (если Chart.js доступен)
    if (typeof Chart !== 'undefined') {
        initPriceChart();
    }
}

// Запуск при загрузке страницы
document.addEventListener('DOMContentLoaded', initializeSkinDetailPage);