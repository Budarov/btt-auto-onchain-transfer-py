import requests
import json
from datetime import datetime
import os.path, sys
import time
import locale


# Указываем токен вашего телеграм бота, если хотите его использовать.
# Add your telegram bot token if you want to use it.
telegram_token = ''
chat_id = 0

# Указываем ваш порт speed.btt.network
# Add your port speed.btt.network
speed_btt_port = 54000

# Минимальный баланс на шлюзе, с учетом знаков после запятой.
# Т.е. 1000 Btt = 1000.000000 Btt. В переменную пишем без точки.
# Minimum balance on the gateway, including decimal places.
# 1000 Btt = 1000.000000 Btt. Write to the variable without a period.
min_tronscan_balance = 50000000000

# Сколько переводим за раз. Должно быть больше 1000 Btt, т.е. минимум 1000000000
# How much to transfer at a time. Must be more than 1000 Btt, minimum 1000000000
min_transfer_sum = 2000000000

# Время задержки между попытками в секундах
# Delay time between attempts in seconds
time_to_try = 5

# Время задержки между попытками в секундах при наличии Btt на шлюзе больше, чем min_tronscan_balance
# The delay time between attempts in seconds in the presence of Btt on the gateway is greater than min_tronscan_balance
turbo_time_to_try = 5

# Количество строк в log файле
# Number of lines in the log file
log_len = 1000

#Узнаём locale системы
sys_lang = locale.getdefaultlocale()[0]

old_tronscan_balance = 0
old_balance = 0
old_transactions = []

# Инциализация Telegram бота
if telegram_token != '':
    import telebot
    bot = telebot.TeleBot(telegram_token)
    @bot.message_handler(commands=['start'])
    def start_command(message):
        bot.send_message(message.chat.id, "Hello! СhatID: ")
        bot.send_message(message.chat.id, str(message.chat.id))
    if chat_id == 0:
        bot.polling()

# Пишем сообщения в log файл и выводим их в консоль
def to_log(text_massage, to_file):
    #Получаем текующие дату и время
    text_massage = ' ' + text_massage
    current_time = datetime.now()
    current_time = current_time.strftime("%d-%m-%Y, %H:%M:%S")
    if to_file:
        if telegram_token != '':
            bot.send_message(chat_id, text_massage)
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
    print(current_time + text_massage)
    if to_file:
        log_file.write(current_time + text_massage + '\n')
        log_file.close()


# Получаем токен BTT Speed
get_token_err = False
def get_token(port):
    global get_token_err
    try:
        token_res = requests.get('http://127.0.0.1:' + str(port) + '/api/token')
        token = token_res.text
        get_token_err = False
    except requests.ConnectionError:
        if get_token_err == False:
            get_token_err = True
            if sys_lang == 'ru_RU':
                to_log('Не удалось получить токен BTT Speed по адресу: ' + 'http://127.0.0.1:' + str(port) + '/api/token' + ' Указан неверный порт или не запущен BTT Speed.', True)
            else:
                to_log('Failed to get BTT Speed token at address: ' + 'http://127.0.0.1:' + str(port) + '/api/token' + ' Wrong port in settings or BTT speed not running.', True)
        else:
            if sys_lang == 'ru_RU':
                to_log('Не удалось получить токен BTT Speed по адресу: ' + 'http://127.0.0.1:' + str(port) + '/api/token' + ' Указан неверный порт или не запущен BTT Speed.', False)
            else:
                to_log('Failed to get BTT Speed token at address: ' + 'http://127.0.0.1:' + str(port) + '/api/token' + ' Wrong port in settings or BTT speed not running.', False)
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
        if sys_lang == 'ru_RU':
            to_log('Не удалось узнать баланc шлюза по адресу https://apiasia.tronscan.io:5566/api/account?address=TA1EHWb1PymZ1qpBNfNj9uTaxd18ubrC7a сайт недоступен.', True)
        else:
            to_log('Failed get balance of gateway at address https://apiasia.tronscan.io:5566/api/account?address=TA1EHWb1PymZ1qpBNfNj9uTaxd18ubrC7a site unavailable.', True)
        return 0
    try:
        res = int(sa[0]['balance'])
    except IndexError:
        if sys_lang == 'ru_RU':
            to_log('Пришел не валидный json от https://apiasia.tronscan.io:5566/api/account?address=TA1EHWb1PymZ1qpBNfNj9uTaxd18ubrC7a', True)
        else:
            to_log('Not valid json from https://apiasia.tronscan.io:5566/api/account?address=TA1EHWb1PymZ1qpBNfNj9uTaxd18ubrC7a', True)
        return 0
    return res
    
# Переводим из In App в On Chain
# Возвращает id перевода    
def tranfer(port, token, transfer_sum):
    transfer_post = requests.post('http://127.0.0.1:' + str(port) + '/api/exchange/withdrawal?t=' + token + '&amount=' + str(transfer_sum))
    return transfer_post.text

# Проверка параметра одноразового запуска -onerun
onerun = False
if len(sys.argv) > 2:
    if sys_lang == 'ru_RU':
        sys.exit("Скрипт имеет только один аргумент: -onerun, выход.")
    else:
	    sys.exit("Script has only one argument: -onerun, exit.")
elif len(sys.argv) == 2:
    if sys.argv[1] == "-onerun":
        if sys_lang == 'ru_RU':
            to_log("------ Скрипт выполнится один раз. ------", False)
        else:
            to_log("------ One-run mode on. ------", False)
        onerun = True
    else:
        if sys_lang == 'ru_RU':
            sys.exit("Скрипт имеет только один аргумент: -onerun, выход.")
        else:
	        sys.exit("Script has only one argument: -onerun, exit.")

# Получение списка транзакций
def get_transactions(port, token):
    if token == '':
        return 0
    transactions_res = requests.get('http://127.0.0.1:' + str(port) + '/api/exchange/transactions?t=' + token + '&count=50')
    transactions = json.loads(transactions_res.text)
    return transactions

# Проверка статуса транзакций
def check_transactions(old_transactions, transactions): 
    for tr in transactions:
        if (tr['id'] in old_transactions) and (tr['status'] == 'Complete'):
            if tr['message'] == 'SUCCESS':
                if sys_lang == 'ru_RU':
                    to_log('Транзацкия ' + str(tr['id']) + ' выполненна успешно! Сумма перевода: ' + str(tr['amount'] / 1000000) + ' BTT.', True)
                else:
                    to_log('Transaction ' + str(tr['id']) + ' completed successfully! Transfer amount: ' + str(tr['amount'] / 1000000) + ' BTT.', True)
                old_transactions.remove(tr['id'])
            else:
                if sys_lang == 'ru_RU':
                    to_log('Транзацкия ' + str(tr['id']) + ' НЕ выполненна. Причина: ' + tr['message'], True)
                else:
                    to_log('Transaction ' + str(tr['id']) + ' NOT completed. Reason: ' + tr['message'], True)
                old_transactions.remove(tr['id'])
    return old_transactions

def try_tranfer(onerun, sleep_time):
    while True:
        global old_tronscan_balance, old_balance, old_transactions
        
        token = get_token(speed_btt_port)
        balance = get_balance(speed_btt_port, token)
        tronscan_balance = get_tronscan_balance()

        if (old_balance == 0) and (get_token_err == False):
            if sys_lang == 'ru_RU':
                to_log('Скрипт запущен. Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Btt. Баланс In App: ' + str(balance / 1000000) + ' Btt. Вопросы по скрипту можно задать тут: https://t.me/joinchat/hQkZhUnN60dhZjZi', True)
            else:
                to_log('Script launched. Gateway balance: ' + str(tronscan_balance / 1000000) + ' Btt. Balance In App: ' + str(balance / 1000000) + ' Btt. Questions about the script can be asked here: https://t.me/joinchat/hQkZhUnN60dhZjZi', True)

        if (token != "") and (tronscan_balance > 0):
            if (tronscan_balance >= min_tronscan_balance) and (balance >= min_transfer_sum):
                if sys_lang == 'ru_RU':
                    to_log('Выполняется перевод. Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Btt. Баланс In App: ' + str(balance / 1000000) + ' Btt.', True)
                else:
                    to_log('Transfer in progress. Gateway balance: ' + str(tronscan_balance / 1000000) + ' Btt. Balance In App: ' + str(balance / 1000000) + ' Btt.', True)
                tr = tranfer(speed_btt_port, token, min_transfer_sum)
                old_tronscan_balance.append(int(tr))
                if sys_lang == 'ru_RU':
                    to_log('id транзакции: ' + tr, True)
                else:
                    to_log('transaction id: ' + tr, True)
                sleep_time = turbo_time_to_try
            else:
                #if (old_tronscan_balance // 1000000) == (tronscan_balance // 1000000) or (balance < min_transfer_sum):
                if old_balance > balance:
                    if sys_lang == 'ru_RU':
                        to_log('Недостаточно средств In App или на шлюзе. Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Btt. Баланс In App: ' + str(balance / 1000000) + ' Btt.', True)
                    else:
                        to_log('Not enough In App or Gateway funds. Gateway balance: ' + str(tronscan_balance / 1000000) + ' Btt. Balance In App: ' + str(balance / 1000000) + ' Btt.', True)
                else:
                    if sys_lang == 'ru_RU':
                        to_log('Недостаточно средств In App или на шлюзе. Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Btt. Баланс In App: ' + str(balance / 1000000) + ' Btt.', False)
                    else:
                        to_log('Not enough In App or Gateway funds. Gateway balance: ' + str(tronscan_balance / 1000000) + ' Btt. Balance In App: ' + str(balance / 1000000) + ' Btt.', False)
                old_tronscan_balance = tronscan_balance
                old_balance = balance
                sleep_time = time_to_try
            if len(old_transactions) > 0:
                old_transactions = check_transactions(old_transactions, get_transactions(speed_btt_port, token))
        else:
            to_log('Не все необходимые данные удалось получить.', False)       
        if onerun:
            sys.exit()    
        time.sleep(sleep_time)
        
try_tranfer(onerun, time_to_try)
