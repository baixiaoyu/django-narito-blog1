from django import forms


class SimpleCaptchaField(forms.CharField):

    def __init__(self, label='确认人', **kwargs):
        super().__init__(label=label, required=True, **kwargs)
        self.widget.attrs['placeholder'] = '请用汉字写'

    def clean(self, value):
        value = super().clean(value)
        if value == '狗':
            return value
        else:
            raise forms.ValidationError('答案不对')
