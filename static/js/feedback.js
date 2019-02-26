//            Валидация формы
var validators = {
    email: /^(\s*|\w+@\w+\.\w+)$/i,
    tel: /^(\s*|\([1-9]{3}\)[0-9]{7})$/i,
    surname: /^[A-Za-zА-Яа-я]{2,}/i,
    name: /^[A-Za-zА-Яа-я]{2,}/i,
    comment: /[^ ]/i
};
var fields = document.getElementsByClassName('check');
var region_selector = document.getElementById('regions');
var city_selector = document.getElementById('cities');


function showError(container, errorMessage) {
    container.className = 'error';
    var msgElem = document.createElement('div');
    msgElem.className = "error-message";
    msgElem.innerHTML = errorMessage;
    container.appendChild(msgElem);
}

function resetError(container) {
    container.className = '';
    if (container.lastChild.className == "error-message") {
        container.removeChild(container.lastChild);
    }
}

function validateForm(form) {

    var err_founds = false;
    for (var i = 0; i < fields.length; i++) {
        resetError(fields[i].parentNode);
        fields[i].classList.remove('incorrect');
        if (!validators[fields[i].id].test(fields[i].value)) {
            fields[i].classList.add('incorrect');
            showError(fields[i].parentNode, fields[i].getAttribute('title'));
            err_founds = true;
        }
    }
    if (err_founds) {
        return false;
    } else {
        return true;
    }

};

//         Обновление выпадающего списка городов

region_selector.onchange = function () {
    var selectedOption = region_selector.options[region_selector.selectedIndex].value;
    var xhr = new XMLHttpRequest();
    var url = "server_address/get_cities/" + selectedOption;
    xhr.open('GET', url);
    //            xhr.responseType = 'text';
    xhr.send();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            city_data = JSON.parse(xhr.responseText);
            for (var i = 0; i < city_selector.length; i++) {
                if (city_selector.options[i].value != '0')
                    city_selector.remove(i);
            }
            var s = city_selector.options;
            city_data.forEach(function (item, i, city_data) {
                s[s.length] = new Option(item[1], item[0]);
            });
            //  сity_selector.innerHTML = "<option value='0' selected>Выберите город</option>" + xhr.responseText;
        };
    };
};
