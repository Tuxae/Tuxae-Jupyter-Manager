def is_fake_register_form(form) -> bool:
    return 'email' not in form or 'password1' not in form or 'password2' not in form


def password_validator(form) -> bool:
    return form['password1'] == form['password2']
