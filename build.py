"""Сборка страниц стенда: общий каркас + тело и скрипт каждой задачи.

python3 build.py  — перезаписывает *.html рядом с собой.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

LAYOUT = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Учебный кабинет</title>
<link rel="stylesheet" href="stend.css">
<script src="stend.js"></script>
</head>
<body>
<header><a class="brand" href="index.html">Учебный кабинет</a><a href="kabinet.html">Кабинет</a><a href="tovary.html">Каталог</a><a href="baza.html">База знаний</a><a href="birzha.html">Заказы</a></header>
<main>
<h1>{title}</h1>
{body}
</main>
<footer>Стенд для проверки браузерных исполнителей. Данные никуда не отправляются: всё остаётся в этом браузере.</footer>
<script>
{script}
</script>
</body>
</html>
"""

PAGES = {}


def page(name, title, body, script=""):
    PAGES[name] = (title, body, script)


# 1. Регистрация -------------------------------------------------------------
page("reg.html", "Регистрация", """
<form class="card" id="f" novalidate>
  <label for="name">Имя и фамилия</label><input type="text" id="name" name="name" required>
  <label for="email">Электронная почта</label><input type="email" id="email" name="email" required>
  <label for="p1">Пароль</label><input type="password" id="p1" name="password" required>
  <label for="p2">Повторите пароль</label><input type="password" id="p2" name="password2" required>
  <label class="switch" for="agree"><input type="checkbox" id="agree" name="agree"><span class="knob"></span>Согласен с правилами сервиса</label>
  <button type="submit">Создать аккаунт</button>
  <div id="msg"></div>
</form>""", """
Stend.$('#f').addEventListener('submit', function (e) {
  e.preventDefault();
  var name = Stend.$('#name').value.trim(), email = Stend.$('#email').value.trim();
  var p1 = Stend.$('#p1').value, p2 = Stend.$('#p2').value, msg = Stend.$('#msg');
  if (!name || !email || !p1) { msg.className = 'err'; msg.textContent = 'Заполните все поля'; return; }
  if (p1 !== p2) { msg.className = 'err'; msg.textContent = 'Пароли не совпадают'; return; }
  if (!Stend.$('#agree').checked) { msg.className = 'err'; msg.textContent = 'Нужно согласие с правилами'; return; }
  Stend.log('register', {name: name, email: email, password_len: p1.length});
  Stend.$('#f').innerHTML = '<div class="ok">Аккаунт создан. Письмо для подтверждения отправлено на ' + email + '</div><a class="btn" href="login.html">Войти</a>';
});""")

# 2. Вход ---------------------------------------------------------------------
# Пароль стенда — значение доступа «brauzer-stend» в хранилище; на странице
# лежит только его SHA-256.
page("login.html", "Вход", """
<form class="card" id="f">
  <label for="login">Логин</label><input type="text" id="login" name="login" autocomplete="username">
  <label for="pass">Пароль</label><input type="password" id="pass" name="pass" autocomplete="current-password">
  <button type="submit">Войти</button>
  <div id="msg"></div>
</form>""", """
var HASH = '__PASS_HASH__';
Stend.$('#f').addEventListener('submit', async function (e) {
  e.preventDefault();
  var login = Stend.$('#login').value.trim(), pass = Stend.$('#pass').value;
  var good = login === 'demo@stend.ru' && (await Stend.sha256(pass)) === HASH;
  Stend.log('login', {login: login, ok: good});
  if (!good) { Stend.$('#msg').className = 'err'; Stend.$('#msg').textContent = 'Неверный логин или пароль'; return; }
  Stend.store('user', login);
  location.href = 'kabinet.html?from=login';
});""")

page("kabinet.html", "Кабинет", """
<div class="card" id="hello"></div>
<div class="card"><a href="zakazy.html">Мои заказы</a> · <a href="nastroyki.html">Настройки</a> · <a href="rekvizity.html">Реквизиты</a> · <a href="chernoviki.html">Черновики откликов</a></div>""", """
var u = Stend.store('user');
Stend.$('#hello').textContent = u ? 'Здравствуйте, ' + u + '! Вы вошли в кабинет.' : 'Вы не вошли. Войдите на странице «Вход».';
Stend.log('cabinet', {user: u || null});""")

# 3. Поиск по базе знаний -----------------------------------------------------
ARTICLES = [
    ("refund", "Как вернуть оплату за заказ", "Возврат денег приходит на карту в течение 10 дней."),
    ("delivery", "Сроки доставки по России", "Курьер привозит заказ за 2–5 дней."),
    ("password", "Как сменить пароль", "Пароль меняется в настройках кабинета."),
    ("invoice", "Счёт для юрлица", "Счёт выставляется после заполнения реквизитов."),
    ("cancel", "Отмена заказа", "Заказ можно отменить до передачи в доставку."),
]
page("baza.html", "База знаний", """
<form class="card search-box" id="f" role="search" action="baza.html">
  <input type="search" id="q" name="q" placeholder="Поиск по статьям" aria-label="Поиск по статьям">
  <button type="submit" class="ghost-submit" tabindex="-1">Найти</button>
</form>
<div class="card" id="res"><p class="muted">Введите запрос и нажмите Enter.</p></div>""", """
var A = %s;
var q = Stend.param('q');
if (q) {
  Stend.$('#q').value = q;
  Stend.log('search', {q: q});
  var words = q.toLowerCase().split(/\\s+/).filter(Boolean);
  var hits = A.filter(function (a) { var t = (a[1] + ' ' + a[2]).toLowerCase();
    return words.some(function (w) { return t.indexOf(w.slice(0, 5)) >= 0; }); });
  Stend.$('#res').innerHTML = hits.length ? '<p>Найдено: ' + hits.length + '</p><ul>' + hits.map(function (a) {
    return '<li><a href="statya.html?id=' + a[0] + '">' + a[1] + '</a></li>'; }).join('') + '</ul>'
    : '<p>Ничего не найдено</p>';
}""" % repr([list(a) for a in ARTICLES]).replace("'", '"'))

page("statya.html", "Статья", """<div class="card" id="art"></div><a href="baza.html">← к поиску</a>""", """
var A = %s;
var id = Stend.param('id'), a = A.filter(function (x) { return x[0] === id; })[0];
Stend.$('#art').innerHTML = a ? '<h2>' + a[1] + '</h2><p>' + a[2] + '</p>' : 'Статья не найдена';
document.title = (a ? a[1] : 'Статья') + ' · Учебный кабинет';
Stend.log('open_article', {id: id});""" % repr([list(a) for a in ARTICLES]).replace("'", '"'))

# 4. Фильтр каталога ----------------------------------------------------------
GOODS = [
    ("n1", "notebooks", "Ноутбук Aster 14", 48900), ("n2", "notebooks", "Ноутбук Lume Pro 16", 112000),
    ("n3", "notebooks", "Ноутбук Kite 13", 36500), ("m1", "monitors", "Монитор View 27", 24900),
    ("m2", "monitors", "Монитор Arc 34", 58900), ("k1", "keyboards", "Клавиатура Tact", 6900),
    ("k2", "keyboards", "Клавиатура Loop TKL", 11900), ("n4", "notebooks", "Ноутбук Aster 15 Air", 52500),
]
page("filtr.html", "Каталог техники", """
<form class="card" id="f">
  <fieldset style="border:0;padding:0"><legend><b>Категория</b></legend>
    <label class="row"><input type="checkbox" name="cat" value="notebooks"> Ноутбуки</label>
    <label class="row"><input type="checkbox" name="cat" value="monitors"> Мониторы</label>
    <label class="row"><input type="checkbox" name="cat" value="keyboards"> Клавиатуры</label>
  </fieldset>
  <label for="max">Цена до</label>
  <select id="max" name="max"><option value="">любая</option><option value="10000">10 000 ₽</option><option value="30000">30 000 ₽</option><option value="50000">50 000 ₽</option><option value="100000">100 000 ₽</option></select>
  <button type="submit">Показать</button>
</form>
<div class="card" id="res"></div>""", """
var G = %s;
function draw(list) { Stend.$('#res').innerHTML = '<p>Товаров: ' + list.length + '</p><table>' + list.map(function (g) {
  return '<tr><td>' + g[2] + '</td><td>' + g[3].toLocaleString('ru-RU') + ' ₽</td></tr>'; }).join('') + '</table>'; }
draw(G);
Stend.$('#f').addEventListener('submit', function (e) {
  e.preventDefault();
  var cats = Stend.$$('input[name=cat]:checked').map(function (i) { return i.value; });
  var max = Number(Stend.$('#max').value) || 0;
  Stend.log('filter', {cats: cats, max: max});
  draw(G.filter(function (g) { return (!cats.length || cats.indexOf(g[1]) >= 0) && (!max || g[3] <= max); }));
});""" % repr([list(g) for g in GOODS]).replace("'", '"'))

# 5. Выпадающий список ------------------------------------------------------
CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", "Нижний Новгород",
          "Челябинск", "Самара", "Омск", "Ростов-на-Дону", "Уфа", "Красноярск", "Воронеж", "Пермь",
          "Волгоград", "Краснодар", "Саратов", "Тюмень", "Тольятти", "Ижевск", "Барнаул", "Ульяновск",
          "Иркутск", "Хабаровск", "Ярославль", "Владивосток", "Махачкала", "Томск", "Оренбург", "Кемерово"]
page("gorod.html", "Профиль доставки", """
<form class="card" id="f">
  <label for="city">Город доставки</label>
  <select id="city" name="city"><option value="">— выберите —</option>%s</select>
  <label for="comment">Комментарий курьеру</label><input type="text" id="comment" name="comment">
  <button type="submit">Сохранить</button><div id="msg"></div>
</form>""" % "".join('<option value="c%d">%s</option>' % (i, c) for i, c in enumerate(CITIES)), """
Stend.$('#f').addEventListener('submit', function (e) {
  e.preventDefault();
  var s = Stend.$('#city');
  if (!s.value) { Stend.$('#msg').className = 'err'; Stend.$('#msg').textContent = 'Выберите город'; return; }
  Stend.log('city', {city: s.options[s.selectedIndex].text});
  Stend.$('#msg').className = 'ok'; Stend.$('#msg').textContent = 'Сохранено: ' + s.options[s.selectedIndex].text;
});""")

# 6. Дата -------------------------------------------------------------------
page("propusk.html", "Заявка на пропуск", """
<form class="card" id="f">
  <label for="fio">ФИО посетителя</label><input type="text" id="fio" name="fio" required>
  <label for="day">Дата визита</label><input type="date" id="day" name="day" min="2026-01-01" required>
  <label for="time">Время</label><select id="time" name="time"><option>10:00</option><option>12:00</option><option>15:00</option><option>17:00</option></select>
  <button type="submit">Сохранить пропуск</button><div id="msg"></div>
</form>""", """
Stend.$('#f').addEventListener('submit', function (e) {
  e.preventDefault();
  var fio = Stend.$('#fio').value.trim(), day = Stend.$('#day').value;
  if (!fio || !day) { Stend.$('#msg').className = 'err'; Stend.$('#msg').textContent = 'Укажите ФИО и дату'; return; }
  Stend.log('pass', {fio: fio, date: day, time: Stend.$('#time').value});
  Stend.$('#msg').className = 'ok'; Stend.$('#msg').textContent = 'Пропуск оформлен: ' + fio + ', ' + day;
});""")

# 7. Многошаговая форма -------------------------------------------------------
page("oformlenie.html", "Оформление заказа", """
<form class="card" id="f">
  <section id="s1"><h2>Шаг 1 из 3. Контакты</h2>
    <label for="cname">Имя</label><input type="text" id="cname" name="cname">
    <label for="phone">Телефон</label><input type="tel" id="phone" name="phone">
    <button type="button" id="next1">Далее</button></section>
  <section id="s2" hidden><h2>Шаг 2 из 3. Доставка</h2>
    <label class="row"><input type="radio" name="how" value="courier"> Курьером</label>
    <label class="row"><input type="radio" name="how" value="pickup"> Самовывоз</label>
    <label for="addr">Адрес доставки</label><input type="text" id="addr" name="addr">
    <button type="button" class="ghost" id="back2">Назад</button> <button type="button" id="next2">Далее</button></section>
  <section id="s3" hidden><h2>Шаг 3 из 3. Подтверждение</h2><p id="sum"></p>
    <button type="button" class="ghost" id="back3">Назад</button> <button type="button" id="confirm">Подтвердить заказ</button></section>
  <div id="msg"></div>
</form>""", """
function step(n) { [1, 2, 3].forEach(function (i) { Stend.show(Stend.$('#s' + i), i === n); }); Stend.$('#msg').textContent = ''; Stend.$('#msg').className = ''; }
function err(t) { Stend.$('#msg').className = 'err'; Stend.$('#msg').textContent = t; }
Stend.$('#next1').onclick = function () { if (!Stend.$('#cname').value.trim() || !Stend.$('#phone').value.trim()) return err('Укажите имя и телефон'); step(2); };
Stend.$('#back2').onclick = function () { step(1); };
Stend.$('#back3').onclick = function () { step(2); };
Stend.$('#next2').onclick = function () {
  var how = (Stend.$('input[name=how]:checked') || {}).value;
  if (!how) return err('Выберите способ доставки');
  if (how === 'courier' && !Stend.$('#addr').value.trim()) return err('Укажите адрес');
  Stend.$('#sum').textContent = Stend.$('#cname').value + ', ' + Stend.$('#phone').value + ', ' + (how === 'courier' ? 'курьером: ' + Stend.$('#addr').value : 'самовывоз');
  step(3);
};
Stend.$('#confirm').onclick = function () {
  var how = Stend.$('input[name=how]:checked').value;
  Stend.log('order', {name: Stend.$('#cname').value.trim(), phone: Stend.$('#phone').value.trim(), how: how, addr: Stend.$('#addr').value.trim()});
  Stend.$('#f').innerHTML = '<div class="ok">Заказ № 5531 оформлен. Мы позвоним для подтверждения.</div>';
};""")

# 8. Биржа: заказ и отклик -----------------------------------------------------
JOBS = [
    ("j1", "Интеграция 1С с сайтом", "60 000 ₽"), ("j2", "Телеграм-бот для записи в салон", "30 000 ₽"),
    ("kofe", "Лендинг для кофейни", "35 000 ₽"), ("j4", "Парсер цен конкурентов", "15 000 ₽"),
    ("j5", "Дизайн карточек для маркетплейса", "12 000 ₽"), ("j6", "Доработка интернет-магазина на Bitrix", "80 000 ₽"),
    ("j7", "Лендинг для студии йоги", "25 000 ₽"), ("j8", "Скрипт выгрузки заказов в Excel", "8 000 ₽"),
]
page("birzha.html", "Заказы на бирже", """
<div class="card"><table>%s</table></div>""" % "".join(
    '<tr><td><a href="zakaz.html?id=%s">%s</a></td><td>%s</td></tr>' % j for j in JOBS), """
Stend.log('jobs', {});""")

page("zakaz.html", "Заказ", """
<div class="card" id="job"></div>
<form class="card" id="f">
  <h2>Ваш отклик</h2>
  <label for="text">Текст отклика</label><textarea id="text" name="text"></textarea>
  <div class="row"><div style="flex:1"><label for="price">Цена, ₽</label><input type="number" id="price" name="price"></div>
  <div style="flex:1"><label for="days">Срок</label><select id="days" name="days"><option value="">—</option><option value="1">1 день</option><option value="3">3 дня</option><option value="5">5 дней</option><option value="7">7 дней</option><option value="14">14 дней</option></select></div></div>
  <button type="submit">Откликнуться</button><div id="msg"></div>
</form>""", """
var J = %s;
var id = Stend.param('id'), j = J.filter(function (x) { return x[0] === id; })[0];
Stend.$('#job').innerHTML = j ? '<h2>' + j[1] + '</h2><p>Бюджет: ' + j[2] + '</p>' : 'Заказ не найден';
document.title = (j ? j[1] : 'Заказ') + ' · Учебный кабинет';
Stend.log('open_job', {id: id});
Stend.$('#f').addEventListener('submit', function (e) {
  e.preventDefault();
  var text = Stend.$('#text').value.trim(), price = Number(Stend.$('#price').value), days = Stend.$('#days').value;
  if (!text || !price || !days) { Stend.$('#msg').className = 'err'; Stend.$('#msg').textContent = 'Заполните текст, цену и срок'; return; }
  Stend.log('bid', {id: id, text_len: text.length, price: price, days: Number(days)});
  Stend.$('#f').innerHTML = '<div class="ok">Отклик отправлен заказчику.</div>';
});""" % repr([list(j) for j in JOBS]).replace("'", '"'))

# 9. Карточка услуги -----------------------------------------------------------
page("usluga.html", "Новая услуга", """
<form class="card" id="f">
  <label for="title">Название услуги</label><input type="text" id="title" name="title">
  <label for="cat">Категория</label><select id="cat" name="cat"><option value="">—</option><option value="web">Сайты и лендинги</option><option value="bots">Чат-боты</option><option value="design">Дизайн</option><option value="integr">Интеграции</option></select>
  <label for="price">Цена от, ₽</label><input type="number" id="price" name="price">
  <label for="about">Описание</label><textarea id="about" name="about"></textarea>
  <label class="switch" for="pub"><input type="checkbox" id="pub" name="pub"><span class="knob"></span>Показывать в каталоге</label>
  <button type="submit">Опубликовать</button><div id="msg"></div>
</form>""", """
Stend.$('#f').addEventListener('submit', function (e) {
  e.preventDefault();
  var d = {title: Stend.$('#title').value.trim(), cat: Stend.$('#cat').value, price: Number(Stend.$('#price').value),
           about_len: Stend.$('#about').value.trim().length, visible: Stend.$('#pub').checked};
  if (!d.title || !d.cat || !d.price || !d.about_len) { Stend.$('#msg').className = 'err'; Stend.$('#msg').textContent = 'Заполните все поля'; return; }
  Stend.log('service', d);
  Stend.$('#f').innerHTML = '<div class="ok">Услуга «' + d.title + '» опубликована.</div>';
});""")

# 10. Настройки -------------------------------------------------------------------
page("nastroyki.html", "Настройки", """
<form class="card" id="f">
  <label for="phone">Телефон</label><input type="tel" id="phone" name="phone" value="+7 912 345-67-89">
  <label class="switch" for="mail"><input type="checkbox" id="mail" name="mail"><span class="knob"></span>Уведомления по почте</label>
  <label class="switch" for="sms"><input type="checkbox" id="sms" name="sms" checked><span class="knob"></span>Уведомления по SMS</label>
  <button type="submit">Сохранить</button><div id="msg"></div>
</form>""", """
Stend.$('#f').addEventListener('submit', function (e) {
  e.preventDefault();
  Stend.log('settings', {phone: Stend.$('#phone').value.trim(), mail: Stend.$('#mail').checked, sms: Stend.$('#sms').checked});
  Stend.$('#msg').className = 'ok'; Stend.$('#msg').textContent = 'Настройки сохранены';
});""")

# 11. Заказы: поиск по номеру и отмена с подтверждением --------------------------
ORDERS = [("1038", "Кофемашина Delonghi", "Доставлен"), ("1042", "Чайник Bork K780", "Собирается"),
          ("1047", "Тостер Kitfort", "Собирается"), ("1051", "Блендер Philips", "Оплачен"),
          ("2077", "Пылесос Dreame L10", "Передан в доставку")]
page("zakazy.html", "Мои заказы", """
<div class="card"><label for="find">Найти заказ по номеру</label><input type="search" id="find" name="find" placeholder="Номер заказа"></div>
<div class="card"><table id="t">%s</table></div>
<div class="modal-back" id="dlg" hidden><div class="modal" role="dialog" aria-modal="true" aria-labelledby="dlgt">
  <h3 id="dlgt">Отменить заказ?</h3><p id="dlgq"></p>
  <button type="button" id="yes">Да, отменить</button> <button type="button" class="ghost" id="no">Нет</button></div></div>""" % "".join(
    '<tr data-id="%s"><td><a href="zakaz-info.html?id=%s">№ %s</a></td><td>%s</td><td class="st">%s</td><td>%s</td></tr>'
    % (o[0], o[0], o[0], o[1], o[2], '<button type="button" class="ghost cancel">Отменить</button>' if o[2] in ("Собирается", "Оплачен") else "")
    for o in ORDERS), """
var target = null;
Stend.$('#find').addEventListener('input', function () {
  var q = this.value.replace(/\\D/g, '');
  Stend.$$('#t tr').forEach(function (tr) { tr.hidden = q && tr.dataset.id.indexOf(q) < 0; });
});
Stend.$$('.cancel').forEach(function (b) { b.onclick = function () {
  target = b.closest('tr'); Stend.$('#dlgq').textContent = 'Заказ № ' + target.dataset.id + ' будет отменён.'; Stend.show(Stend.$('#dlg'), true); }; });
Stend.$('#no').onclick = function () { Stend.show(Stend.$('#dlg'), false); };
Stend.$('#yes').onclick = function () {
  Stend.log('cancel', {id: target.dataset.id});
  target.querySelector('.st').textContent = 'Отменён'; var c = target.querySelector('.cancel'); if (c) c.remove();
  Stend.show(Stend.$('#dlg'), false);
};""")

page("zakaz-info.html", "Заказ", """<div class="card" id="o"></div><a href="zakazy.html">← к заказам</a>""", """
var O = %s;
var id = Stend.param('id'), o = O.filter(function (x) { return x[0] === id; })[0];
Stend.$('#o').innerHTML = o ? '<h2>Заказ № ' + o[0] + '</h2><p>' + o[1] + '</p><p>Статус: <b>' + o[2] + '</b></p>' : 'Заказ не найден';
Stend.log('view_order', {id: id});""" % repr([list(o) for o in ORDERS]).replace("'", '"'))

# 12. Пагинация ------------------------------------------------------------------
ITEMS = ["Чайник Bork K780", "Тостер Kitfort KT-2014", "Блендер Philips HR3655", "Миксер Bosch MFQ", "Соковыжималка Braun",
         "Мультиварка Redmond", "Вафельница Tefal", "Кофеварка Melitta", "Хлебопечка Panasonic", "Мясорубка Moulinex",
         "Пароварка Tefal", "Йогуртница Ariete", "Гриль Tefal Optigrill", "Блинница Kitfort", "Аэрогриль Xiaomi",
         "Сэндвичница Redmond", "Электрогриль Bork", "Кофемолка Bork J800", "Весы кухонные Xiaomi", "Термопот Kitfort"]
page("tovary.html", "Каталог", """
<div class="goods" id="g"></div>
<div class="pager" id="p"></div>""", """
var I = %s, per = 6, n = Number(Stend.param('page') || 1), pages = Math.ceil(I.length / per);
Stend.$('#g').innerHTML = I.slice((n - 1) * per, n * per).map(function (t) {
  return '<div class="card"><a href="tovar.html?name=' + encodeURIComponent(t) + '">' + t + '</a></div>'; }).join('');
Stend.$('#p').innerHTML = 'Страница ' + n + ' из ' + pages + (n > 1 ? ' <a href="tovary.html?page=' + (n - 1) + '">Предыдущая</a>' : '') +
  (n < pages ? ' <a href="tovary.html?page=' + (n + 1) + '">Следующая</a>' : '');
Stend.log('catalog_page', {page: n});""" % repr(ITEMS).replace("'", '"'))

page("tovar.html", "Товар", """<div class="card" id="t"></div><a href="tovary.html">← в каталог</a>""", """
var name = Stend.param('name') || '';
Stend.$('#t').innerHTML = '<h2>' + name.replace(/</g, '') + '</h2><p>В наличии. Доставка завтра.</p><button type="button">В корзину</button>';
document.title = name + ' · Учебный кабинет';
Stend.log('item_open', {name: name});""")

# 13. Подсказки ------------------------------------------------------------------
page("adres.html", "Адрес доставки", """
<form class="card" id="f" autocomplete="off">
  <label for="city">Город</label><input type="text" id="city" name="city" role="combobox" aria-autocomplete="list" aria-controls="sug" aria-expanded="false">
  <ul class="suggest" id="sug" role="listbox" hidden></ul>
  <label for="street">Улица и дом</label><input type="text" id="street" name="street">
  <button type="submit" id="save" disabled>Сохранить адрес</button><div id="msg"></div>
  <p class="muted">Город выбирается только из подсказок.</p>
</form>""", """
var C = %s, picked = '';
Stend.$('#city').addEventListener('input', function () {
  picked = ''; Stend.$('#save').disabled = true;
  var q = this.value.trim().toLowerCase(), list = Stend.$('#sug');
  var hits = q.length < 2 ? [] : C.filter(function (c) { return c.toLowerCase().indexOf(q) === 0 || c.toLowerCase().indexOf(' ' + q) >= 0; }).slice(0, 6);
  list.innerHTML = hits.map(function (c) { return '<li role="option" tabindex="-1">' + c + '</li>'; }).join('');
  Stend.show(list, hits.length > 0); this.setAttribute('aria-expanded', hits.length > 0);
  Stend.$$('#sug li').forEach(function (li) { li.onclick = function () {
    Stend.$('#city').value = li.textContent; picked = li.textContent; Stend.show(list, false); Stend.$('#save').disabled = false; }; });
});
Stend.$('#f').addEventListener('submit', function (e) {
  e.preventDefault();
  if (!picked) return;
  Stend.log('address', {city: picked, street: Stend.$('#street').value.trim()});
  Stend.$('#msg').className = 'ok'; Stend.$('#msg').textContent = 'Адрес сохранён: ' + picked;
});""" % repr(CITIES).replace("'", '"'))

# 14. Вкладки ---------------------------------------------------------------------
page("rekvizity.html", "Компания", """
<div class="card">
  <div class="tabs" role="tablist">
    <button type="button" role="tab" aria-selected="true" aria-controls="t1" id="b1">Профиль</button>
    <button type="button" role="tab" aria-selected="false" aria-controls="t2" id="b2">Реквизиты</button>
    <button type="button" role="tab" aria-selected="false" aria-controls="t3" id="b3">Безопасность</button>
  </div>
  <div role="tabpanel" id="t1"><p>ООО «Учебная компания»</p><label for="brand">Название для клиентов</label><input type="text" id="brand" value="Учебная компания"></div>
  <form role="tabpanel" id="t2" hidden>
    <label for="inn">ИНН</label><input type="text" id="inn" name="inn" inputmode="numeric">
    <label for="kpp">КПП</label><input type="text" id="kpp" name="kpp" inputmode="numeric">
    <button type="submit">Сохранить реквизиты</button><div id="msg"></div>
  </form>
  <div role="tabpanel" id="t3" hidden><p>Двухфакторная защита включена.</p></div>
</div>""", """
Stend.$$('[role=tab]').forEach(function (b) { b.onclick = function () {
  Stend.$$('[role=tab]').forEach(function (x) { x.setAttribute('aria-selected', x === b); Stend.show(Stend.$('#' + x.getAttribute('aria-controls')), x === b); }); }; });
Stend.$('#t2').addEventListener('submit', function (e) {
  e.preventDefault();
  var inn = Stend.$('#inn').value.replace(/\\D/g, ''), kpp = Stend.$('#kpp').value.replace(/\\D/g, '');
  if (inn.length !== 10 || kpp.length !== 9) { Stend.$('#msg').className = 'err'; Stend.$('#msg').textContent = 'ИНН — 10 цифр, КПП — 9'; return; }
  Stend.log('requisites', {inn: inn, kpp: kpp});
  Stend.$('#msg').className = 'ok'; Stend.$('#msg').textContent = 'Реквизиты сохранены';
});""")

# 15. Удаление черновика -------------------------------------------------------------
DRAFTS = ["Отклик на лендинг для кофейни", "Старый отклик на дизайн", "Отклик на телеграм-бота", "Старый отклик на парсер"]
page("chernoviki.html", "Черновики откликов", """
<div class="card"><table id="t">%s</table></div>
<div class="modal-back" id="dlg" hidden><div class="modal" role="dialog" aria-modal="true">
  <h3>Удалить черновик?</h3><p id="q"></p>
  <button type="button" id="yes">Удалить</button> <button type="button" class="ghost" id="no">Отмена</button></div></div>""" % "".join(
    '<tr><td>%s</td><td><button type="button" class="ghost del">Удалить</button></td></tr>' % d for d in DRAFTS), """
var row = null;
Stend.$$('.del').forEach(function (b) { b.onclick = function () {
  row = b.closest('tr'); Stend.$('#q').textContent = '«' + row.cells[0].textContent + '» будет удалён без возврата.'; Stend.show(Stend.$('#dlg'), true); }; });
Stend.$('#no').onclick = function () { Stend.show(Stend.$('#dlg'), false); };
Stend.$('#yes').onclick = function () { Stend.log('delete_draft', {title: row.cells[0].textContent}); row.remove(); Stend.show(Stend.$('#dlg'), false); };""")

# 16. Главная ----------------------------------------------------------------------
page("index.html", "Учебный кабинет", """
<div class="card"><p>Учебный кабинет поставщика: формы, каталог, заказы. Здесь проверяют браузерных исполнителей.</p>
<ul>
<li><a href="reg.html">Регистрация</a></li><li><a href="login.html">Вход</a></li><li><a href="baza.html">База знаний</a></li>
<li><a href="filtr.html">Каталог техники с фильтром</a></li><li><a href="gorod.html">Профиль доставки</a></li>
<li><a href="propusk.html">Заявка на пропуск</a></li><li><a href="oformlenie.html">Оформление заказа</a></li>
<li><a href="birzha.html">Заказы на бирже</a></li><li><a href="usluga.html">Новая услуга</a></li>
<li><a href="nastroyki.html">Настройки</a></li><li><a href="zakazy.html">Мои заказы</a></li>
<li><a href="tovary.html">Каталог</a></li><li><a href="adres.html">Адрес доставки</a></li>
<li><a href="rekvizity.html">Реквизиты компании</a></li><li><a href="chernoviki.html">Черновики откликов</a></li>
</ul></div>""")


def main():
    pass_hash = os.environ.get("STEND_PASS_HASH", "")
    for name, (title, body, script) in PAGES.items():
        html = LAYOUT.format(title=title, body=body.strip(), script=script.strip())
        html = html.replace("__PASS_HASH__", pass_hash)
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as fh:
            fh.write(html)
    print("страниц:", len(PAGES))


if __name__ == "__main__":
    main()
