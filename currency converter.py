import tkinter as tk
from tkinter import ttk, messagebox
import requests


class CurrencyConverter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Currency Converter")
        self.geometry("480x320")
        self.minsize(400, 300)
        self.configure(bg="#34495e")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TLabel', background='#34495e', foreground='white', font=('Segoe UI', 12))
        style.configure('TEntry', font=('Segoe UI', 12))
        style.configure('TButton',
                        background='#2980b9',
                        foreground='white',
                        font=('Segoe UI', 12, 'bold'),
                        padding=8)
        style.map('TButton',
                  foreground=[('active', 'white')],
                  background=[('active', '#3498db')])

        self.currencies = []
        self.rates = {}

        self.create_widgets()
        self.fetch_currencies()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20 15 20 15")
        main_frame.grid(row=0, column=0, sticky="NSEW")

        main_frame.columnconfigure((0, 1), weight=1, uniform="col")
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=0)
        main_frame.rowconfigure(3, weight=1)

        title_label = ttk.Label(main_frame, text="Currency Converter", font=('Segoe UI', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        from_label = ttk.Label(main_frame, text="From Currency:")
        from_label.grid(row=1, column=0, sticky="w", padx=5, pady=(0, 5))

        self.from_currency = ttk.Combobox(main_frame, state="normal")  # Editable dropdown
        self.from_currency.grid(row=2, column=0, sticky="EW", padx=5, pady=(0, 15))
        self.from_currency.bind("<KeyRelease>", self.on_key_release)

        to_label = ttk.Label(main_frame, text="To Currency:")
        to_label.grid(row=1, column=1, sticky="w", padx=5, pady=(0, 5))

        self.to_currency = ttk.Combobox(main_frame, state="normal")  # Editable dropdown
        self.to_currency.grid(row=2, column=1, sticky="EW", padx=5, pady=(0, 15))
        self.to_currency.bind("<KeyRelease>", self.on_key_release)

        amount_label = ttk.Label(main_frame, text="Amount to Convert:")
        amount_label.grid(row=3, column=0, sticky="w", padx=5, pady=(0, 5))

        self.amount_entry = ttk.Entry(main_frame)
        self.amount_entry.grid(row=4, column=0, sticky="EW", padx=5, pady=(0, 15), columnspan=2)

        self.convert_btn = ttk.Button(main_frame, text="Convert", command=self.convert_currency)
        self.convert_btn.grid(row=5, column=0, columnspan=2, sticky="EW", padx=5, pady=(0, 15))

        self.result_label = ttk.Label(main_frame, text="", font=('Segoe UI', 14, 'bold'), foreground='#2ecc71')
        self.result_label.grid(row=6, column=0, columnspan=2, pady=(0, 5))

    def on_key_release(self, event):
        """Selects the first item in the dropdown that starts with the typed letter."""
        combobox = event.widget
        typed_char = event.char.upper()
        for item in combobox['values']:
            if item.startswith(typed_char):
                combobox.set(item)
                break

    def fetch_currencies(self):
        self.convert_btn.config(state="disabled")
        self.result_label.config(text="Loading currencies...")
        self.update_idletasks()
        try:
            url = "https://open.er-api.com/v6/latest/USD"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if data['result'] == 'success':
                self.rates = data['rates']
                self.currencies = sorted(self.rates.keys())

                self.from_currency['values'] = self.currencies
                self.to_currency['values'] = self.currencies

                self.from_currency.set("USD")
                self.to_currency.set("EUR")

                self.result_label.config(text="Select currencies & enter amount")
            else:
                messagebox.showerror("API Error", "Failed to load currencies.")
                self.result_label.config(text="Error loading currencies")
        except requests.exceptions.RequestException:
            messagebox.showerror("Network Error", "Cannot connect to the exchange rate service.")
            self.result_label.config(text="Network error")
        finally:
            self.convert_btn.config(state="normal")

    def convert_currency(self):
        from_cur = self.from_currency.get().strip()
        to_cur = self.to_currency.get().strip()
        amount_str = self.amount_entry.get().strip()

        if not from_cur or not to_cur:
            messagebox.showwarning("Input Error", "Please select both currencies.")
            return

        try:
            amount = float(amount_str)
            if amount < 0:
                messagebox.showwarning("Input Error", "Amount must be positive.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid numeric amount.")
            return

        try:
            if from_cur == "USD":
                usd_amount = amount
            else:
                from_rate = self.rates.get(from_cur)
                if from_rate is None:
                    messagebox.showwarning("Input Error", f"Currency '{from_cur}' not recognized.")
                    return
                usd_amount = amount / from_rate

            to_rate = self.rates.get(to_cur)
            if to_rate is None:
                messagebox.showwarning("Input Error", f"Currency '{to_cur}' not recognized.")
                return
            converted = usd_amount * to_rate
            self.result_label.config(text=f"{amount:.2f} {from_cur} = {converted:.2f} {to_cur}")
        except KeyError:
            messagebox.showerror("Conversion Error", "Conversion rate not available for selected currencies.")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")


if __name__ == "__main__":
    app = CurrencyConverter()
    app.mainloop()
