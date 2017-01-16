var mistakes = 0

function check_email() {
    var request = new XMLHttpRequest();
    var error = ''
    request.open('GET', '/accounts/check_unique/?email=' + $('#id_email').val(), false);  // `false` makes the request synchronous
    request.send(null);

    if (request.status === 200)
        if (JSON.parse(request.responseText).email == '1')
            error = 'Почта уже используется';
    return error
}

function check_field(event) {
    var error = '';
    if (event.data == 'first_name'){
        if (!(/^^[А-ЯЁA-Z][а-яёa-z]+$/.test($('#id_first_name').val()))) error += 'Должно начинается с большой буквы';
    }
    if (event.data == 'last_name'){
        if (!(/^[А-ЯЁA-Z][а-яёa-z]+$/.test($('#id_last_name').val()))) error += 'Должно начинается с большой буквы';
    }
    if (event.data == 'email'){
        if (!(/^.+@.+\..+$/.test($('#id_email').val()))) error += 'Формат example@domain.com';
        error += check_email();
    }
    if (event.data == 'password'){
        if (($('#id_password').val()).length < 6) error += 'Слишком короткий - нужно больше 5 символов<br>';
        if (($('#id_password').val()).length > 30) error += 'Слишком длинный - нужно меньше 30 символов<br>';
        event.data = 'password_repeat'
        check_field(event)
        event.data = 'password'
    }
    if (event.data == 'password_repeat'){
        if ($('#id_password').val() != $('#id_password_repeat').val()) error += 'Пароли не совпадают';
    }

    if ($('.errorlist-'+event.data).length != 0){
        $('.errorlist-'+event.data).remove();
        mistakes-=1;
    }
    if (error !== '') {
        mistakes+=1;
        $('#signup_form').find('#id_'+event.data).after('<ul class="errorlist errorlist-'+event.data+'"><li>' + error + '</li></ul>');
        $('#subbutton').attr('disabled', 'true');
        $('#subbutton').addClass('disabled');
    }
}


$(document).ready(function () {
    setInterval(function () {
        if (
        $('#id_password').val() === '' |
        $('#id_password_repeat').val() === '' |
        $('#id_email').val() === '' |
        $('#id_first_name').val() === '' |
        $('#id_last_name').val() === '') {
            $('#subbutton').attr('disabled', 'true');
            $('#subbutton').addClass('disabled');
            $('#subbutton').html('Заполните все поля');
        } else {
            if (mistakes > 0) {
                $('#subbutton').attr('disabled', 'true');
                $('#subbutton').addClass('disabled');
                $('#subbutton').html('Исправьте ошибки');
            } else {
                $('#subbutton').removeAttr('disabled');
                $('#subbutton').removeClass('disabled');
                $('#subbutton').html('Зарегистрироваться');
            }
        }
    }, 10);

    var fields = ['email', 'first_name', 'last_name', 'password', 'password_repeat', 'organisation'];
    for (i in fields)
        $('#id_'+fields[i]).blur(fields[i], check_field);
});
