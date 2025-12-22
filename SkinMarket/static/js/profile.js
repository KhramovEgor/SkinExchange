// profile.js

// Вспомогательные функции
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function createSlug(name) {
    return name.toLowerCase()
        .replace(/\|/g, '-')
        .replace(/\s+/g, '-')
        .replace(/[^\w-]/g, '')
        .replace(/--+/g, '-')
        .trim('-');
}

function openSkinDetails(skinName) {
    const slug = createSlug(skinName);
    if (typeof window.skinDetailBaseUrl !== 'undefined') {
        window.location.href = window.skinDetailBaseUrl.replace('{slug}', slug);
    } else {
        window.location.href = `/skin/${slug}/`;
    }
}

function openSkinDetailsFromInventory(skinName) {
    openSkinDetails(skinName);
}

function getImageUrl(item) {
    if (item.icon_url_large) {
        return `https://steamcommunity-a.akamaihd.net/economy/image/${item.icon_url_large}`;
    } else if (item.icon_url) {
        return `https://steamcommunity-a.akamaihd.net/economy/image/${item.icon_url}`;
    }
    return 'https://via.placeholder.com/200x120/2a2f3d/8a94a6?text=CS:GO';
}

function showEmptyInventory() {
    const container = document.getElementById('inventory-container');
    if (!container) return;

    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">🎮</div>
            <h3>Инвентарь CS:GO пуст</h3>
            <p>В вашем Steam инвентаре нет предметов CS:GO/CS2</p>
        </div>
    `;
}

// Основные функции
function renderWalletItems() {
    const container = document.getElementById('wallet-items-container');
    if (!container) return;

    if (!window.walletItems || window.walletItems.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">💰</div>
                <h3>Кошелек пуст</h3>
                <p>Добавьте предметы из раздела "Сравнение цен"</p>
            </div>
        `;
        return;
    }

    container.innerHTML = window.walletItems.map((item, index) => {
        const escapedName = (item.name || 'Без названия').replace(/'/g, "\\'").replace(/"/g, '&quot;');

        return `
            <div class="item-card">
                <div class="item-image-wrapper">
                    <img src="${item.image || 'https://via.placeholder.com/200x120/2a2f3d/8a94a6?text=CS:GO'}"
                         alt="${item.name}"
                         class="item-image"
                         onerror="this.src='https://via.placeholder.com/200x120/2a2f3d/8a94a6?text=CS:GO'">
                </div>
                <div class="item-details">
                    <div class="item-name" title="${item.name}">
                        ${item.name || 'Без названия'}
                    </div>
                    <div class="item-meta">
                        <div class="item-type">${item.category || 'Инвестиция'}</div>
                        <div class="item-change ${item.change >= 0 ? 'value-positive' : 'value-negative'}">
                            ${item.change >= 0 ? '▲' : '▼'} ${Math.abs(item.change)}%
                        </div>
                    </div>
                </div>
                <div class="item-actions">
                    <button class="action-btn btn-view" onclick="viewItemOnMarket(${index})" title="Посмотреть на маркете">
                        <i class="fas fa-chart-line"></i>
                    </button>
                    <button class="action-btn btn-add" onclick="analyzeItem(${index})" title="Проанализировать">
                        <i class="fas fa-chart-bar"></i>
                    </button>
                    <button class="action-btn" onclick="openSkinDetails('${escapedName}')"
                            title="Детальная аналитика" style="background: rgba(108, 92, 231, 0.1); color: #6c5ce7; border-color: #6c5ce7;">
                        <i class="fas fa-search-plus"></i>
                    </button>
                    <button class="action-btn" onclick="removeFromWallet(${index})" title="Удалить" style="background: rgba(255, 71, 87, 0.1); color: #ff4757; border-color: #ff4757;">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    updateWalletStats();
}

function renderInventory(items) {
    const container = document.getElementById('inventory-container');
    if (!container) return;

    if (!items || items.length === 0) {
        showEmptyInventory();
        return;
    }

    container.innerHTML = items.map(item => {
        const escapedName = (item.name || item.market_hash_name || 'Без названия')
            .replace(/'/g, "\\'")
            .replace(/"/g, '&quot;');

        const displayName = item.name || item.market_hash_name || 'Без названия';
        const shortName = displayName.length > 40 ? displayName.substring(0, 40) + '...' : displayName;

        return `
            <div class="item-card">
                <div class="item-image-wrapper">
                    <img src="${getImageUrl(item)}"
                         alt="${displayName}"
                         class="item-image"
                         onerror="this.src='https://via.placeholder.com/200x120/2a2f3d/8a94a6?text=CS:GO'">
                    ${item.amount > 1 ? `<div class="item-quantity">×${item.amount}</div>` : ''}
                </div>
                <div class="item-details">
                    <div class="item-name" title="${displayName}">
                        ${shortName}
                    </div>
                    <div class="item-meta">
                        <div class="item-type">${item.type || 'Предмет'}</div>
                        <div class="item-tradable ${item.tradable ? 'value-positive' : 'value-negative'}">
                            ${item.tradable ? '🔄' : '🔒'}
                        </div>
                    </div>
                </div>
                <div class="item-actions">
                    <button class="action-btn btn-view" onclick="openSteamMarket('${item.market_hash_name || item.name}')" title="Открыть на Steam Market">
                        <i class="fas fa-external-link-alt"></i>
                    </button>
                    <button class="action-btn btn-add" onclick="addToWallet('${item.name || item.market_hash_name}', '${getImageUrl(item)}')"
                            title="Добавить в кошелек" ${!item.tradable ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
                        <i class="fas fa-plus"></i>
                    </button>
                    <button class="action-btn" onclick="openSkinDetailsFromInventory('${escapedName}')"
                            title="Детальная аналитика" style="background: rgba(108, 92, 231, 0.1); color: #6c5ce7; border-color: #6c5ce7;">
                        <i class="fas fa-chart-line"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function updateWalletStats() {
    if (!window.walletItems) return;

    const totalItems = window.walletItems.length;
    const totalValue = window.walletItems.reduce((sum, item) => sum + (item.price || 0), 0);
    const totalProfit = window.walletItems.reduce((sum, item) => sum + (item.profit || 0), 0);

    const itemsCountElem = document.getElementById('wallet-items-count');
    const totalElem = document.getElementById('wallet-total');
    const profitElem = document.getElementById('wallet-profit');
    const growthElem = document.getElementById('wallet-growth');
    const changeElem = document.getElementById('wallet-change');

    if (itemsCountElem) itemsCountElem.textContent = totalItems;
    if (totalElem) totalElem.textContent = `$${totalValue.toFixed(2)}`;
    if (profitElem) profitElem.textContent = `$${totalProfit.toFixed(2)}`;

    if (totalValue > 0) {
        const growth = (totalProfit / totalValue * 100).toFixed(1);
        if (growthElem) {
            growthElem.textContent = `${growth}%`;
            growthElem.className = `wallet-stats-value ${growth >= 0 ? 'value-positive' : 'value-negative'}`;
        }
        if (changeElem) {
            changeElem.textContent = `+${growth}%`;
            changeElem.className = `wallet-stats-change ${growth >= 0 ? 'value-positive' : 'value-negative'}`;
        }
    }
}

function addSampleItems() {
    if (!window.walletItems) {
        window.walletItems = [];
    }

    const sampleItems = [
        {
            name: "Кейс «Киловатт»",
            price: 24.76,
            change: 2.5,
            profit: 1.25,
            image: "https://steamcommunity-a.akamaihd.net/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XsnXwtmkJjSU91dh8bj35VTqVBP4io_frnEVvqf_a6VoIfGSXz7Hlbwg57QwSS_mxhl15jiGyN37c3_GZw91W8BwRflK7EfKsa2sfw"
        },
        {
            name: "Gamma Case",
            price: 477.09,
            change: 1.8,
            profit: 8.50,
            image: "https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XsnXwtmkJjSU91dh8bj35VTqVBP4io_frHEVtvP5bPZrd6XECmOSxe0v4bRoTnnjwBkitWrRm4yoeX3GagMnCZZ2FPlK7EcEv22BnQ/62fx62f"
        }
    ];

    window.walletItems = [...window.walletItems, ...sampleItems];
    localStorage.setItem('walletItems', JSON.stringify(window.walletItems));
    renderWalletItems();

    showNotification('Тестовые предметы добавлены в кошелек!', 'success');
}

function removeFromWallet(index) {
    if (confirm('Удалить этот предмет из кошелька?')) {
        window.walletItems.splice(index, 1);
        localStorage.setItem('walletItems', JSON.stringify(window.walletItems));
        renderWalletItems();
        showNotification('Предмет удален из кошелька', 'info');
    }
}

async function loadCSGOInventory() {
    const container = document.getElementById('inventory-container');
    const refreshBtn = document.getElementById('refresh-btn');

    if (!container || !refreshBtn) return;

    try {
        container.innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>Загрузка инвентаря CS:GO...</p>
            </div>
        `;

        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Загрузка...';
        refreshBtn.disabled = true;

        if (!window.csrftoken || !window.steamId || window.steamId === "Не указан") {
            throw new Error('Steam ID не найден. Пожалуйста, войдите заново.');
        }

        const response = await fetch(`/api/inventory/?appid=730&steam_id=${window.steamId}`, {
            headers: {
                'X-CSRFToken': window.csrftoken
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка загрузки инвентаря');
        }

        const data = await response.json();

        if (data.items && data.items.length > 0) {
            renderInventory(data.items);
        } else {
            showEmptyInventory();
        }

        updateProfileStats(data.items || []);

    } catch (error) {
        console.error('Ошибка:', error);
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Ошибка загрузки</h3>
                <p>${error.message}</p>
                <button class="btn btn-login" onclick="loadCSGOInventory()" style="margin-top: 10px;">
                    <i class="fas fa-redo"></i> Попробовать снова
                </button>
            </div>
        `;
    } finally {
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Обновить инвентарь';
        refreshBtn.disabled = false;
    }
}

function updateProfileStats(items) {
    const totalItems = items.length;
    const tradableItems = items.filter(item => item.tradable).length;
    const uniqueGames = new Set(items.map(item => item.appid)).size;

    const totalItemsElem = document.getElementById('total-items');
    const tradableItemsElem = document.getElementById('tradable-items');
    const gamesCountElem = document.getElementById('games-count');
    const lastUpdateElem = document.getElementById('last-update');

    if (totalItemsElem) totalItemsElem.textContent = totalItems;
    if (tradableItemsElem) tradableItemsElem.textContent = tradableItems;
    if (gamesCountElem) gamesCountElem.textContent = uniqueGames;
    if (lastUpdateElem) lastUpdateElem.textContent = new Date().toLocaleDateString('ru-RU');
}

function addToWallet(itemName, itemImage) {
    if (!window.walletItems) {
        window.walletItems = [];
    }

    const alreadyAdded = window.walletItems.some(walletItem =>
        walletItem.name === itemName
    );

    if (alreadyAdded) {
        showNotification(`"${itemName}" уже добавлен в ваш кошелек!`, 'warning');
        return;
    }

    const newItem = {
        id: Date.now(),
        name: itemName,
        image: itemImage,
        price: Math.random() * 100 + 10,
        change: (Math.random() * 20 - 10).toFixed(1),
        profit: Math.random() * 10,
        category: 'weapon',
        addedDate: new Date().toISOString(),
        url: `https://steamcommunity.com/market/listings/730/${encodeURIComponent(itemName)}`
    };

    window.walletItems.push(newItem);
    localStorage.setItem('walletItems', JSON.stringify(window.walletItems));
    renderWalletItems();

    showNotification(`"${itemName}" добавлен в кошелек!`, 'success');
}

function openSteamMarket(itemName) {
    const encodedName = encodeURIComponent(itemName);
    window.open(`https://steamcommunity.com/market/listings/730/${encodedName}`, '_blank');
}

function viewItemOnMarket(index) {
    if (window.walletItems && window.walletItems[index]) {
        openSteamMarket(window.walletItems[index].name);
    }
}

function analyzeItem(index) {
    if (window.walletItems && window.walletItems[index]) {
        const item = window.walletItems[index];
        alert(`Анализ предмета: ${item.name}\nЦена: $${item.price.toFixed(2)}\nИзменение: ${item.change}%\nПрибыль: $${item.profit.toFixed(2)}`);
    }
}

function showNotification(message, type = 'info') {
    const colors = {
        'success': '#00d09c',
        'error': '#ff4757',
        'info': '#4f7bff',
        'warning': '#ffc107'
    };

    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        display: flex;
        align-items: center;
        gap: 10px;
    `;

    const icon = type === 'success' ? 'check-circle' :
                type === 'error' ? 'exclamation-circle' :
                type === 'warning' ? 'exclamation-triangle' : 'info-circle';

    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);

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

// Инициализация
function initializeProfilePage() {
    // Загружаем инвентарь CS:GO
    loadCSGOInventory();

    // Отображаем кошелек
    renderWalletItems();

    // Обработчики для вкладок игр
    document.querySelectorAll('.game-tab').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.game-tab').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const appid = this.dataset.appid;
            if (appid === '730') {
                loadCSGOInventory();
            } else {
                showNotification('Загрузка инвентаря для этой игры будет доступна в следующем обновлении!', 'info');
            }
        });
    });
}

// Запуск при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем глобальные переменные
    if (!window.walletItems) {
        window.walletItems = JSON.parse(localStorage.getItem('walletItems') || '[]');
    }

    if (!window.csrftoken) {
        window.csrftoken = getCookie('csrftoken');
    }

    // Запускаем инициализацию
    initializeProfilePage();
});