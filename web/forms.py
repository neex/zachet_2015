from wtforms import SelectField, Form, TextField, PasswordField, BooleanField, validators, ValidationError
from models import *

class RegistrationForm(Form):
    username = TextField('Username', [validators.Required(), validators.Length(max=25)])
    def validate_username(form, field):
        if User.query.filter_by(username = field.data).count():
            raise ValidationError('User with such name already exists')
    password = PasswordField('Password', [validators.Required(), validators.Length(max=25)])
    recovery_question = TextField('Question for password recovery', [validators.Required(), validators.Length(max=25)])
    recovery_answer = TextField('Answer', [validators.Required(), validators.Length(max=25)])
    secret = TextField('Your super secret', [validators.Length(max=16)])        

class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=1, max=25)])
    password = PasswordField('Password', [
        validators.Required(),
    ])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user is None:
            self.username.errors.append('Unknown username')
            return False

        if user.password != self.password.data:
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True


class SendForm(Form):
#    user_to = TextField('To', [validators.Length(min=1, max=25)])
    user_to = SelectField('To', [validators.Length(min=1, max=25)])

    text = TextField('Text', [validators.Length(min=1)])
    encrypt = BooleanField('Encrypt the message? ')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False        
        user_to = User.query.filter_by(username=self.user_to.data).first()
        if user_to is None:
            self.user_to.errors.append('Unknown username')
            return False

        if self.encrypt.data and len(self.text.data) > 16:
            self.text.errors.append('Len of encrypted message must be <= 16')
            return False

        return True
        
    
class SendSecretForm(Form):
    user_to = SelectField('To', [validators.Length(min=1, max=25)])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        
        user_to = User.query.filter_by(username=self.user_to.data).first()
        if user_to is None:
            self.user_to.errors.append('Unknown username')
            return False

        return True

class PasswordRecoveryForm(Form):
    username = TextField('Username', [validators.Length(min=1, max=25)])

    def validate(self):
        rv = Form.validate(self)        
        username = User.query.filter_by(username=self.username.data).first()
        if username is None:
            self.username.errors.append('Unknown username')
            return False

        return True


class PasswordRecoveryAnswerForm(Form):
    recovery_answer = TextField('Answer', [validators.Length(min=1, max=25)])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        return True
        
