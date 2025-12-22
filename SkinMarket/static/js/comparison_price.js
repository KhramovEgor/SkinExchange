function createSlug(name) {
    return name.toLowerCase()
        .replace(/\|/g, '-')
        .replace(/\s+/g, '-')
        .replace(/[^\w-]/g, '')
        .replace(/--+/g, '-')
        .trim('-');
}

// Функция для открытия страницы скина
function openSkinDetails(skinName) {
    const slug = createSlug(skinName);
    // Проверяем, существует ли URL для деталей скина
    if (typeof window.skinDetailBaseUrl !== 'undefined') {
        window.location.href = window.skinDetailBaseUrl.replace('{slug}', slug);
    } else {
        // Если нет базового URL, используем относительный путь
        window.location.href = `/skin/${slug}/`;
    }
}

// Расширенные данные из парсера
const itemsData = [
    {
        "id": 1,
        "name": "Кейс «Киловатт»",
        "hash_name": "Kilowatt Case",
        "category": "case",
        "price": {
            "lowest_price": 24.76,
            "median_price": 24.97,
            "volume": 134692
        },
        "profit": 15.3,
        "liquidity": 85,
        "updated": "2024-03-15",
        "image": "https://steamcommunity-a.akamaihd.net/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XsnXwtmkJjSU91dh8bj35VTqVBP4io_frnEVvqf_a6VoIfGSXz7Hlbwg57QwSS_mxhl15jiGyN37c3_GZw91W8BwRflK7EfKsa2sfw",
        "url": "https://steamcommunity.com/market/listings/730/Kilowatt Case"
    },
    {
        "id": 2,
        "name": "Капсула с наклейками кандидатов BLAST.tv Paris Major 2023",
        "hash_name": "Paris 2023 Contenders Sticker Capsule",
        "category": "sticker",
        "price": {
            "lowest_price": 9.50,
            "median_price": 9.67,
            "volume": 40531
        },
        "profit": 8.2,
        "liquidity": 72,
        "updated": "2024-03-14",
        "image": "https://steamcommunity-a.akamaihd.net/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XsnXwtmkJjSU91dh8bjn_lDkShjjoYbh_ilk__O8Ybc_cKLAMWSfz_pzvuVsXTr9kRki5m_Uwtz7cXKWO1ApCcByRLEO50LtkoWyP7_k4Afdi99GniT4jzQJsHjtsZcvVQ",
        "url": "https://steamcommunity.com/market/listings/730/Paris 2023 Contenders Sticker Capsule"
    }
];

// Переменные для состояния
let currentPage = 1;
let itemsPerPage = 10;
let filteredItems = [...itemsData];
let currentFilters = {
    search: '',
    priceMin: null,
    priceMax: null,
    profitMin: null,
    profitMax: null,
    liquidity: '',
    category: '',
    tradeType: '',
    updated: '',
    sortBy: 'profit_desc'
};

// Функция для форматирования чисел
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function formatPrice(price) {
    return `${price.toFixed(2)} руб.`;
}

// Функция для получения уровня ликвидности
function getLiquidityLevel(liquidity) {
    if (liquidity >= 80) return 'high';
    if (liquidity >= 50) return 'medium';
    return 'low';
}

// Функция для обновления счетчика активных фильтров
function updateActiveFiltersCount() {
    let count = 0;
    if (currentFilters.search) count++;
    if (currentFilters.priceMin !== null) count++;
    if (currentFilters.priceMax !== null) count++;
    if (currentFilters.profitMin !== null) count++;
    if (currentFilters.profitMax !== null) count++;
    if (currentFilters.liquidity) count++;
    if (currentFilters.category) count++;
    if (currentFilters.tradeType) count++;
    if (currentFilters.updated) count++;

    const counterElement = document.getElementById('active-filters-count');
    if (counterElement) {
        counterElement.textContent = count;
    }
}

// Функция для применения фильтров
function applyFilters() {
    filteredItems = itemsData.filter(item => {
        // Поиск по названию
        if (currentFilters.search) {
            const searchLower = currentFilters.search.toLowerCase();
            if (!item.name.toLowerCase().includes(searchLower) &&
                !item.hash_name.toLowerCase().includes(searchLower)) {
                return false;
            }
        }

        // Фильтр по цене
        if (currentFilters.priceMin !== null && item.price.lowest_price < currentFilters.priceMin) {
            return false;
        }
        if (currentFilters.priceMax !== null && item.price.lowest_price > currentFilters.priceMax) {
            return false;
        }

        // Фильтр по прибыли
        if (currentFilters.profitMin !== null && item.profit < currentFilters.profitMin) {
            return false;
        }
        if (currentFilters.profitMax !== null && item.profit > currentFilters.profitMax) {
            return false;
        }

        // Фильтр по ликвидности
        if (currentFilters.liquidity) {
            const level = getLiquidityLevel(item.liquidity);
            if (level !== currentFilters.liquidity) {
                return false;
            }
        }

        // Фильтр по категории
        if (currentFilters.category && item.category !== currentFilters.category) {
            return false;
        }

        return true;
    });

    // Сортировка
    sortItems();

    // Обновление интерфейса
    updateUI();
}

// Функция для сортировки
function sortItems() {
    filteredItems.sort((a, b) => {
        switch (currentFilters.sortBy) {
            case 'profit_desc':
                return b.profit - a.profit;
            case 'profit_asc':
                return a.profit - b.profit;
            case 'price_desc':
                return b.price.lowest_price - a.price.lowest_price;
            case 'price_asc':
                return a.price.lowest_price - b.price.lowest_price;
            case 'liquidity_desc':
                return b.liquidity - a.liquidity;
            case 'name_asc':
                return a.name.localeCompare(b.name);
            default:
                return 0;
        }
    });
}

// Функция для добавления предмета в кошелек
function addToWallet(item) {
    // Получаем текущие предметы из localStorage
    let walletItems = JSON.parse(localStorage.getItem('walletItems') || '[]');

    // Проверяем, не добавлен ли уже этот предмет
    const alreadyAdded = walletItems.some(walletItem =>
        walletItem.id === item.id || walletItem.name === item.name
    );

    if (alreadyAdded) {
        showNotification('Этот предмет уже добавлен в ваш кошелек!', 'warning');
        return;
    }

    // Создаем объект предмета для кошелька
    const walletItem = {
        id: item.id || Date.now(), // Используем текущее время если нет ID
        name: item.name,
        hash_name: item.hash_name,
        image: item.image,
        url: item.url,
        price: item.price.lowest_price,
        addedDate: new Date().toISOString(),
        currentPrice: item.price.lowest_price,
        profit: item.profit || 0,
        change: item.profit || 0,
        category: item.category || 'weapon'
    };

    // Добавляем предмет в кошелек
    walletItems.push(walletItem);

    // Сохраняем в localStorage
    localStorage.setItem('walletItems', JSON.stringify(walletItems));

    showNotification(`"${item.name}" добавлен в ваш инвестиционный кошелек!`, 'success');

    // Обновляем кнопку, чтобы показать что предмет добавлен
    updateAddToWalletButton(item.id);
}

function updateAddToWalletButton(itemId) {
    const buttons = document.querySelectorAll('.btn-wallet');

    buttons.forEach(button => {
        if (button.dataset.id == itemId) {
            button.innerHTML = '<i class="fas fa-check"></i> Добавлено';
            button.classList.add('disabled');
            button.onclick = null; // Убираем обработчик
            button.style.background = 'rgba(0, 208, 156, 0.2)';
            button.style.color = '#00d09c';
            button.style.borderColor = '#00d09c';
        }
    });
}

// Функция для отображения предметов в таблице
function renderItemsTable() {
    const tableBody = document.getElementById('items-table');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    // Рассчитываем индексы для текущей страницы
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageItems = filteredItems.slice(startIndex, endIndex);

    if (pageItems.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8">
                    <div class="empty-state">
                        <i class="fas fa-search"></i>
                        <h3>Предметы не найдены</h3>
                        <p>Попробуйте изменить параметры фильтрации или поисковый запрос</p>
                        <button class="btn-secondary" onclick="resetFilters()" style="margin-top: 20px;">
                            <i class="fas fa-redo"></i>
                            Сбросить фильтры
                        </button>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    pageItems.forEach(item => {
        const liquidityLevel = getLiquidityLevel(item.liquidity);
        const liquidityPercent = `${item.liquidity}%`;
        const isAuthenticated = window.isAuthenticated || false;

        // Экранируем кавычки в имени для использования в onclick
        const escapedName = item.name.replace(/'/g, "\\'").replace(/"/g, '&quot;');

        const row = document.createElement('tr');
        row.className = 'fade-in';

        row.innerHTML = `
            <td>
                <div class="item-col">
                    <img src="${item.image}" alt="${item.name}" class="item-image"
                         onerror="this.src='https://via.placeholder.com/64x64/2a2f3d/8a94a6?text=CS'">
                    <div class="item-info">
                        <div class="item-name">${item.name}</div>
                        <div class="item-category">${getCategoryName(item.category)}</div>
                    </div>
                </div>
            </td>
            <td class="price-col lowest-price">${formatPrice(item.price.lowest_price)}</td>
            <td class="price-col median-price">${formatPrice(item.price.median_price)}</td>
            <td class="profit-col ${item.profit >= 0 ? 'positive' : 'negative'}">
                ${item.profit >= 0 ? '+' : ''}${item.profit.toFixed(1)}%
            </td>
            <td>
                <div class="liquidity-col">
                    <span>${liquidityPercent}</span>
                    <div class="liquidity-bar">
                        <div class="liquidity-fill ${liquidityLevel}" style="width: ${item.liquidity}%"></div>
                    </div>
                </div>
            </td>
            <td class="volume-col">${formatNumber(item.price.volume)}</td>
            <td class="action-col">
                <a href="${item.url}" target="_blank" class="btn-action btn-steam">
                    <i class="fab fa-steam"></i> Steam
                </a>
                <button class="btn-action btn-details" onclick="openSkinDetails('${escapedName}')">
                    <i class="fas fa-chart-line"></i> Детали
                </button>
                <button class="btn-action btn-wallet ${isAuthenticated ? '' : 'disabled'}"
                        onclick="${isAuthenticated ? `addToWallet(${JSON.stringify(item).replace(/"/g, '&quot;')})` : 'showLoginAlert()'}"
                        data-id="${item.id}">
                    <i class="fas fa-wallet"></i> В кошелек
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    });
}

// Функция для получения названия категории
function getCategoryName(category) {
    const categories = {
        'knife': 'Ножи',
        'glove': 'Перчатки',
        'weapon': 'Оружие',
        'case': 'Кейсы',
        'sticker': 'Стикеры',
        'agent': 'Агенты'
    };
    return categories[category] || 'Другое';
}

// Функция для обновления пагинации
function updatePagination() {
    const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
    const paginationPages = document.getElementById('pagination-pages');
    if (!paginationPages) return;

    paginationPages.innerHTML = '';

    // Кнопка "Назад"
    const prevBtn = document.getElementById('prev-page');
    if (prevBtn) {
        prevBtn.disabled = currentPage === 1;
    }

    // Кнопка "Вперед"
    const nextBtn = document.getElementById('next-page');
    if (nextBtn) {
        nextBtn.disabled = currentPage === totalPages || totalPages === 0;
    }

    // Создаем кнопки страниц
    const maxPages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
    let endPage = Math.min(totalPages, startPage + maxPages - 1);

    if (endPage - startPage + 1 < maxPages) {
        startPage = Math.max(1, endPage - maxPages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.className = `pagination-page ${i === currentPage ? 'active' : ''}`;
        pageBtn.textContent = i;
        pageBtn.onclick = () => {
            currentPage = i;
            updateUI();
        };
        paginationPages.appendChild(pageBtn);
    }

    // Обновляем счетчик отфильтрованных предметов
    const filteredCount = filteredItems.length;
    const totalCount = itemsData.length;
    const countElement = document.getElementById('filtered-items-count');
    if (countElement) {
        countElement.textContent = `${filteredCount} из ${formatNumber(totalCount)} предметов`;
    }
}

// Функция для обновления всего интерфейса
function updateUI() {
    renderItemsTable();
    updatePagination();
    updateActiveFiltersCount();
}

// Функция для сброса фильтров
function resetFilters() {
    // Сброс значений фильтров
    const elements = {
        'search-input': '',
        'price-min': '',
        'price-max': '',
        'profit-min': '',
        'profit-max': '',
        'liquidity-select': '',
        'category-select': '',
        'trade-type': '',
        'updated-select': '',
        'sort-by': 'profit_desc'
    };

    for (const [id, value] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element) element.value = value;
    }

    // Сброс состояния
    currentFilters = {
        search: '',
        priceMin: null,
        priceMax: null,
        profitMin: null,
        profitMax: null,
        liquidity: '',
        category: '',
        tradeType: '',
        updated: '',
        sortBy: 'profit_desc'
    };

    // Применение фильтров
    applyFilters();
    showNotification('Фильтры сброшены', 'info');
}

// Функция для показа уведомления
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
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 500;
        font-size: 14px;
    `;

    const icon = type === 'success' ? 'check-circle' :
                type === 'warning' ? 'exclamation-triangle' :
                type === 'error' ? 'exclamation-circle' : 'info-circle';

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

// Функция для показа предупреждения о необходимости входа
function showLoginAlert() {
    showNotification('Для добавления предметов в инвестиционный кошелек необходимо войти через Steam!', 'warning');
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Настройка переключения фильтров
    const filtersToggle = document.getElementById('filters-toggle');
    const filtersGrid = document.getElementById('filters-grid');

    if (filtersToggle && filtersGrid) {
        filtersToggle.addEventListener('click', () => {
            const isVisible = filtersGrid.style.display === 'grid';
            filtersGrid.style.display = isVisible ? 'none' : 'grid';
            filtersToggle.innerHTML = isVisible ?
                '<i class="fas fa-sliders-h"></i> Фильтры' :
                '<i class="fas fa-times"></i> Скрыть фильтры';
            filtersToggle.innerHTML += `<span id="active-filters-count" style="background: #4f7bff; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">${document.getElementById('active-filters-count').textContent}</span>`;
        });
    }

    // Кнопка поиска
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                currentFilters.search = searchInput.value;
                currentPage = 1;
                applyFilters();
                showNotification('Поиск выполнен', 'info');
            }
        });
    }

    // Поиск по Enter
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                currentFilters.search = searchInput.value;
                currentPage = 1;
                applyFilters();
                showNotification('Поиск выполнен', 'info');
            }
        });
    }

    // Применение фильтров
    const applyBtn = document.getElementById('apply-filters');
    if (applyBtn) {
        applyBtn.addEventListener('click', () => {
            // Собираем значения фильтров
            const priceMin = document.getElementById('price-min');
            const priceMax = document.getElementById('price-max');
            const profitMin = document.getElementById('profit-min');
            const profitMax = document.getElementById('profit-max');
            const liquiditySelect = document.getElementById('liquidity-select');
            const categorySelect = document.getElementById('category-select');
            const tradeType = document.getElementById('trade-type');
            const updatedSelect = document.getElementById('updated-select');
            const sortBy = document.getElementById('sort-by');

            currentFilters.priceMin = priceMin && priceMin.value ? parseFloat(priceMin.value) : null;
            currentFilters.priceMax = priceMax && priceMax.value ? parseFloat(priceMax.value) : null;
            currentFilters.profitMin = profitMin && profitMin.value ? parseFloat(profitMin.value) : null;
            currentFilters.profitMax = profitMax && profitMax.value ? parseFloat(profitMax.value) : null;
            currentFilters.liquidity = liquiditySelect ? liquiditySelect.value : '';
            currentFilters.category = categorySelect ? categorySelect.value : '';
            currentFilters.tradeType = tradeType ? tradeType.value : '';
            currentFilters.updated = updatedSelect ? updatedSelect.value : '';
            currentFilters.sortBy = sortBy ? sortBy.value : 'profit_desc';

            currentPage = 1;
            applyFilters();
            showNotification('Фильтры применены', 'success');
        });
    }

    // Сброс фильтров
    const resetBtn = document.getElementById('reset-filters');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetFilters);
    }

    // Изменение количества элементов на странице
    const pageSize = document.getElementById('page-size');
    if (pageSize) {
        pageSize.addEventListener('change', (e) => {
            itemsPerPage = parseInt(e.target.value);
            currentPage = 1;
            updateUI();
        });
    }

    // Кнопки пагинации
    const prevPage = document.getElementById('prev-page');
    if (prevPage) {
        prevPage.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                updateUI();
            }
        });
    }

    const nextPage = document.getElementById('next-page');
    if (nextPage) {
        nextPage.addEventListener('click', () => {
            const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                updateUI();
            }
        });
    }

    // Инициализация
    applyFilters();
});