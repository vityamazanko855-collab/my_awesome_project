<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>bot бандит — криминальная игра в Telegram</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #0a0c12;
            font-family: 'Segoe UI', system-ui, -apple-system, 'Roboto', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        /* Телефон-подобный контейнер */
        .phone {
            max-width: 420px;
            width: 100%;
            background: #0f1117;
            border-radius: 36px;
            box-shadow: 0 25px 45px rgba(0, 0, 0, 0.5), 0 0 0 8px #2c2f3a;
            overflow: hidden;
            position: relative;
        }

        /* Шапка как в скриншотах */
        .header {
            background: #1a1d27;
            padding: 18px 20px 12px 20px;
            border-bottom: 1px solid #2a2e3c;
        }

        .bot-name {
            font-size: 24px;
            font-weight: 800;
            color: #ffd966;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .bot-name span:first-child {
            background: #2a2e3c;
            padding: 4px 12px;
            border-radius: 40px;
            font-size: 14px;
            font-weight: normal;
            color: #bbb;
        }

        .stats {
            display: flex;
            gap: 12px;
            margin-top: 12px;
            font-size: 13px;
            color: #8e92a2;
        }

        /* Основная прокрутка */
        .chat-area {
            height: 540px;
            overflow-y: auto;
            padding: 16px 18px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            background: #0b0e14;
            scroll-behavior: smooth;
        }

        /* Стили сообщений */
        .message {
            background: #151a24;
            border-radius: 20px;
            padding: 14px 16px;
            border-left: 3px solid #ffb347;
            color: #eef2ff;
            font-size: 15px;
            line-height: 1.45;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        .message strong {
            color: #ffb347;
        }

        .game-panel {
            background: #10131c;
            border-radius: 24px;
            padding: 18px;
            margin: 4px 0;
            border: 1px solid #292e3e;
        }

        .button-group {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 18px;
        }

        .btn {
            background: #232a36;
            border: none;
            padding: 12px 18px;
            border-radius: 60px;
            font-weight: 600;
            font-size: 15px;
            color: white;
            cursor: pointer;
            transition: 0.2s;
            flex: 1 0 auto;
            text-align: center;
            font-family: inherit;
            box-shadow: 0 1px 2px black;
        }

        .btn-primary {
            background: #ff914d;
            color: #0b0e14;
            font-weight: 800;
        }

        .btn-warning {
            background: #3a2c1f;
            border: 1px solid #ffb347;
            color: #ffcd85;
        }

        .btn-danger {
            background: #5a2a2a;
            color: #ffa098;
        }

        .btn-success {
            background: #2c5a3a;
            color: #c0ffb0;
        }

        .inline-buttons {
            display: flex;
            gap: 10px;
            margin-top: 12px;
            flex-wrap: wrap;
        }

        .badge {
            background: #1f2533;
            border-radius: 30px;
            padding: 6px 14px;
            font-size: 13px;
            display: inline-block;
            margin-bottom: 8px;
        }

        .money {
            color: #6fcf97;
            font-weight: bold;
        }

        .footer-input {
            background: #11141e;
            padding: 12px 18px;
            border-top: 1px solid #252a38;
            display: flex;
            gap: 8px;
        }

        .footer-input input {
            flex: 1;
            background: #1e232f;
            border: none;
            padding: 12px;
            border-radius: 32px;
            color: white;
            font-size: 14px;
            outline: none;
        }

        .footer-input button {
            background: #ff914d;
            border: none;
            border-radius: 32px;
            padding: 0 20px;
            font-weight: bold;
            cursor: pointer;
        }

        /* полоса прокрутки */
        .chat-area::-webkit-scrollbar {
            width: 4px;
        }
        .chat-area::-webkit-scrollbar-track {
            background: #1a1e2a;
        }
        .chat-area::-webkit-scrollbar-thumb {
            background: #ff914d;
            border-radius: 10px;
        }
    </style>
</head>
<body>
<div class="phone">
    <div class="header">
        <div class="bot-name">
            <span># bot бандит</span>
            <span style="font-size:14px;">20,977 📢</span>
        </div>
        <div class="stats">
            <span>👥 пользователей</span>
            <span>⚡ живая игра</span>
        </div>
    </div>

    <div class="chat-area" id="chatMessages">
        <!-- Динамические сообщения будут добавляться сюда -->
        <div class="message"><strong>бот бандит</strong> — это игра прямо в твоём Telegram-чате.<br>💰 можно зарабатывать деньги, делать бизнес, покупать недвижимость, тачки и шмотки.</div>
        <div class="message">📅 20 апреля<br>🔹 /start 13:02</div>
        <div class="game-panel" id="regPanel">
            <div><strong>✨ регистрация</strong></div>
            <div style="margin: 12px 0;">привет! у тебя ещё нет человечка в бот бандите!<br>давай это исправим.</div>
            <div class="button-group">
                <button class="btn btn-primary" id="createHumanBtn">✔ создать человечка</button>
            </div>
        </div>
    </div>

    <div class="footer-input">
        <input type="text" id="chatInput" placeholder="Напиши сообщение...">
        <button id="sendMsgBtn">➤</button>
    </div>
</div>

<script>
    // ---------- ИГРОВОЕ СОСТОЯНИЕ ----------
    let player = {
        name: null,
        skinColor: null,
        hair: null,
        money: 50000,
        taxiTripsDone: 0,      // нужно 1 поездку для задания
        taxiJobUnlocked: true,  // таксист доступен
        clothesShopUnlocked: false,
        otherJobsUnlocked: false,
        inGame: false,          // зарегистрирован?
        currentTrip: null,      // { passengerName, destination, endTime }
        tripTimer: null,
        taxiStarted: false
    };

    const chatContainer = document.getElementById('chatMessages');
    const regPanelDiv = document.getElementById('regPanel');

    // Вспомогательная: добавить сообщение в чат (с прокруткой вниз)
    function addMessage(text, isSystem = true, isError = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message';
        if (isError) msgDiv.style.borderLeftColor = '#e34d4d';
        msgDiv.innerHTML = isSystem ? `<strong>🤖 бот бандит</strong><br>${text}` : text;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Обновить главный интерфейс (панель регистрации/меню)
    function updateMainUI() {
        if (!player.inGame) {
            // Панель регистрации видна
            if (regPanelDiv) regPanelDiv.style.display = 'block';
            return;
        }
        if (regPanelDiv) regPanelDiv.style.display = 'none';

        // Если игрок в игре, покажем динамическое меню с балансом и заданиями
        // но чтобы не дублировать, добавим информационную карточку, если её нет
        const existingInfo = document.getElementById('dynamicGameInfo');
        if (existingInfo) existingInfo.remove();

        const infoPanel = document.createElement('div');
        infoPanel.id = 'dynamicGameInfo';
        infoPanel.className = 'game-panel';
        infoPanel.innerHTML = `
            <div>👋 здравствуй, ${player.name || 'игрок'}! на счету у тя <span class="money">$${player.money.toLocaleString()}</span>.</div>
            <div style="margin: 10px 0;">📋 задание: <strong>сделать 1 поездку на работе таксиста</strong> ${player.taxiTripsDone >= 1 ? '✅ выполнено!' : `(сделано ${player.taxiTripsDone}/1)`}</div>
            <div class="button-group">
                <button class="btn" id="showJobsBtn">🚕 работа / задания</button>
                <button class="btn" id="resetGameBtn" style="background:#2a2a36;">🔄 пересоздать персонажа</button>
            </div>
        `;
        chatContainer.appendChild(infoPanel);

        // обработчики кнопок меню
        document.getElementById('showJobsBtn')?.addEventListener('click', () => showWorkMenu());
        document.getElementById('resetGameBtn')?.addEventListener('click', () => resetGame());
        
        // Если задание выполнено — даём награду
        if (player.taxiTripsDone >= 1 && !player.otherJobsUnlocked) {
            player.otherJobsUnlocked = true;
            player.clothesShopUnlocked = true;
            addMessage(`🎉 Поздравляю! Ты выполнил первое задание! Разблокированы: другие работы, магазин одежды. +$50.000!`);
            player.money += 50000;
            addMessage(`💰 Твой баланс: $${player.money.toLocaleString()}. Теперь можешь зайти в /menu → работа`);
            updateMainUI(); // обновить отображение баланса
        }
    }

    // Меню выбора работ
    function showWorkMenu() {
        addMessage(`🚖 Работа: выбери профессию, ${player.name}.`, true);
        const workPanel = document.createElement('div');
        workPanel.className = 'game-panel';
        workPanel.innerHTML = `
            <div><strong>Доступные работы</strong></div>
            <div class="button-group">
                <button class="btn btn-primary" id="taxiWorkBtn">🚕 Таксист (доступен)</button>
                ${player.otherJobsUnlocked ? '<button class="btn" id="otherWorkBtn" disabled style="opacity:0.6;">🏭 Бизнесмен (скоро)</button>' : '<button class="btn" disabled>🔒 Другие работы (выполни задание)</button>'}
                <button class="btn" id="backToMenuBtn">◀ Назад</button>
            </div>
        `;
        chatContainer.appendChild(workPanel);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        document.getElementById('taxiWorkBtn')?.addEventListener('click', () => {
            workPanel.remove();
            startTaxiJob();
        });
        document.getElementById('backToMenuBtn')?.addEventListener('click', () => {
            workPanel.remove();
            updateMainUI();
        });
    }

    // Работа таксиста (полный цикл)
    function startTaxiJob() {
        addMessage(`🚕 Ты находишься в таксопарке города "LAS-VEGAS". Транспорт — Cabbie (скорость 20 км/мин). Поездок до завершения задания: ${player.taxiTripsDone >= 1 ? '0 (задание готово!)' : '1'}`);
        
        const taxiPanel = document.createElement('div');
        taxiPanel.className = 'game-panel';
        taxiPanel.innerHTML = `
            <div>📍 твой автомобиль: <strong>Cabbie</strong> (номер TAX3)</div>
            <div>🚗 выбери машину, чтобы начать поездку:</div>
            <div class="inline-buttons">
                <button class="btn btn-warning" data-car="TAX2">TAX2</button>
                <button class="btn btn-warning" data-car="TAX5">TAX5</button>
                <button class="btn btn-primary" data-car="TAX3">TAX3 (твоя)</button>
                <button class="btn" data-car="TAX4">TAX4</button>
                <button class="btn" data-car="TAX9">TAX9</button>
                <button class="btn" data-car="TAX1">TAX1</button>
            </div>
            <div class="button-group" style="margin-top:12px;">
                <button class="btn" id="cancelTaxiBtn">◀ Вернуться</button>
            </div>
        `;
        chatContainer.appendChild(taxiPanel);
        
        // Обработчики выбора машин
        const carBtns = taxiPanel.querySelectorAll('[data-car]');
        carBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const chosen = btn.getAttribute('data-car');
                if (chosen !== 'TAX3') {
                    addMessage(`😵 ты выбрал не ту машину! Ты теребил замок чужого такси, клиент отменил заказ... Попробуй ещё раз.`, true, true);
                    taxiPanel.remove();
                    setTimeout(() => startTaxiJob(), 300);
                } else {
                    addMessage(`✅ Ты взял ключи от своей ласточки "${chosen}". Клиент уже ждёт!`);
                    taxiPanel.remove();
                    startPassengerTrip();
                }
            });
        });
        document.getElementById('cancelTaxiBtn')?.addEventListener('click', () => {
            taxiPanel.remove();
            showWorkMenu();
        });
    }

    // Пассажир и поездка
    function startPassengerTrip() {
        if (player.currentTrip) {
            addMessage(`⚠️ У тебя уже есть активная поездка! Заверши её.`);
            return;
        }
        const randomNames = ["Писюн", "Джек Воробей", "Мистер Кэш", "Леди Удача", "Босс", "Серёга"];
        const destinations = ["РОДИНА-МАТУШКА", "Аэропорт", "Казино Royale", "Пентхаус", "Полицейский участок", "Пляж Лас-Вегаса"];
        const passenger = randomNames[Math.floor(Math.random() * randomNames.length)];
        const dest = destinations[Math.floor(Math.random() * destinations.length)];
        const travelSeconds = 5; // 5 секунд для демонстрации, но в духе игры (имитация 1 минуты)
        
        addMessage(`🚕 К тебе подсел <strong>${passenger}</strong>. Вы направляетесь в город "${dest}". Прибудете через ${travelSeconds} сек. Общайся с пассажиром через чат!`);
        
        player.currentTrip = {
            passengerName: passenger,
            destination: dest,
            remainingSec: travelSeconds,
            active: true
        };
        
        // Таймер обратного отсчёта
        let counter = travelSeconds;
        const interval = setInterval(() => {
            if (!player.currentTrip || !player.currentTrip.active) {
                clearInterval(interval);
                return;
            }
            counter--;
            if (counter <= 0) {
                clearInterval(interval);
                finishTripSuccess();
            } else {
                // обновим сообщение в реальном времени (можно добавить мелкий апдейт)
                const timerMsg = document.querySelector('.timer-message');
                if (!timerMsg) {
                    const msg = addMessageDynamic(`⏳ Осталось ${counter} сек. Нажми "обновить время" после прибытия.`, false);
                    if(msg) msg.classList.add('timer-message');
                } else {
                    timerMsg.innerHTML = `<strong>🤖 бот бандит</strong><br>⏳ Осталось ${counter} сек. Нажми "обновить время" для высадки.`;
                }
            }
        }, 1000);
        
        // Кнопка обновить время / завершить поездку
        const completeDiv = document.createElement('div');
        completeDiv.className = 'game-panel';
        completeDiv.id = 'tripCompletePanel';
        completeDiv.innerHTML = `
            <div>🚕 везёшь реального игрока (${passenger}) — напиши что-нибудь в чат!</div>
            <button class="btn btn-success" id="finishTripBtn">✅ обновить время / высадить пассажира</button>
        `;
        chatContainer.appendChild(completeDiv);
        
        const finishBtn = document.getElementById('finishTripBtn');
        const finishHandler = () => {
            if (player.currentTrip && player.currentTrip.active) {
                clearInterval(interval);
                finishTripSuccess();
                completeDiv.remove();
            } else {
                addMessage("Поездка уже завершена!", true);
                completeDiv.remove();
            }
        };
        finishBtn?.addEventListener('click', finishHandler);
        
        // сохраним cleanup
        player.tripTimer = { interval, completeDiv, finishHandler };
    }
    
    function finishTripSuccess() {
        if (!player.currentTrip) return;
        const earned = 2500;
        player.money += earned;
        addMessage(`✅ Ты успешно высадил пассажира ${player.currentTrip.passengerName}! Заработано: $${earned}. Баланс: $${player.money.toLocaleString()}.`);
        
        if (player.taxiTripsDone === 0) {
            player.taxiTripsDone = 1;
            addMessage(`🎯 Задание выполнено: 1 поездка таксиста! Теперь тебе доступны другие работы и магазин одежды. +$50.000 на счёт!`);
            player.money += 50000;
            player.otherJobsUnlocked = true;
            player.clothesShopUnlocked = true;
            addMessage(`💰 Новый баланс: $${player.money.toLocaleString()}`);
        } else {
            addMessage(`🚕 Отличная работа! Можешь продолжать возить пассажиров через меню "работа".`);
        }
        
        // убираем активную поездку
        if (player.tripTimer && player.tripTimer.interval) clearInterval(player.tripTimer.interval);
        if (player.tripTimer && player.tripTimer.completeDiv) player.tripTimer.completeDiv.remove();
        player.currentTrip = null;
        
        // обновить меню
        updateMainUI();
    }
    
    // Функция добавления временного сообщения без пересоздания
    function addMessageDynamic(text, isSystem = true) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message';
        msgDiv.innerHTML = isSystem ? `<strong>🤖 бот бандит</strong><br>${text}` : text;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return msgDiv;
    }
    
    // ----- Регистрация с кастомизацией -----
    let regStep = 0; // 0: start, 1: skin, 2: hair, 3: name
    let tempSkin = null;
    let tempHair = null;
    
    function startRegistration() {
        regStep = 1;
        updateRegUI();
    }
    
    function updateRegUI() {
        if (!regPanelDiv) return;
        if (regStep === 1) {
            regPanelDiv.innerHTML = `
                <div><strong>🎨 выбирай цвет кожи:</strong></div>
                <div class="button-group">
                    <button class="btn" id="skinLight">светлый</button>
                    <button class="btn" id="skinDark">тёмный</button>
                    <button class="btn btn-danger" id="noGenderBtn">я не мужик 😂</button>
                </div>
            `;
            document.getElementById('skinLight')?.addEventListener('click', () => { tempSkin = 'светлый'; nextStep(); });
            document.getElementById('skinDark')?.addEventListener('click', () => { tempSkin = 'тёмный'; nextStep(); });
            document.getElementById('noGenderBtn')?.addEventListener('click', () => { tempSkin = '😜 унисекс'; nextStep(); });
        } else if (regStep === 2) {
            regPanelDiv.innerHTML = `
                <div><strong>💇 теперь причёска — выбирай:</strong></div>
                <div class="button-group">
                    <button class="btn">Классика</button>
                    <button class="btn">Андеркат</button>
                    <button class="btn">Дреды</button>
                    <button class="btn">Лысый</button>
                    <button class="btn btn-warning" id="noHairBtn">ничего не нравится</button>
                </div>
            `;
            const allHairBtns = regPanelDiv.querySelectorAll('.btn:not(#noHairBtn)');
            allHairBtns.forEach(btn => {
              
