import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

"""
Transactions screen 
shows display for adding new transactions and view all transactions.
"""

class TransactionsView(ctk.CTkFrame):
    

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.amount_var = ctk.StringVar()
        self.category_var = ctk.StringVar()
        self.description_var = ctk.StringVar()
        self.date_var = ctk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.type_var = ctk.StringVar(value="expense")

        self.buildUI()

    def buildUI(self):
        # add transaction form
        ctk.CTkLabel(self, text="Add Transaction",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))

        formFrame = ctk.CTkFrame(self)
        formFrame.pack(fill="x", padx=20, pady=10)

        # type toggle
        ctk.CTkLabel(formFrame, text="Type").pack(anchor="w", padx=10, pady=(10, 0))
        typeFrame = ctk.CTkFrame(formFrame, fg_color="transparent")
        typeFrame.pack(fill="x", padx=10, pady=5)
        ctk.CTkRadioButton(typeFrame, text="Expense", variable=self.type_var, value="expense").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(typeFrame, text="Refund", variable=self.type_var, value="refund").pack(side="left")

        ctk.CTkLabel(formFrame, text="Amount (£)").pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkEntry(formFrame, textvariable=self.amount_var, placeholder_text="e.g. 12.50").pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(formFrame, text="Category").pack(anchor="w", padx=10, pady=(10, 0))
        self.categoryDropdown = ctk.CTkComboBox(formFrame, variable=self.category_var, values=[])
        self.categoryDropdown.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(formFrame, text="Description").pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkEntry(formFrame, textvariable=self.description_var).pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(formFrame, text="Date (DD/MM/YYYY)").pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkEntry(formFrame, textvariable=self.date_var).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(formFrame, text="Add Transaction",
                      command=self.onAddTransaction).pack(fill="x", padx=10, pady=15)

        # all transactions list
        ctk.CTkLabel(self, text="All Transactions",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=20)

        self.transactionsFrame = ctk.CTkScrollableFrame(self)
        self.transactionsFrame.pack(fill="both", expand=True, padx=20, pady=10)

    def onAddTransaction(self):
        """Collect form data and pass to controller."""
        data = {
            "amount": self.amount_var.get().strip(),
            "category_name": self.category_var.get().strip(),
            "description": self.description_var.get().strip(),
            "date": self.date_var.get().strip(),
            "type": self.type_var.get(),
        }
        self.controller.addTransaction(data)

    def clearForm(self):
        self.amount_var.set("")
        self.description_var.set("")
        self.date_var.set(datetime.now().strftime("%d/%m/%Y"))
        self.type_var.set("expense")

    def updateCategoryDropdown(self, categoryNames):
        if not categoryNames:
            categoryNames = ["No categories available"]
        self.categoryDropdown.configure(values=categoryNames)
        if self.category_var.get() == "":
            self.category_var.set(categoryNames[0])

    def displayAllTransactions(self, transactions):
        for widget in self.transactionsFrame.winfo_children():
            widget.destroy()

        if not transactions:
            ctk.CTkLabel(self.transactionsFrame, text="No transactions recorded.",
                         text_color="#aaaaaa").pack(pady=20)
            return

        for t in transactions:
            row = ctk.CTkFrame(self.transactionsFrame)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=t["date"], width=85,
                         font=ctk.CTkFont(size=12), text_color="#888888").pack(side="left", padx=(12, 5), pady=8)

            ctk.CTkLabel(row, text=t["category_name"],
                         font=ctk.CTkFont(size=11), text_color="#aaaaaa").pack(side="left", padx=(0, 10), pady=8)

            ctk.CTkLabel(row, text=t["description"],
                         font=ctk.CTkFont(size=12)).pack(side="left", padx=5, pady=8)

            amount_color = "#4CAF50" if t["amount"] > 0 else "#e05555"
            ctk.CTkLabel(row, text=f"£{t['amount']:.2f}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=amount_color).pack(side="right", padx=12, pady=8)

    def showSuccess(self, message):
        messagebox.showinfo("Success", message)

    def showError(self, message):
        messagebox.showerror("Error", message)