from wtforms import Form, StringField, PasswordField, BooleanField, validators


class RegistrationForm(Form):
    username = StringField('username', [validators.data_required(),
                                        validators.Length(min=1, max=20)])
    email = StringField('email', [validators.data_required(),
                                  validators.email()])
    password = PasswordField('password', [validators.data_required(),
                                          validators.equal_to('confirm_password', message='two different passwords')])
    confirm_password = PasswordField('confirm_password')


class LoginForm(Form):
    email = StringField('email', [validators.data_required(),
                                  validators.email()])
    password = PasswordField('password', [validators.data_required()])
    admin_log_in = BooleanField('admin_log_in')
