# Yandex Money

This app provide only architecture of a View class. In terms of Java it calls Interface Class.
It also contains the forms classes, for communication with the service through HTTP POST.
The protocol description you will find [here](https://money.yandex.ru/doc.xml?id=526537).
Also, your client will recive a "Technical form", that you should fill.

## Setup

The first step is a line in your settings.py file, which contain a secret word of your shop.
That word is the same you set in a "Tech. form":

    # settings.py
    YANDEX_MONEY_SECRET_WORD = u'some random sequence'

Also you should recived a shopId and scid from the operator:

    # settings.py
    YANDEX_MONEY_SHOPID = 1234
    YANDEX_MONEY_SCID = 4321

