from django.core.exceptions import ValidationError


class CustomPasswordValidator:
    def __call__(self, value):
        self.validate(value)

    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError("비밀번호는 8자리 이상이어야 합니다.")
        if not any(char.isalpha() for char in password):
            raise ValidationError("비밀번호는 하나 이상의 영문이 포함되어야 합니다.")
        if not any(char.isalpha() for char in password):
            raise ValidationError("비밀번호는 하나 이상의 숫자가 포함되어야 합니다.")
        if not any(char in "~!@#$%^&*()_+|<>?:{}" for char in password):
            raise ValidationError(
                "비밀번호는 적어도 하나 이상의 특수문자(~!@#$%^&*()_+|<>?:{})가 포함되어야 합니다.")

    def get_help_text(self):
        return "비밀번호는 8자리 이상이며 영문, 숫자, 특수문자(~!@#$%^&*()_+|<>?:{})를 포함해야 합니다."
