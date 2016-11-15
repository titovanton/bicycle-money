# -*- coding: utf-8 -*-

import re

from django import forms
from django.conf import settings
from bicycle.core.forms import SmartDateTimeField


PAYMENT_TYPE = [
    (u'AC',  u'Онлайн кредитной картой Visa/Mastercard'),
    (u'SB',  u'Оплата через Сбербанк: оплата по SMS или Сбербанк Онлайн'),
    (u'AB',  u'Оплата через Альфа-Клик'),
    (u'PB',  u'Оплата через Промсвязьбанк'),
    (u'PC',  u'Оплата из кошелька в Яндекс.Деньгах'),
    (u'WM',  u'Оплата из кошелька в системе WebMoney'),
    (u'GP',  u'Оплата наличными через кассы и терминалы'),
    (u'MC',  u'Платеж со счета мобильного телефона'),
    (u'MP',  u'Оплата через мобильный терминал (mPOS)'),
    (u'МА',  u'Оплата через MasterPass'),
]


class FormBase(forms.Form):
    requestDatetime = SmartDateTimeField()
    action = forms.CharField()
    md5 = forms.CharField(max_length=32, min_length=32)
    shopId = forms.IntegerField()
    shopArticleId = forms.IntegerField(required=False)
    invoiceId = forms.IntegerField()
    orderNumber = forms.CharField(max_length=64, required=False)
    customerNumber = forms.CharField(max_length=64)
    orderCreatedDatetime = SmartDateTimeField()
    orderSumAmount = forms.DecimalField()
    orderSumCurrencyPaycash = forms.IntegerField()
    orderSumBankPaycash = forms.IntegerField()
    shopSumAmount = forms.DecimalField()
    shopSumCurrencyPaycash = forms.IntegerField()
    shopSumBankPaycash = forms.IntegerField()
    paymentPayerCode = forms.CharField(max_length=33, min_length=11)
    paymentType = forms.ChoiceField(choices=PAYMENT_TYPE)

    def clean_shopId(self):

        if self.cleaned_data['shopId'] != settings.YANDEX_MONEY_SHOPID:
            raise forms.ValidationError('Invalid shopId', code='invalid')

        return self.cleaned_data['shopId']

    def clean_orderSumCurrencyPaycash(self):
        data = self.cleaned_data['orderSumCurrencyPaycash']
        demo = settings.YANDEX_MONEY_DEMO

        if data != 643 and not demo or data != 10643 and demo:
            raise forms.ValidationError('Invalid orderSumCurrencyPaycash', code='invalid')

        return data

    def clean_shopSumCurrencyPaycash(self):
        data = self.cleaned_data['shopSumCurrencyPaycash']
        demo = settings.YANDEX_MONEY_DEMO

        if data != 643 and not demo or data != 10643 and demo:
            raise forms.ValidationError('Invalid shopSumCurrencyPaycash', code='invalid')

        return data

    def clean_orderSumBankPaycash(self):
        data = self.cleaned_data['orderSumBankPaycash']
        demo = settings.YANDEX_MONEY_DEMO

        if data != 1001 and not demo or data != 1003 and demo:
            raise forms.ValidationError('Invalid orderSumBankPaycash', code='invalid')

        return data

    def clean_shopSumBankPaycash(self):
        data = self.cleaned_data['shopSumBankPaycash']
        demo = settings.YANDEX_MONEY_DEMO

        if data != 1001 and not demo or data != 1003 and demo:
            raise forms.ValidationError('Invalid shopSumBankPaycash', code='invalid')

        return data

    def clean_paymentPayerCode(self):
        data = self.cleaned_data['paymentPayerCode']
        payment_payer_code_exp = re.compile(r'[^0-9]')

        if payment_payer_code_exp.search(data) is not None:
            raise forms.ValidationError('Invalid paymentPayerCode', code='invalid')

        return data


class CheckingOrderForm(FormBase):

    def clean_action(self):

        if self.cleaned_data['action'] != 'checkOrder':
            raise forms.ValidationError('Invalid action', code='invalid')

        return self.cleaned_data['action']


class TransferNoticeForm(FormBase):
    paymentDatetime = SmartDateTimeField()
    cps_user_country_code = forms.CharField(max_length=2, min_length=2)

    def clean_action(self):

        if self.cleaned_data['action'] != 'paymentAviso':
            raise forms.ValidationError('Invalid action', code='invalid')

        return self.cleaned_data['action']


class FailOrSuccessForm(forms.Form):
    order_number = forms.CharField(max_length=64)
