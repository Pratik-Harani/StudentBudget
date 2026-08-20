"""
Categories screen
Shows list of categories, budget reallocation, and alerts.
"""

import customtkinter as ctk
from tkinter import messagebox


class CategoriesView(ctk.CTkFrame):
    

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.from_var = ctk.StringVar()
        self.to_var = ctk.StringVar()
        self.realloc_amount_var = ctk.StringVar()
        self.new_cat_name_var = ctk.StringVar()
        self.new_cat_amount_var = ctk.StringVar()

        self.buildUI()

    def buildUI(self):
        # scrollable content area
        self.scrollFrame = ctk.CTkScrollableFrame(self)
        self.scrollFrame.pack(fill="both", expand=True, padx=20, pady=10)

        # alerts section (filled dynamically)
        self.alertsFrame = ctk.CTkFrame(self.scrollFrame)
        self.alertsFrame.pack(fill="x", pady=(0, 10))

        # category cards container
        self.listFrame = ctk.CTkFrame(self.scrollFrame, fg_color="transparent")
        self.listFrame.pack(fill="x", pady=(0, 10))

        # reallocation section
        ctk.CTkLabel(
            self.scrollFrame, text="Reallocate Budget",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        reallocFrame = ctk.CTkFrame(self.scrollFrame)
        reallocFrame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(reallocFrame, text="From").pack(anchor="w", padx=10, pady=(10, 0))
        self.fromDropdown = ctk.CTkComboBox(reallocFrame, variable=self.from_var, values=[])
        self.fromDropdown.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(reallocFrame, text="To").pack(anchor="w", padx=10, pady=(10, 0))
        self.toDropdown = ctk.CTkComboBox(reallocFrame, variable=self.to_var, values=[])
        self.toDropdown.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(reallocFrame, text="Amount").pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkEntry(reallocFrame, textvariable=self.realloc_amount_var).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            reallocFrame, text="Transfer",
            command=self.onReallocate
        ).pack(fill="x", padx=10, pady=15)

        # add category section
        ctk.CTkLabel(
            self.scrollFrame, text="Add Category",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        addCatFrame = ctk.CTkFrame(self.scrollFrame)
        addCatFrame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(addCatFrame, text="Name").pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkEntry(addCatFrame, textvariable=self.new_cat_name_var, placeholder_text="e.g. Subscriptions").pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(addCatFrame, text="Allocated Amount (£)").pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkEntry(addCatFrame, textvariable=self.new_cat_amount_var, placeholder_text="e.g. 50").pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            addCatFrame, text="Add Category",
            command=self.onAddCategory
        ).pack(fill="x", padx=10, pady=15)

        # detail panel (hidden by default)
        self.detailFrame = ctk.CTkFrame(self)
        self.detailLabel = ctk.CTkLabel(self.detailFrame, text="", justify="left",
                                         font=ctk.CTkFont(size=14))
        self.detailLabel.pack(anchor="w", padx=15, pady=(10, 5))
        self.detailTransactionsFrame = ctk.CTkScrollableFrame(self.detailFrame)
        self.detailTransactionsFrame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkButton(
            self.detailFrame, text="← Back to Categories",
            command=self.hideDetail
        ).pack(pady=10)

    def onReallocate(self):
        """Collect reallocation data and pass to controller."""
        data = {
            "from_name": self.from_var.get().strip(),
            "to_name": self.to_var.get().strip(),
            "amount": self.realloc_amount_var.get().strip(),
        }
        self.controller.reallocateBudget(data)

    def clearReallocForm(self):
        self.realloc_amount_var.set("")

    def onAddCategory(self):
        """Collect new category data and pass to controller."""
        data = {
            "name": self.new_cat_name_var.get().strip(),
            "allocated": self.new_cat_amount_var.get().strip(),
        }
        self.controller.addNewCategory(data)

    def clearAddCategoryForm(self):
        self.new_cat_name_var.set("")
        self.new_cat_amount_var.set("")

    # --- methods the controller calls ---

    def updateCategoryDropdowns(self, categoryNames):
        if not categoryNames:
            categoryNames = ["No categories"]
        self.fromDropdown.configure(values=categoryNames)
        self.toDropdown.configure(values=categoryNames)
        if self.from_var.get() == "":
            self.from_var.set(categoryNames[0])
        if self.to_var.get() == "":
            self.to_var.set(categoryNames[-1] if len(categoryNames) > 1 else categoryNames[0])

    def displayAlerts(self, alerts):
        """Show spending alerts. alerts is a list of dicts with name, percentage, remaining."""
        for widget in self.alertsFrame.winfo_children():
            widget.destroy()

        if not alerts:
            self.alertsFrame.pack_forget()
            return

        self.alertsFrame.pack(fill="x", pady=(0, 10), before=self.listFrame)

        ctk.CTkLabel(
            self.alertsFrame, text="⚠ Spending Alerts",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e05555"
        ).pack(anchor="w", padx=10, pady=(10, 5))

        for alert in alerts:
            ctk.CTkLabel(
                self.alertsFrame,
                text=f"{alert['name']}: {alert['percentage']}% of budget used (£{alert['remaining']:.2f} remaining)",
                text_color="#f0a500",
                font=ctk.CTkFont(size=13)
            ).pack(anchor="w", padx=15, pady=2)

        ctk.CTkLabel(self.alertsFrame, text="").pack(pady=2)  # spacing

    def displayCategories(self, categories):
        """Show the list of categories."""
        for widget in self.listFrame.winfo_children():
            widget.destroy()

        if not categories:
            ctk.CTkLabel(self.listFrame, text="No categories yet.").pack(pady=20)
            return

        for cat in categories:
            card = ctk.CTkFrame(self.listFrame)
            card.pack(fill="x", pady=5)

            # top row: name and remaining
            topRow = ctk.CTkFrame(card, fg_color="transparent")
            topRow.pack(fill="x", padx=15, pady=(10, 2))

            ctk.CTkLabel(topRow, text=cat["name"],
                         font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")

            remaining = cat["remaining"]
            remaining_color = "#e05555" if remaining < 0 else "#4CAF50"
            remaining_text = f"£{remaining:.2f} left" if remaining >= 0 else "OVERSPENT"
            ctk.CTkLabel(topRow, text=remaining_text,
                         font=ctk.CTkFont(size=13), text_color=remaining_color).pack(side="right")

            # progress bar
            pct = min(cat["spent"] / cat["allocated"], 1.0) if cat["allocated"] > 0 else 0
            bar_color = "#e05555" if pct >= 1.0 else "#f0a500" if pct >= 0.8 else "#4CAF50"
            progressBar = ctk.CTkProgressBar(card, progress_color=bar_color, height=10)
            progressBar.pack(fill="x", padx=15, pady=(0, 4))
            progressBar.set(pct)

            # bottom row: allocated, spent, button
            bottomRow = ctk.CTkFrame(card, fg_color="transparent")
            bottomRow.pack(fill="x", padx=15, pady=(0, 10))

            ctk.CTkLabel(bottomRow, text=f"£{cat['allocated']:.2f} allocated",
                         font=ctk.CTkFont(size=11), text_color="#888888").pack(side="left")
            ctk.CTkLabel(bottomRow, text=f"£{cat['spent']:.2f} spent",
                         font=ctk.CTkFont(size=11), text_color="#888888").pack(side="left", padx=15)

            ctk.CTkButton(
                bottomRow, text="View Transactions", width=140, height=28,
                command=lambda name=cat["name"]: self.controller.showCategoryDetail(name)
            ).pack(side="right")

            ctk.CTkButton(
                bottomRow, text="Delete", width=70, height=28,
                fg_color="#e05555", hover_color="#c04444",
                command=lambda name=cat["name"]: self.onDeleteCategory(name)
            ).pack(side="right", padx=(0, 5))

    def displayCategoryDetail(self, name, allocated, spent, remaining, transactions):
        """Show detail view for a single category."""
        self.scrollFrame.pack_forget()
        self.detailFrame.pack(fill="both", expand=True, padx=20, pady=10)

        remaining_color = "#e05555" if remaining < 0 else "#4CAF50"
        self.detailLabel.configure(
            text=f"{name}     Allocated: £{allocated:.2f}   |   Spent: £{spent:.2f}   |   Remaining: £{remaining:.2f}"
        )

        # clear old rows
        for widget in self.detailTransactionsFrame.winfo_children():
            widget.destroy()

        if not transactions:
            ctk.CTkLabel(self.detailTransactionsFrame, text="No transactions recorded for this category.",
                         text_color="#aaaaaa").pack(pady=20)
        else:
            for t in transactions:
                row = ctk.CTkFrame(self.detailTransactionsFrame)
                row.pack(fill="x", pady=2)

                ctk.CTkLabel(row, text=t["date"], width=85,
                             font=ctk.CTkFont(size=12), text_color="#888888").pack(side="left", padx=(12, 5), pady=8)

                ctk.CTkLabel(row, text=t["description"],
                             font=ctk.CTkFont(size=12)).pack(side="left", padx=5, pady=8)

                amount_color = "#4CAF50" if t["amount"] > 0 else "#e05555"
                ctk.CTkLabel(row, text=f"£{t['amount']:.2f}",
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=amount_color).pack(side="right", padx=12, pady=8)

    def hideDetail(self):
        """Go back from detail view to category list."""
        self.detailFrame.pack_forget()
        self.scrollFrame.pack(fill="both", expand=True, padx=20, pady=10)
        self.controller.refreshCategories()

    def onDeleteCategory(self, categoryName):
        """Show a dialog to pick where to move transactions, then delete."""
        # get other category names for the dropdown
        otherNames = []
        for cat in self.controller.user.categories:
            if cat.name != categoryName:
                otherNames.append(cat.name)

        if not otherNames:
            self.showError("Cannot delete the only category.")
            return

        # create dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Delete {categoryName}")
        dialog.geometry("400x200")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f'Delete "{categoryName}"?',
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Move transactions and budget to:",
                     font=ctk.CTkFont(size=12)).pack(pady=(0, 10))

        moveToVar = ctk.StringVar(value=otherNames[0])
        ctk.CTkComboBox(dialog, variable=moveToVar, values=otherNames).pack(padx=20, pady=5)

        def confirm():
            self.controller.deleteCategory(categoryName, moveToVar.get())
            dialog.destroy()

        btnFrame = ctk.CTkFrame(dialog, fg_color="transparent")
        btnFrame.pack(pady=15)
        ctk.CTkButton(btnFrame, text="Cancel", width=100, fg_color="transparent",
                      command=dialog.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btnFrame, text="Delete", width=100, fg_color="#e05555",
                      hover_color="#c04444", command=confirm).pack(side="left", padx=10)

    def showSuccess(self, message):
        messagebox.showinfo("Success", message)

    def showError(self, message):
        messagebox.showerror("Error", message)