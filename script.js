// Демо-данные сотрудника
const employee = {
    name: 'Алексей Петрович Иванов',
    email: 'support@eris.ru',
    phone: '+7 (495) 123-45-67'
};

// Демо-данные заявок пользователей
let tickets = [
    {
        id: 1,
        date: '2026-02-23 09:15',
        fio: 'Иван Смирнов',
        object: 'ООО "Газпром нефть"',
        phone: '+7 (912) 345-67-89',
        email: 'ivan@example.com',
        serialNumbers: 'ГА-2024-001, ГА-2024-002',
        subject: 'Неисправность газоанализатора',
        tone: 'негативная',
        status: 'в обработке',
        response: ''
    },
    {
        id: 2,
        date: '2026-02-23 10:30',
        fio: 'Елена Петрова',
        object: 'АО "Северсталь"',
        phone: '+7 (921) 456-78-90',
        email: 'elena@example.com',
        serialNumbers: 'ГА-2024-045',
        subject: 'Запрос на калибровку',
        tone: 'нейтральная',
        status: 'новая',
        response: ''
    },
    {
        id: 3,
        date: '2026-02-22 16:45',
        fio: 'Михаил Соколов',
        object: 'ООО "Лукойл"',
        phone: '+7 (915) 567-89-01',
        email: 'mikhail@example.com',
        serialNumbers: 'ГА-2023-112, ГА-2023-113',
        subject: 'Требуется документация',
        tone: 'позитивная',
        status: 'закрыта',
        response: 'Документация отправлена на email'
    },
    {
        id: 4,
        date: '2026-02-23 11:20',
        fio: 'Анна Кузнецова',
        object: 'АЭС "Калининская"',
        phone: '+7 (918) 678-90-12',
        email: 'anna@example.com',
        serialNumbers: 'ГА-2024-078',
        subject: 'Срочная неисправность',
        tone: 'негативная',
        status: 'новая',
        response: ''
    }
];

// Авторизация
function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (email && password.length > 0) {
        if (email.includes('@')) {
            // Скрываем страницу авторизации
            document.getElementById('loginPage').style.display = 'none';
            // Показываем страницу профиля
            document.getElementById('profilePage').style.display = 'block';
            
            // Заполняем данные сотрудника
            document.getElementById('employeeName').textContent = employee.name;
            document.getElementById('employeeEmail').textContent = employee.email;
            document.getElementById('employeePhone').textContent = employee.phone;
            
            // Загружаем таблицу заявок
            renderTickets();
            
            // Очищаем ошибку
            document.getElementById('loginError').innerHTML = '';
        } else {
            document.getElementById('loginError').innerHTML = 'Введите корректный email';
        }
    } else {
        document.getElementById('loginError').innerHTML = 'Введите email и пароль';
    }
}

// Выход
function logout() {
    // Скрываем страницу профиля
    document.getElementById('profilePage').style.display = 'none';
    // Показываем страницу авторизации
    document.getElementById('loginPage').style.display = 'block';
    // Очищаем поля
    document.getElementById('email').value = 'support@eris.ru';
    document.getElementById('password').value = '123456';
    document.getElementById('loginError').innerHTML = '';
}

// Отправить ответ на заявку
function sendResponse(ticketId) {
    const responseInput = document.getElementById(`response-${ticketId}`);
    const responseText = responseInput.value.trim();
    
    if (responseText) {
        const ticket = tickets.find(t => t.id === ticketId);
        if (ticket) {
            ticket.response = responseText;
            ticket.status = 'закрыта';
            renderTickets();
            responseInput.value = '';
        }
    } else {
        alert('Введите текст ответа');
    }
}

// Отображение заявок в таблице
function renderTickets() {
    const tbody = document.getElementById('ticketsBody');
    tbody.innerHTML = '';

    tickets.forEach(ticket => {
        const row = document.createElement('tr');

        // Ячейка с ответом
        let responseCell = '';
        if (ticket.response) {
            responseCell = `✓ Ответ отправлен: "${ticket.response}"`;
        } else {
            responseCell = `
                <textarea id="response-${ticket.id}" rows="2" cols="25" placeholder="Введите ответ..."></textarea><br>
                <button onclick="sendResponse(${ticket.id})">Отправить ответ</button>
            `;
        }

        row.innerHTML = `
            <td>${ticket.date}</td>
            <td><strong>${ticket.fio}</strong></td>
            <td>${ticket.object}</td>
            <td>${ticket.phone}</td>
            <td>${ticket.email}</td>
            <td>${ticket.serialNumbers}</td>
            <td>${ticket.subject}</td>
            <td>${ticket.tone}</td>
            <td>${ticket.status}</td>
            <td>${responseCell}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// При загрузке страницы показываем только логин
window.onload = function() {
    document.getElementById('loginPage').style.display = 'block';
    document.getElementById('profilePage').style.display = 'none';
};