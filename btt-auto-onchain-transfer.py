import os, sys, time
import configparser
import BttSpeed

config = configparser.ConfigParser()
host = BttSpeed.BttSpeed()

# Если конфигфайла нет, создаю новый, с кофигурацией по умолчанию, если есть, читаю.
if os.path.isfile(sys.path[0] + '\\settings.ini'):
    config.read(sys.path[0] + '\\settings.ini')
else:
    host.to_log('Config file not found. Created settings.ini with default settings.', True)
    config['HOST'] = {'host_name': 'Node name',
                    'log_len': '1000',
                    'sys_lang': ''}
    config['BTT_SPEED'] = {'speed_btt_port': '54000',
                        'min_gateway_balance': '50000000000',
                        'min_transfer_sum': '2000000000',
                        'time_to_try': '5',
                        'turbo_time_to_try': '5'}
    config['TELEGRAM'] = {'telegram': 'off',
                        'api_access_token': '',
                        'chat_id': '0'}
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)
        configfile.close()
    sys.exit('Need to edit config file.')

# Запоминаю значения конфига
host.set_port(int(config['BTT_SPEED']['speed_btt_port']))
host.set_host_name(config['HOST']['host_name'])
host.set_log_len(int(config['HOST']['log_len']))

min_gateway_balance = int(config['BTT_SPEED']['min_gateway_balance'])
min_transfer_sum = int(config['BTT_SPEED']['min_transfer_sum'])
time_to_try = int(config['BTT_SPEED']['time_to_try'])
turbo_time_to_try = int(config['BTT_SPEED']['turbo_time_to_try'])
sys_lang = host.get_sys_lang()

if config['TELEGRAM'].getboolean('telegram'):
    host.to_log('Telegram ON', False)
    host.telegram_on(config['TELEGRAM']['api_access_token'], int(config['TELEGRAM']['chat_id']))
else:
    host.to_log('Telegram OFF', False)

old_tronscan_balance = 0
old_balance = 0

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
            host.to_log("------ Скрипт выполнится один раз. ------", False)
        else:
            host.to_log("------ One-run mode on. ------", False)
        onerun = True
    else:
        if sys_lang == 'ru_RU':
            sys.exit("Скрипт имеет только один аргумент: -onerun, выход.")
        else:
	        sys.exit("Script has only one argument: -onerun, exit.")


old_transactions = host.get_old_transactions()

# Проверка балансов и попытка вывода
def try_tranfer(onerun, sleep_time):
    while True:
        global old_balance, old_transactions
        
        # Обновляем данные
        get_token_err = host.update_token()
        balance = host.update_balance()
        tronscan_balance = host.update_gateway_balance()

        # Проверка на запуск (первое прохождение цикла)
        if (old_balance == 0) and (get_token_err == False):
            if sys_lang == 'ru_RU':
                host.to_log('Скрипт запущен. Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Btt. Баланс In App: ' + str(balance / 1000000) + ' Btt. Вопросы по скрипту можно задать тут: https://t.me/joinchat/hQkZhUnN60dhZjZi', True)
            else:
                host.to_log('Script launched. Gateway balance: ' + str(tronscan_balance / 1000000) + ' Btt. Balance In App: ' + str(balance / 1000000) + ' Btt. Questions about the script can be asked here: https://t.me/joinchat/hQkZhUnN60dhZjZi', True)

        if (get_token_err == False) and (tronscan_balance > 0):
            if (tronscan_balance >= min_gateway_balance) and (balance >= min_transfer_sum):
                tr = host.tranfer(min_transfer_sum)
                old_transactions = host.add_old_transactions(int(tr))
                sleep_time = turbo_time_to_try
            else:
                if old_balance > balance:
                    if sys_lang == 'ru_RU':
                        host.to_log('Недостаточно средств In App или на шлюзе. Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Btt. Баланс In App: ' + str(balance / 1000000) + ' Btt.', True)
                    else:
                        host.to_log('Not enough In App or Gateway funds. Gateway balance: ' + str(tronscan_balance / 1000000) + ' Btt. Balance In App: ' + str(balance / 1000000) + ' Btt.', True)
                else:
                    if sys_lang == 'ru_RU':
                        host.to_log('Недостаточно средств In App или на шлюзе. Баланс шлюза: ' + str(tronscan_balance / 1000000) + ' Btt. Баланс In App: ' + str(balance / 1000000) + ' Btt.', False)
                    else:
                        host.to_log('Not enough In App or Gateway funds. Gateway balance: ' + str(tronscan_balance / 1000000) + ' Btt. Balance In App: ' + str(balance / 1000000) + ' Btt.', False)
                old_balance = balance
                sleep_time = time_to_try
        else:
            host.to_log('Не все необходимые данные удалось получить.', False)  
        if len(old_transactions) > 0:
                old_transactions = host.check_transactions(old_transactions)     
        if onerun:
            sys.exit()    
        time.sleep(sleep_time)
try:
    try_tranfer(onerun, time_to_try)
except KeyboardInterrupt:
    sys.exit('CTRL+C Stop Script!')
