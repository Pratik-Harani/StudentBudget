"""
Dashboard screen 
Displays summary, categories, quick add, recent transactions.
"""


import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

class DashboardView(ctk.CTkFrame):
    

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
        # scrollable container for all content
        scrollFrame = ctk.CTkScrollableFrame(self)
        scrollFrame.pack(fill="both", expand=True)

        # summary cards
        summaryFrame = ctk.CTkFrame(scrollFrame, fg_color="transparent")
        summaryFrame.pack(fill="x", padx=20, pady=10)
        summaryFrame.columnconfigure((0, 1, 2), weight=1)

        # income card
        incomeCard = ctk.CTkFrame(summaryFrame)
        incomeCard.grid(row=0, column=0, padx=5, sticky="ew")
        self.incomeValue = ctk.CTkLabel(incomeCard, text="£0.00", font=ctk.CTkFont(size=24, weight="bold"))
        self.incomeValue.pack(pady=(15, 2))
        ctk.CTkLabel(incomeCard, text="Monthly Income", font=ctk.CTkFont(size=12), text_color="#aaaaaa").pack(pady=(0, 15))

        # spent card
        spentCard = ctk.CTkFrame(summaryFrame)
        spentCard.grid(row=0, column=1, padx=5, sticky="ew")
        self.spentValue = ctk.CTkLabel(spentCard, text="£0.00", font=ctk.CTkFont(size=24, weight="bold"), text_color="#e05555")
        self.spentValue.pack(pady=(15, 2))
        ctk.CTkLabel(spentCard, text="Total Spent", font=ctk.CTkFont(size=12), text_color="#aaaaaa").pack(pady=(0, 15))

        # available card
        availableCard = ctk.CTkFrame(summaryFrame)
        availableCard.grid(row=0, column=2, padx=5, sticky="ew")
        self.availableValue = ctk.CTkLabel(availableCard, text="£0.00", font=ctk.CTkFont(size=24, weight="bold"), text_color="#4CAF50")
        self.availableValue.pack(pady=(15, 2))
        ctk.CTkLabel(availableCard, text="Available to Budget", font=ctk.CTkFont(size=12), text_color="#aaaaaa").pack(pady=(0, 15))

        # categories section
        ctk.CTkLabel(scrollFrame, text="Budget Categories",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=20)
        self.categoriesFrame = ctk.CTkFrame(scrollFrame, fg_color="transparent")
        self.categoriesFrame.pack(fill="x", padx=20, pady=10)

        # quick add transaction form
        ctk.CTkLabel(scrollFrame, text="Quick Add Transaction",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=20)

        formFrame = ctk.CTkFrame(scrollFrame)
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

        ctk.CTkButton(formFrame, text="Add Expense",
                      command=self.onAddExpense).pack(fill="x", padx=10, pady=15)

        # recent transactions section
        ctk.CTkLabel(scrollFrame, text="Recent Transactions",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=20)
        self.transactionsFrame = ctk.CTkFrame(scrollFrame, fg_color="transparent")
        self.transactionsFrame.pack(fill="x", padx=20, pady=(10, 20))

    def onAddExpense(self):
        """Collect form data and pass to controller."""
        data = {
            "amount": self.amount_var.get().strip(),
            "category_name": self.category_var.get().strip(),
            "description": self.description_var.get().strip(),
            "date": self.date_var.get().strip(),
            "type": self.type_var.get(),
        }
        self.controller.addExpenseFromDashboard(data)

    def clearForm(self):
        self.amount_var.set("")
        self.description_var.set("")
        self.date_var.set(datetime.now().strftime("%d/%m/%Y"))
        self.type_var.set("expense")

    # --- methods the controller calls to update the display ---

    def updateSummary(self, monthlyIncome, totalSpent, availableToBudget):
        self.incomeValue.configure(text=f"£{monthlyIncome:.2f}")
        self.spentValue.configure(text=f"£{totalSpent:.2f}")
        self.availableValue.configure(text=f"£{availableToBudget:.2f}")

        # colour available red if negative
        if availableToBudget < 0:
            self.availableValue.configure(text_color="#e05555")
        else:
            self.availableValue.configure(text_color="#4CAF50")

    def updateCategoryDropdown(self, categoryNames):
        if not categoryNames:
            categoryNames = ["No categories available"]
        self.categoryDropdown.configure(values=categoryNames)
        if self.category_var.get() == "":
            self.category_var.set(categoryNames[0])

    def updateCategoriesBox(self, categories):
        for widget in self.categoriesFrame.winfo_children():
            widget.destroy()

        if not categories:
            ctk.CTkLabel(self.categoriesFrame, text="No categories yet.", text_color="#aaaaaa").pack(pady=10)
            return

        for cat in categories:
            card = ctk.CTkFrame(self.categoriesFrame)
            card.pack(fill="x", pady=3)

            # top row: name and remaining
            topRow = ctk.CTkFrame(card, fg_color="transparent")
            topRow.pack(fill="x", padx=12, pady=(8, 2))

            ctk.CTkLabel(topRow, text=cat["name"],
                         font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

            remaining = cat["remaining"]
            remaining_color = "#e05555" if remaining < 0 else "#4CAF50"
            remaining_text = f"£{remaining:.2f} left" if remaining >= 0 else "OVERSPENT"
            ctk.CTkLabel(topRow, text=remaining_text,
                         font=ctk.CTkFont(size=12), text_color=remaining_color).pack(side="right")

            # progress bar
            pct = min(cat["spent"] / cat["allocated"], 1.0) if cat["allocated"] > 0 else 0
            bar_color = "#e05555" if pct >= 1.0 else "#f0a500" if pct >= 0.8 else "#4CAF50"
            progressBar = ctk.CTkProgressBar(card, progress_color=bar_color, height=8)
            progressBar.pack(fill="x", padx=12, pady=(0, 2))
            progressBar.set(pct)

            # bottom row: allocated and spent
            bottomRow = ctk.CTkFrame(card, fg_color="transparent")
            bottomRow.pack(fill="x", padx=12, pady=(0, 8))

            ctk.CTkLabel(bottomRow, text=f"£{cat['allocated']:.2f} allocated",
                         font=ctk.CTkFont(size=11), text_color="#888888").pack(side="left")
            ctk.CTkLabel(bottomRow, text=f"£{cat['spent']:.2f} spent",
                         font=ctk.CTkFont(size=11), text_color="#888888").pack(side="left", padx=15)

    def updateTransactionsBox(self, transactions):
        for widget in self.transactionsFrame.winfo_children():
            widget.destroy()

        if not transactions:
            ctk.CTkLabel(self.transactionsFrame, text="No transactions recorded yet.", text_color="#aaaaaa").pack(pady=10)
            return

        for t in transactions:
            row = ctk.CTkFrame(self.transactionsFrame)
            row.pack(fill="x", pady=2)

            # date
            ctk.CTkLabel(row, text=t["date"], width=85,
                         font=ctk.CTkFont(size=12), text_color="#888888").pack(side="left", padx=(12, 5), pady=8)

            # category badge
            ctk.CTkLabel(row, text=t["category_name"],
                         font=ctk.CTkFont(size=11), text_color="#aaaaaa").pack(side="left", padx=(0, 10), pady=8)

            # description
            ctk.CTkLabel(row, text=t["description"],
                         font=ctk.CTkFont(size=12)).pack(side="left", padx=5, pady=8)

            # amount (right-aligned, colour coded)
            amount_color = "#4CAF50" if t["amount"] > 0 else "#e05555"
            ctk.CTkLabel(row, text=f"£{t['amount']:.2f}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=amount_color).pack(side="right", padx=12, pady=8)

    def showSuccess(self, message):
        messagebox.showinfo("Success", message)

    def showError(self, message):
        messagebox.showerror("Error", message)