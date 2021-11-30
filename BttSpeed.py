import sys, os
import locale
from datetime import datetime
import json
try:
    import requests
except ModuleNotFoundError:
    import pip
    pip.main(['install', "requests"]) 
    import requests
try:
    import telebot
except ModuleNotFoundError:
    import pip
    pip.main(['install', "pyTelegramBotAPI"])
    import telebot

class BttSpeed:
    def __init__(self, port=54000, host_name='', log_len = 1000) -> None:
        # Имя хоста для логов
        self.host_name = host_name

        # Порт Btt Speed
        if type(port) == int:
            self.port = port
        else: 
            sys.exit("No valid BTT port: " + str(port))
        
        #BTT Speed Token
        self.token = ''

        self.gateway_balance = 0
        self.balance = 0
        
        # ['tg_token, chat_id, is on']
        self.telegram_info = ['', 0, False]
                
        # Узнаём locale системы
        self.sys_lang = locale.getdefaultlocale()[0]

        self.tg_bot = 0
        self.log_len = log_len

#--------------------- Getters ---------------------
    # Выдача системной локали
    def get_sys_lang(self):
        return self.sys_lang
    
    def get_balance(self):
        return self.balance

    def get_gateway_balance(self):
        return self.gateway_balance


# --------------------- Setters ---------------------
    
    # Задаем имя хоста для логов
    def set_host_name(self, host_name):
        self.host_name = str(host_name)

    # Задаём порт Btt Speed
    def set_port(self, port):
        if type(port) == int:
            self.port = port
        else: 
            sys.exit("No valid BTT port: " + str(port))

    # Задаём данные для telegram бота
    def set_telegram_info(self, tg_info):
        self.telegram_info[0] = str(tg_info[0])
        self.telegram_info[1] = int(tg_info[1])
        self.telegram_info[2] = tg_info[2]

    # Задаём длинну Log Файла.
    def set_log_len(self, log_ln):
        self.log_len = log_ln

# --------------------- Получение токена Btt Speed ---------------------

    def update_token(self, get_token_err = False):
        try:
            token_res = requests.get('http://127.0.0.1:' + str(self.port) + '/api/token')
            self.token = token_res.text
            get_token_err = False
        except requests.ConnectionError:
            if get_token_err == False:
                get_token_err = True
                if self.sys_lang == 'ru_RU':
                    self.to_log('Не удалось получить токен BTT Speed по адресу: ' + 'http://127.0.0.1:' + str(self.port) + '/api/token' + ' Указан неверный порт или не запущен BTT Speed.', True)
                else:
                    self.to_log('Failed to get BTT Speed token at address: ' + 'http://127.0.0.1:' + str(self.port) + '/api/token' + ' Wrong port in settings or BTT speed not running.', True)
            else:
                if self.sys_lang == 'ru_RU':
                    self.to_log('Не удалось получить токен BTT Speed по адресу: ' + 'http://127.0.0.1:' + str(self.port) + '/api/token' + ' Указан неверный порт или не запущен BTT Speed.', False)
                else:
                    self.to_log('Failed to get BTT Speed token at address: ' + 'http://127.0.0.1:' + str(self.port) + '/api/token' + ' Wrong port in settings or BTT speed not running.', False)
            return get_token_err
        return get_token_err

# --------------------- Получение балансов ---------------------
    # Получаем баланс In App
    def update_balance(self):
        if self.token == '':
            return 0
        balance_res = requests.get('http://127.0.0.1:' + str(self.port) + '/api/status?t=' + self.token)
        balance = json.loads(balance_res.text)
        self.balance = balance['balance']
        return self.balance

    # Получаем баланс на шлюзе
    def update_gateway_balance(self):
        try:
            balance_res = requests.get('https://apiasia.tronscan.io:5566/api/account?address=TTZu7wpHa9tnQjFUDrsjgPfXE7fck7yYs5')
            balance = json.loads(balance_res.text)
            sa = list(filter(lambda tokenBalances: tokenBalances['tokenId'] == '1002000', balance["tokenBalances"]))
        except requests.ConnectionError:
            if self.sys_lang == 'ru_RU':
                self.to_log('Не удалось узнать баланc шлюза по адресу https://apiasia.tronscan.io:5566/api/account?address=TTZu7wpHa9tnQjFUDrsjgPfXE7fck7yYs5 сайт недоступен.', True)
            else:
                self.to_log('Failed get balance of gateway at address https://apiasia.tronscan.io:5566/api/account?address=TTZu7wpHa9tnQjFUDrsjgPfXE7fck7yYs5 site unavailable.', True)
            self.gateway_balance = 0
            return self.gateway_balance
        try:
            self.gateway_balance = int(sa[0]['balance'])
        except IndexError:
            if self.sys_lang == 'ru_RU':
                self.to_log('Пришел не валидный json от https://apiasia.tronscan.io:5566/api/account?address=TTZu7wpHa9tnQjFUDrsjgPfXE7fck7yYs5', True)
            else:
                self.to_log('Not valid json from https://apiasia.tronscan.io:5566/api/account?address=TTZu7wpHa9tnQjFUDrsjgPfXE7fck7yYs5', True)
            self.gateway_balance = 0
            return self.gateway_balance
        return self.gateway_balance

# --------------------- Переводим из In App в On Chain ---------------------
    # Возвращает id перевода    
    def tranfer(self, transfer_sum):
        transfer_post = requests.post('http://127.0.0.1:' + str(self.port) + '/api/exchange/withdrawal?t=' + self.token + '&amount=' + str(transfer_sum))
        tr_text = transfer_post.text
        self.add_old_transactions(int(tr_text))
        if self.sys_lang == 'ru_RU':
            self.to_log('Выполнен перевод на сумму: ' + str(transfer_sum / 1000000) + ' Btt. id транзакции: '+ tr_text + ' Баланс шлюза: ' + str(self.gateway_balance / 1000000) + ' Btt. Баланс In App: ' + str(self.balance / 1000000) + ' Btt.', True)
        else:
            self.to_log('A transfer in the amount of: ' + str(transfer_sum / 1000000) + ' Btt. Transaction id: '+ tr_text + ' Gateway balance: ' + str(self.gateway_balance / 1000000) + ' Btt. Balance In App: ' + str(self.balance / 1000000) + ' Btt.', True)
        return tr_text

# --------------------- Отслеживание статуса транзакций ---------------------
    # Получение списка транзакций
    def update_transactions(self):
        if self.token == '':
            return 0
        transactions_res = requests.get('http://127.0.0.1:' + str(self.port) + '/api/exchange/transactions?t=' + self.token + '&count=50')
        transactions = json.loads(transactions_res.text)
        return transactions

    # Читаем транзакции из файла, если они есть.
    def get_old_transactions(self):
        if os.path.isfile(sys.path[0] + '\\btt-auto-transactions-id.dat'):
            tr_file = open(sys.path[0] + '\\btt-auto-transactions-id.dat', 'r')
            tr_file_lines = tr_file.readlines() 
            try:          
                res = json.loads(tr_file_lines[0])
            except IndexError:
                res = []
            tr_file.close()
            return res
        else:
            return []
    
    # Пишем выполненную транзакцию в файл
    def add_old_transactions(self, tr):
        old_tr = self.get_old_transactions()
        old_tr.append(tr)
        tr_file = open(sys.path[0] + '\\btt-auto-transactions-id.dat', 'w')
        tr_file.write(json.dumps(old_tr))
        tr_file.close()
        return old_tr

    # Удаляем выполненную транзакцию из файла
    def del_old_transactions(self, tr):
        old_tr = self.get_old_transactions()
        try:
            old_tr.remove(tr)
        except ValueError:
            print ('id Транзакции в файле не найдена.')
        tr_file = open(sys.path[0] + '\\btt-auto-transactions-id.dat', 'w')
        tr_file.write(json.dumps(old_tr))
        tr_file.close()
        return old_tr

    # Проверка статуса транзакций
    def check_transactions(self, old_transactions): 
        transactions = self.update_transactions()
        for tr in transactions:
            if (tr['id'] in old_transactions) and (tr['status'] == 'Complete'):
                if tr['message'] == 'SUCCESS':
                    if self.sys_lang == 'ru_RU':
                        self.to_log('Транзацкия ' + str(tr['id']) + ' выполненна успешно! Сумма перевода: ' + str(tr['amount'] / 1000000) + ' BTT.', True)
                    else:
                        self.to_log('Transaction ' + str(tr['id']) + ' completed successfully! Transfer amount: ' + str(tr['amount'] / 1000000) + ' BTT.', True)
                    old_transactions = self.del_old_transactions(tr['id'])
                else:
                    if self.sys_lang == 'ru_RU':
                        self.to_log('Транзацкия ' + str(tr['id']) + ' НЕ выполненна. Причина: ' + tr['message'], True)
                    else:
                        self.to_log('Transaction ' + str(tr['id']) + ' NOT completed. Reason: ' + tr['message'], True)
                    old_transactions = self.del_old_transactions(tr['id'])
        return old_transactions

# --------------------- Логирование, вывод в консоль, отправка сообщений в Telegram ---------------------
    # Включаем telegram бота
    def telegram_on(self, tg_token, chat_id):
        self.tg_bot = telebot.TeleBot(tg_token)
        self.telegram_info[1] = chat_id
        self.telegram_info[2] = True

    # Пишем сообщения в log файл и выводим их в консоль
    def to_log(self, text_massage, to_file, tg = True):
        # Получаем текующие дату и время
        current_time = datetime.now()
        current_time = current_time.strftime("%d-%m-%Y, %H:%M:%S")
        text_massage = current_time + '  ' + self.host_name + ' ' + text_massage
        if to_file:
            if tg and self.telegram_info[2]:
                try:
                    self.tg_bot.send_message(self.telegram_info[1], text_massage)
                except telebot.apihelper.ApiTelegramException:
                    self.telegram_info[2] = False
                    if self.sys_lang == 'ru_RU':
                        self.to_log('Указан не верный telegram Chat id или токен.', True, False )
                    else:
                        self.to_log('Incorrect telegram Chat id or Token.', True, False)
                except requests.exceptions.ConnectionError:
                    if self.sys_lang == 'ru_RU':
                        self.to_log('Api Telegtam не доступно.', True, False)
                    else:
                        self.to_log('Api Telegtam not available.', True, False)
            if os.path.isfile(sys.path[0] + '\\btt-auto-transfer.log'):
                log_file = open(sys.path[0] + '\\btt-auto-transfer.log', encoding='utf-8', mode='r')
                log_file_lines = log_file.readlines()
                if len(log_file_lines) >= self.log_len:
                    cut_len = len(log_file_lines) - self.log_len
                    for ln in range(cut_len + 1):
                        log_file_lines.pop(0)
                    log_file = open(sys.path[0] + '\\btt-auto-transfer.log', encoding='utf-8', mode='w')
                    for ln in range(len(log_file_lines)):
                        log_file.write(str(log_file_lines[ln]))
                else:
                    log_file = open(sys.path[0] + '\\btt-auto-transfer.log', encoding='utf-8', mode='a')
            else:
                log_file = open(sys.path[0] + '\\btt-auto-transfer.log', encoding='utf-8', mode='w')
        print(text_massage)
        if to_file:
            log_file.write(text_massage + '\n')
            log_file.close()
