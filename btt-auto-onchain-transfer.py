import requests
import json
from datetime import datetime
import os.path, sys
import time

# Указываем ваш порт speed.btt.network
speed_btt_port = 54426

# Минимальный баланс на шлюзе, с учетом знаков после запятой.
# Т.е. 1000 Btt = 1000.000000 Btt. В переменную пишем без точки. 
min_tronscan_balance = 10000000000

# Сколько переводим за раз.
# Должно быть больше 1000 Btt, т.е. минимум 1000000000
min_transfer_sum = 1000000000

# Время задержки между попытками в секундах
time_to_try = 5

# Количество строк в log файле
log_len = 1000

old_tronscan_balance = 0

# Пишем сообщения в log файл и выводим их в консоль
def to_log(massage, to_file):
    #Получаем текующие дату и время
    massage = ' ' + massage
    current_time = datetime.now()
    current_time = current_time.strftime("%d-%m-%Y, %H:%M:%S")
    if to_file:
        if os.path.isfile(sys.path[0] + '\\btt-auto-transfer.log'):
            log_file = open(sys.path[0] + '\\btt-auto-transfer.log', 'r')
            log_file_lines = log_file.readlines()
            if len(log_file_lines) >= log_len:
                cut_len = len(log_file_lines) - log_len
                for ln in range(cut_len + 1):
                    log_file_lines.pop(0)
                log_file = open(sys.path[0] + '\\btt-auto-transfer.log', 'w')
                for ln in range(len(log_file_lines)):
                    log_file.write(str(log_file_lines[ln]))
            else:
                log_file = open(sys.path[0] + '\\btt-auto-transfer.log', 'a')
        else:
            log_file = open(sys.path[0] + '\\btt-auto-transfer.log', 'w')
    print(current_time + massage)
    if to_file:
        log_file.write(current_time + massage + '\n')
        log_file.close()


# Получаем токен BTT Speed
def get_token(port):
    try:
        token_res = requests.get('http://127.0.0.1:' + str(port) + '/api/token')
        token = token_res.text
    except requests.ConnectionError:
         to_log('Не удалось получить токен BTT Speed по адресу: ' + 'http://127.0.0.1:' + str(port) + '/api/token' + ' Указан неверный порт или не запущен BTT Speed.', True)
         return ''
    return token

# Получаем баланс In App
def get_balance(port, token):
    if token == '':
        return 0
    balance_res = requests.get('http://127.0.0.1:' + str(port) + '/api/status?t=' + token)
    balance = json.loads(balance_res.text)
    return balance['balance']

# Получаем баланс на шлюзе
def get_tronscan_balance():
    try:
        balance_res = requests.get('https://apiasia.tronscan.io:5566/api/account?address=TA1EHWb1PymZ1qpBNfNj9uTaxd18ubrC7a')
        balance = json.loads(balance_res.text)
        sa = list(filter(lambda tokenBalances: tokenBalances['tokenId'] == '1002000', balance["tokenBalances"]))
    except requests.ConnectionError:
        to_log('Не удалось узнать баланc шлюза по адресу https://apiasia.tronscan.io:5566/api/account?address=TA1EHWb1PymZ1qpBNfNj9uTaxd18ubrC7a сайт недоступен.', True)
        return 0
    return int(sa[0]['balance'])
    
# Переводим из In App в On Chain
# Возвращает id перевода    
def tranfer(port, token, transfer_sum):
    transfer_post = requests.post('http://127.0.0.1:' + str(port) + '/api/exchange/withdrawal?t=' + token + '&amount=' + str(transfer_sum))
    return transfer_post.text

# Проверка параметра одноразового запуска -onerun
onerun = False
if len(sys.argv) > 2:
	sys.exit("Script has only one argument: -onerun, exit.")
elif len(sys.argv) == 2:
	if sys.argv[1] == "-onerun":
		to_log("------ One-run mode on. ------", False)
		onerun = True
	else:
		sys.exit("Script has only one argument: -onerun, exit.")

def try_tranfer(onerun):
    global old_tronscan_balance
    token = get_token(speed_btt_port)
    balance = get_balance(speed_btt_port, token)
    tronscan_balance = get_tronscan_balance()

    if (token != "") and (tronscan_balance > 0):
        if (tronscan_balance >= min_tronscan_balance) and (balance >= min_transfer_sum):
            to_log('Выполняется перевод. Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Баланс In App: ' + str(balance / 1000000), True)
            tr = tranfer(speed_btt_port, token, min_transfer_sum)
            to_log('id транзакции: ' + tr, True)
        else:
            if (old_tronscan_balance // 1000000) == (balance // 1000000):
                to_log('Недостаточно средств In App или на шлюзе. Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Btt. Баланс In App: ' + str(balance / 1000000) + ' Btt.', False)
            else:
                to_log('Недостаточно средств In App или на шлюзе. Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Btt. Баланс In App: ' + str(balance / 1000000) + ' Btt.', True)
            old_tronscan_balance = balance
    else:
        to_log('Не все необходимые данные удалось получить.', False)
    if not onerun:
        time.sleep(time_to_try)
        try_tranfer(onerun)


try_tranfer(onerun)
    