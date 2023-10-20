import requests
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from bit import Key
from bitcoinlib.wallets import Wallet

class SquareApp(App):
    def build(self):
        layout = GridLayout(cols=16, spacing=1)

        self.buttons = []  # Список для хранения кнопок и чисел
        current_value = 1  # Начальное значение

        for i in range(1, 257):
            button = Button(text="", background_color=(1, 1, 1))
            button.bind(on_press=self.on_button_press)  # Привязываем обработчик событий к кнопке
            layout.add_widget(button)
            self.buttons.append((button, current_value, False))  # Добавляем кнопку, число и флаг активации
            current_value *= 2  # Увеличиваем значение в два раза

        self.output_text_input = TextInput(
            text="Хеш\nСжатый Биткоин-адрес: \nБаланс: \nКоличество транзакций: \nВсего получено: BTC",
            readonly=True,
            multiline=True
        )

        root_layout = GridLayout(cols=1)
        root_layout.add_widget(layout)
        root_layout.add_widget(self.output_text_input)

        self.total_sum = 0  # Инициализируем общую сумму чисел

        return root_layout

    def on_button_press(self, instance):
        for button, number, is_active in self.buttons:
            if button == instance:
                if is_active:
                    # Если кнопка уже активирована, возвращаем цвет и вычитаем число из общей суммы
                    button.background_color = (1, 1, 1)  # Возвращает цвет кнопки (белый)
                    self.total_sum -= number  # Вычитаем число из общей суммы
                    self.buttons[self.buttons.index((button, number, is_active))] = (
                        button, number, False)  # Обновляем флаг активации
                else:
                    # Если кнопка не активирована, меняем цвет на желтый и добавляем число к общей сумме
                    button.background_color = (128, 0, 128, 1)  # Меняет цвет кнопки (желтый)
                    self.total_sum += number  # Добавляем число к общей сумме
                    self.buttons[self.buttons.index((button, number, is_active))] = (
                        button, number, True)  # Обновляем флаг активации
        # Проверяем, есть ли активные кнопки
        if any(is_active for _, _, is_active in self.buttons):
            hex_sum = hex(self.total_sum).replace("0x", "")
            bitcoin_address = self.calculate_bitcoin_address(hex_sum)  # Вычисляем биткоин-адрес
            balance, n_tx, total_received_satoshi = self.get_balance_and_transactions(
                bitcoin_address)  # Получаем баланс, количество транзакций и total_received в сатоши
            # Преобразуем total_received в биткоины
            total_received_btc = total_received_satoshi / 100000000.0
            if n_tx > 0:
                text_color = (0, 0.5, 0, 1)  # Зеленый цвет текста (RGBA)
            else:
                text_color = (0, 0, 0)  # Черный цвет текста (RGBA)
            self.output_text_input.foreground_color = text_color  # Устанавливаем цвет текста
            # Формируем текст для вывода
            output_text = f"Хеш: {hex_sum}\nСжатый Биткоин-адрес: {bitcoin_address}\nБаланс: {balance} сатоши\nКоличество транзакций: {n_tx}\nВсего получено: {total_received_btc} BTC"
            # Устанавливаем текст в TextInput
            self.output_text_input.text = output_text

    def calculate_bitcoin_address(self, hex_sum):
        # Удаляем префикс "0x", если он есть
        hex_sum = hex_sum.replace("0x", "")
        private_key = Key.from_hex(hex_sum)
        bitcoin_address = private_key.address
        return bitcoin_address

    def get_balance_and_transactions(self, bitcoin_address):
        url = f"https://blockchain.info/balance?active={bitcoin_address}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            balance = data[bitcoin_address]["final_balance"]
            n_tx = data[bitcoin_address]["n_tx"]
            total_received = data[bitcoin_address]["total_received"]
            return balance, n_tx, total_received
        else:
            return None, None, None

if __name__ == '__main__':
    SquareApp().run()



