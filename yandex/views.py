# -*- coding: utf-8 -*-

import datetime
import hashlib
import json
import pytz

from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.views.decorators.csrf import csrf_exempt
from bicycle.core.views import ResponseMixin
from bicycle.core.views import ToDoView

from forms import CheckingOrderForm
from forms import FailOrSuccessForm
from forms import TransferNoticeForm


def md5_validator(cleaned_data):
    keys = [
        'action',
        'orderSumAmount',
        'orderSumCurrencyPaycash',
        'orderSumBankPaycash',
        'shopId',
        'invoiceId',
        'customerNumber',
    ]

    try:
        values = [force_text(cleaned_data[k]) for k in keys] + [settings.YANDEX_MONEY_SECRET_WORD]
    except ValueError:
        return False

    return cleaned_data['md5'].lower() == hashlib.md5(';'.join(values)).hexdigest()


class YandexMoneyBase(ResponseMixin, ToDoView):

    checking_order_form = CheckingOrderForm
    transfer_notice_form = TransferNoticeForm
    fail_or_success_form = FailOrSuccessForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(YandexMoneyBase, self).dispatch(request, *args, **kwargs)

    def _post_handler(self, request, form_class, hook, response_tag):
        form = form_class(request.POST)
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)).isoformat()

        if form.is_valid():

            if md5_validator(form.cleaned_data):
                code, techMessage = hook(request, form)
            else:
                code = 1
                techMessage = u'Authorization error'

            c = {
                'performedDatetime': now,
                'code': code,
                'shopId': settings.YANDEX_MONEY_SHOPID,
                'invoiceId': form.cleaned_data['invoiceId'],
                'orderSumAmount': form.cleaned_data['orderSumAmount'],
            }

            if techMessage is not None:
                c['techMessage'] = techMessage

        else:
            c = {
                'performedDatetime': now,
                'code': form.errors.get('md5') and 1 or 200,
                'shopId': settings.YANDEX_MONEY_SHOPID,
                'invoiceId': request.POST['invoiceId'],
                'orderSumAmount': request.POST['orderSumAmount'],
            }

            c['techMessage'] = json.dumps(form.errors, ensure_ascii=False).replace('"', '\'')

        if c.get('techMessage', False):
            c['message'] = u'Ошибка формата запроса.'

        raw_text = u'<?xml version="1.0" encoding="UTF-8"?>\n'\
            u'<%(response_tag)s\n%(raw_content)s />'
        flat_c = [u'%s="%s"' % (key, c[key]) for key in c]
        raw_content = u'\n'.join(flat_c)
        raw_text = raw_text % {'response_tag': response_tag, 'raw_content': raw_content}

        return self.raw_response(raw_text, content_type='application/xml')

    def post_checking_order(self, request):
        return self._post_handler(request, self.checking_order_form,
                                  self.hook_checking_order, u'checkOrderResponse')

    def post_transfer_notice(self, request):
        return self._post_handler(request, self.transfer_notice_form,
                                  self.hook_transfer_notice, u'paymentAvisoResponse')

    def get_success(self, request):
        form = self.fail_or_success_form(request.GET)

        if form.is_valid():
            return self.hook_success(request, form)

    def post_fail(self, request):
        form = self.fail_or_success_form(request.POST)

        if form.is_valid():
            return self.hook_fail(request, form)
