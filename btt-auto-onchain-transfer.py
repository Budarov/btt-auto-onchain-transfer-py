import requests
import json
from datetime import datetime
import os.path, sys


#Указываем ваш порт speed.btt.network
speed_btt_port = 54426
#Минимальный баланс на шлюзе, с учетом знаков после запятой.
# Т.е. 1000 Btt = 1000.000000 Btt. В переменную пишем без точки. 
min_tronscan_balance = 10000000000
#Сколько переводим за раз.
#Доджно быть больше 1000 Btt, т.е. минимум 1000000000
min_transfer_sum = 1000000000

#Получаем текующие дату и время
current_time = datetime.now()
current_time = current_time.strftime("%d-%m-%Y, %H:%M:%S")

#Пишем сообщения в log файл и выводим их в консоль
def to_log(massage):
    #Получаем текующие дату и время
    massage = ' ' + massage
    current_time = datetime.now()
    current_time = current_time.strftime("%d-%m-%Y, %H:%M:%S")
    if os.path.isfile(sys.path[0] + '\\btt-auto-transfer.log'):
        log_file = open(sys.path[0] + '\\btt-auto-transfer.log', 'a')
    else:
        log_file = open(sys.path[0] + '\\btt-auto-transfer.log', 'w')
    print(current_time + massage)
    log_file.write(current_time + massage + '\n')
    log_file.close()


#Получаем токен BTT Speed
def get_token(port):
    try:
        token_res = requests.get('http://127.0.0.1:' + str(port) + '/api/token')
        token = token_res.text
    except requests.ConnectionError:
        to_log('Не удалось получить токен BTT Speed по адресу: ' + 'http://127.0.0.1:' + str(port) + '/api/token' + ' Указан неверный порт или не запущен BTT Speed.')
        return ""
    return token

#Получаем баланс In App
def get_balance(port, token):
    balance_res = requests.get('http://127.0.0.1:' + str(port) + '/api/status?t=' + token)
    balance = json.loads(balance_res.text)
    return balance['balance']

#Получаем баланс на шлюзе
def get_tronscan_balance():
    try:
        balance_res = requests.get('https://apiasia.tronscan.io:5566/api/account?address=TA1EHWb1PymZ1qpBNfNj9uTaxd18ubrC7a')
        balance = json.loads(balance_res.text)
        sa = list(filter(lambda tokenBalances: tokenBalances['tokenId'] == '1002000', balance["tokenBalances"]))
    except requests.ConnectionError:
        to_log('Не удалось узнать балан шлюза по адресу https://apiasia.tronscan.io:5566/api/account?address=TA1EHWb1PymZ1qpBNfNj9uTaxd18ubrC7a сайт недоступен.')
        return 0
    return int(sa[0]['balance'])
    
#Переводим из In App в On Chain
#Возвращает id перевода    
def tranfer(port, token, transfer_sum):
    transfer_post = requests.post('http://127.0.0.1:' + str(port) + '/api/exchange/withdrawal?t=' + token + '&amount=' + str(transfer_sum))
    return transfer_post.text


token = get_token(speed_btt_port)
balance = get_balance(speed_btt_port, token)
tronscan_balance = get_tronscan_balance()

if (token != "") and (tronscan_balance > 0):
    if (tronscan_balance >= min_tronscan_balance) and (balance >= min_transfer_sum):
        to_log(current_time + ' Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Баланс In App: ' + str(balance / 1000000) + ' Выполняется перевод.')
        tr = tranfer(speed_btt_port, token, min_transfer_sum)
        to_log('id транзакции: ' + tr)
    else:
        to_log(current_time + ' Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Btt. Баланс In App: ' + str(balance / 1000000) + ' Btt. Недостаточно средств In App или на шлюзе.')
else:
    to_log(current_time + ' Не все необходимые данные удалось получить.')
    