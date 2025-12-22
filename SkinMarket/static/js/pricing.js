document.addEventListener('DOMContentLoaded', function() {
    // Кнопки выбора плана
    const standardBtn = document.querySelector('.btn-standard');
    const proBtn = document.querySelector('.btn-pro');

    if (standardBtn) {
        standardBtn.addEventListener('click', function(e) {
            e.preventDefault();
            selectPlan('standard');
        });
    }

    if (proBtn) {
        proBtn.addEventListener('click', function(e) {
            e.preventDefault();
            selectPlan('pro');
        });
    }

    // Анимация для карточек планов
    const planCards = document.querySelectorAll('.plan-card');
    planCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            if (!this.classList.contains('popular')) {
                this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.4)';
            }
        });

        card.addEventListener('mouseleave', function() {
            if (!this.classList.contains('popular')) {
                this.style.boxShadow = '';
            }
        });
    });
});

// Функция выбора плана
function selectPlan(planType) {
    const plans = {
        'standard': {
            name: 'Стандарт',
            price: '$49.99/месяц',
            features: ['10,000 запросов', '30 запросов/мин', '5 API-сервисов']
        },
        'pro': {
            name: 'Про',
            price: '$99.99/месяц',
            features: ['50,000 запросов', '60 запросов/мин', '5 API-сервисов']
        }
    };

    const plan = plans[planType];
    if (!plan) return;

    // В реальном проекте здесь будет перенаправление на страницу оплаты
    // Сейчас просто показываем сообщение

    const modalHtml = `
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        ">
            <div style="
                background: #1a1f2e;
                border-radius: 16px;
                padding: 40px;
                max-width: 500px;
                width: 90%;
                border: 1px solid #4f7bff;
            ">
                <h3 style="color: #4f7bff; margin-bottom: 20px; text-align: center;">
                    Вы выбрали план "${plan.name}"
                </h3>
                <div style="text-align: center; margin-bottom: 25px;">
                    <div style="font-size: 28px; font-weight: 700; color: #fff; margin-bottom: 10px;">
                        ${plan.price}
                    </div>
                    <div style="color: #8a94a6; margin-bottom: 20px;">
                        ${plan.features.map(f => `<div style="margin-bottom: 5px;">✓ ${f}</div>`).join('')}
                    </div>
                </div>
                <div style="text-align: center; margin-bottom: 20px;">
                    <p style="color: #8a94a6; font-size: 14px;">
                        Сейчас вы будете перенаправлены на страницу оплаты...
                    </p>
                </div>
                <div style="display: flex; gap: 15px; justify-content: center;">
                    <button onclick="this.parentElement.parentElement.remove()" style="
                        padding: 12px 24px;
                        background: rgba(255, 71, 87, 0.1);
                        color: #ff4757;
                        border: 1px solid #ff4757;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: 600;
                    ">
                        Отмена
                    </button>
                    <button onclick="startTrial('${planType}')" style="
                        padding: 12px 24px;
                        background: linear-gradient(90deg, #4f7bff, #6c5ce7);
                        color: white;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: 600;
                    ">
                        Начать пробный период
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// Функция начала пробного периода
function startTrial(planType) {
    alert(`Пробный период для плана ${planType.toUpperCase()} начался!\n\nВ течение 3 дней вы можете тестировать все функции выбранного плана бесплатно.`);
    document.querySelector('.modal-backdrop')?.remove();

    // В реальном проекте здесь будет запрос к серверу
    console.log(`Starting trial for ${planType} plan`);
}