# Auto BTT transfer to on-chain
<a name="info">Как использовать скрипт</a>  [On english](#info_en)
-------------------------
На сегодняшний день, на шлюзе, откуда происходят переводы в on-chain кошелек, BTT в наличии очень редко.
Для увеличения шанса удачного вывода BTT в on-chain необходимо постоянно мониторить наличие BTT на шлюзе.
Данный скрипт проверяет баланс на шлюзе и In app кошельке. Как только баланс на шлюзе будет больше указанного `min_tronscan_balance` и баланс в In app кошельке больше `min_transfer_sum` будет произведена попытка вывода в On-chain кошелек суммы равной `min_transfer_sum`

------

 Инструкция по использованию:

1. Качаем и устанавливаем Phyton: [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. Качаете [этот репозиторий](https://github.com/Budarov/btt-auto-onchain-transfer-py) (Если нет гита то нажимаете сверху кнопку Code и выбираете Download zip, затем извлекаете и переходите в папку).

3. Копируем порт из адресной строки веб интерфейса Speed BTT. Например, если веб интерфейс доступен по адресу `https://speed.btt.network/gui/index.html?port=54000#/dashboard` , то ваш порт **54000**.

4. Открываете файл скрипта _**btt-auto-onchain-transfer.py**_ в любом текстовом редакторе, удобнее всего редактировать в [Notepad++](https://notepad-plus-plus.org/downloads/)

5. Указываем свой порт Speed BTT в `speed_btt_port`. Можно, но не обязательно, редактировать и другие параметры:

   `\# Указываем ваш порт speed.btt.network`

   `speed_btt_port = 54000`

   `\# Минимальный баланс на шлюзе, с учетом знаков после запятой.`

   `\# Т.е. 1000 Btt = 1000.000000 Btt. В переменную пишем без точки.` 

   `min_tronscan_balance = 10000000000`

   `\# Сколько переводим за раз.`

   `\# Должно быть больше 1000 Btt, т.е. минимум 1000000000`

   `min_transfer_sum = 1000000000`

   `\# Время задержки между попытками в секундах`

   `time_to_try = 5`

   `\# Количество строк в log файле`

   `log_len = 1000`

6. Для запуска программы используйте _**START.bat**_

Если хотите получать уведомления от скрипта в **Telegram**:

1. Устанавливаем модуль, выполняем в консоли `pip install pyTelegramBotAPI`

2. Идем в чат [@BotFather](https://t.me/botfather)

3. Пишем команду `/newbot`. Он запросит название и `@username` для будущего бота. Тут ничего сложного - он всё подсказывает (главное, чтобы `@username` был не занят и заканчивался на bot). BotFather пришлет HTTP API токен.

4. Указываем токен в кавычках в переменную `telegram_token`, например:

   `telegram_token = '1850000000:AAAAAAAAAAAAAAAAzvKwBwCFSB0Pi7ImY8'`

5. Находим пользователя [@id_ChatBot](https://telegram.me/id_chatbot), пишем ему команду `/start`. Получаем Chat ID.

6. Указываем его в переменную [chat_id]() без кавычек, например:

   `chat_id = 20000002`

7. Находим бота по его `@username`, добавляем в контакты, пишем ему `/start`.

   
   
   ------
   
   <a name="info_en">How to use the script:</a>
   -------------------------
   
   [Google translate ;)]
   
   Today, BTT on gateway wallet is very rarely available.
   To increase the chance of successful BTT withdrawal in the on-chain, it is necessary to constantly monitor the presence of BTT on the gateway.
   This script checks the balance on the gateway and In app wallet. As soon as the balance on the gateway is more than the specified `min_tronscan_balance` and the balance in the In app wallet is more than` min_transfer_sum`, an attempt will be made to withdraw the amount equal to `min_transfer_sum` to the On-chain wallet
   
   ------
   
    Instructions for use:
   
   1. Download and install Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   
   2. Download [this repository](https://github.com/Budarov/btt-auto-onchain-transfer-py) (If there is no git, then click the Code button on top and select Download zip, then extract and go to the folder).
   
   3. Copy the port from the address line of the Speed BTT web interface. For example, if the web interface is available at `https: //speed.btt.network/gui/index.html? Port = 54000 # / dashboard`, then your port is ** 54000 **.
   
   4. Open the script file _**btt-auto-onchain-transfer.py**_ in any text editor, it is most convenient to edit in [Notepad ++](https://notepad-plus-plus.org/downloads/)
   
   5. Add your Speed BTT port to `speed_btt_port`. It is possible, but not required, to edit other parameters:
   
      `\# Add your port speed.btt.network`
   
      `speed_btt_port = 54000`
   
      `\# Minimum balance on the gateway, including decimal places.`
   
      `\# 1000 Btt = 1000.000000 Btt. Write to the variable without a period.`
   
      `min_tronscan_balance = 10000000000`
   
      `\# How much to transfer at a time. Must be more than 1000 Btt, minimum 1000000000`
   
      `min_transfer_sum = 1000000000`
   
      `\# Delay time between attempts in seconds`
   
      `time_to_try = 5`
   
      `\# Number of lines in the log file`
   
      `log_len = 1000`
   
   6. Use _**START.bat**_ to run the program.
   
   If you want to receive notifications from the script in **Telegram**:
   
   1. Install the module, execute in the console `pip install pyTelegramBotAPI`
   
   2. Go to the chat [@BotFather](https://t.me/botfather)
   
   3. Write the command `/ newbot`. It will ask for a name and `@ username` for the future bot. There is nothing complicated here - it prompts everything (the main thing is that `@ username` is not busy and ends with bot). BotFather will send an HTTP API token.
   
   4. Specify the token in quotes in the `telegram_token` variable, for example:
   
      `telegram_token = '1850000000:AAAAAAAAAAAAAAAAzvKwBwCFSB0Pi7ImY8'`
   
   5. Find the user [@id_ChatBot](https://telegram.me/id_chatbot), write him the command `/ start`. We get the Chat ID.
   
   6. We specify it in the `chat_id` variable without quotes, for example:
   
      `chat_id = 20000002`
   
   7. Find your bot by `@ username`, open chat, write ` / start` to it..

