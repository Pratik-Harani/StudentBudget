"""
Main application window. Manages switching between screens and all logic.
"""


import customtkinter as ctk
from model.model import Transaction
from saveData import saveToFile
from views.dashboard import DashboardView
from views.categories_screen import CategoriesView
from views.transactions_screen import TransactionsView


class AppController(ctk.CTk):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.title("StudentBudget")
        self.geometry("900x700")

        # navbar at top — always visible
        self.navBar = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=0, height=50)
        self.navBar.pack(fill="x")
        self.navBar.pack_propagate(False)

        ctk.CTkLabel(
            self.navBar, text="StudentBudget",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20)

        # nav buttons (right-aligned)
        self.transactionsNavBtn = ctk.CTkButton(
            self.navBar, text="Transactions", width=120, height=32,
            fg_color="transparent", hover_color="#2a2a4e",
            command=self.showTransactionsScreen
        )
        self.transactionsNavBtn.pack(side="right", padx=5, pady=9)

        self.categoriesNavBtn = ctk.CTkButton(
            self.navBar, text="Categories", width=120, height=32,
            fg_color="transparent", hover_color="#2a2a4e",
            command=self.showCategoriesScreen
        )
        self.categoriesNavBtn.pack(side="right", padx=5, pady=9)

        self.dashboardNavBtn = ctk.CTkButton(
            self.navBar, text="Dashboard", width=120, height=32,
            fg_color="transparent", hover_color="#2a2a4e",
            command=self.showDashboardScreen
        )
        self.dashboardNavBtn.pack(side="right", padx=5, pady=9)

        # container that holds all screens
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # create all screens
        self.dashboardView = DashboardView(self.container, self)
        self.categoriesView = CategoriesView(self.container, self)
        self.transactionsView = TransactionsView(self.container, self)

        # save on window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # start on dashboard
        self.showDashboardScreen()

    def on_close(self):
        saveToFile(self.user)
        self.destroy()

    # --- screen switching ---

    def _highlightNavButton(self, activeBtn):
        """Highlight the active nav button, reset others."""
        for btn in [self.dashboardNavBtn, self.categoriesNavBtn, self.transactionsNavBtn]:
            btn.configure(fg_color="transparent")
        activeBtn.configure(fg_color="#3a3a6e")

    def showDashboardScreen(self):
        self.categoriesView.pack_forget()
        self.transactionsView.pack_forget()
        self.dashboardView.pack(fill="both", expand=True)
        self._highlightNavButton(self.dashboardNavBtn)
        self.refreshDashboard()

    def showCategoriesScreen(self):
        self.dashboardView.pack_forget()
        self.transactionsView.pack_forget()
        self.categoriesView.pack(fill="both", expand=True)
        self._highlightNavButton(self.categoriesNavBtn)
        self.refreshCategories()

    def showTransactionsScreen(self):
        self.dashboardView.pack_forget()
        self.categoriesView.pack_forget()
        self.transactionsView.pack(fill="both", expand=True)
        self._highlightNavButton(self.transactionsNavBtn)
        self.refreshTransactions()

    # --- dashboard logic ---

    def refreshDashboard(self):
        # summary
        self.dashboardView.updateSummary(
            self.user.monthly_income,
            self.user.totalSpent(),
            self.user.availableToBudget(),
        )

        # category dropdown
        categoryNames = [cat.name for cat in self.user.categories]
        self.dashboardView.updateCategoryDropdown(categoryNames)

        # categories box
        categoryData = []
        for cat in self.user.categories:
            categoryData.append({
                "name": cat.name,
                "allocated": cat.allocatedAmount,
                "spent": cat.spentAmount(self.user.transactions),
                "remaining": cat.currentAmount(self.user.transactions),
            })
        self.dashboardView.updateCategoriesBox(categoryData)

        # recent transactions
        recentData = []
        for t in self.user.recentTransactions(5):
            recentData.append({
                "description": t.description,
                "category_name": t.category.name,
                "date": t.date.strftime("%d/%m/%Y"),
                "amount": t.amount,
            })
        self.dashboardView.updateTransactionsBox(recentData)

    def addExpenseFromDashboard(self, data):
        """Called when user clicks Add Expense on the dashboard."""
        self._processTransaction(data, self.dashboardView)

    # --- categories logic ---

    def refreshCategories(self):
        categoryData = []
        for cat in self.user.categories:
            categoryData.append({
                "name": cat.name,
                "allocated": cat.allocatedAmount,
                "spent": cat.spentAmount(self.user.transactions),
                "remaining": cat.currentAmount(self.user.transactions),
            })
        self.categoriesView.displayCategories(categoryData)

        # update dropdowns for reallocation
        categoryNames = [cat.name for cat in self.user.categories]
        self.categoriesView.updateCategoryDropdowns(categoryNames)

        # show spending alerts
        alerts = self.user.getSpendingAlerts()
        self.categoriesView.displayAlerts(alerts)

    def showCategoryDetail(self, categoryName):
        """Called when user clicks View Transactions on a category card."""
        category = self.user.findCategory(categoryName)
        if category is None:
            return

        transactionData = []
        for t in category.getTransactions(self.user.transactions):
            transactionData.append({
                "date": t.date.strftime("%d/%m/%Y"),
                "amount": t.amount,
                "description": t.description,
            })

        self.categoriesView.displayCategoryDetail(
            name=category.name,
            allocated=category.allocatedAmount,
            spent=category.spentAmount(self.user.transactions),
            remaining=category.currentAmount(self.user.transactions),
            transactions=transactionData,
        )

    def reallocateBudget(self, data):
        """Called when user clicks Transfer on the categories screen."""
        # validate amount
        try:
            amount = float(data["amount"])
        except ValueError:
            self.categoriesView.showError("Amount must be a valid number.")
            return

        # find categories
        fromCategory = self.user.findCategory(data["from_name"])
        toCategory = self.user.findCategory(data["to_name"])

        if fromCategory is None or toCategory is None:
            self.categoriesView.showError("Category not found.")
            return

        # call model to do the transfer
        try:
            self.user.reallocateBudget(fromCategory, toCategory, amount)
        except ValueError as e:
            self.categoriesView.showError(str(e))
            return

        self.categoriesView.showSuccess(
            f"Transferred £{amount:.2f} from {fromCategory.name} to {toCategory.name}."
        )
        self.categoriesView.clearReallocForm()
        saveToFile(self.user)
        self.refreshCategories()

    def addNewCategory(self, data):
        """Called when user clicks Add Category on the categories screen."""
        name = data.get("name", "").strip()
        amountStr = data.get("allocated", "").strip()

        if not name:
            self.categoriesView.showError("Category name cannot be empty.")
            return

        # check for duplicate
        if self.user.findCategory(name) is not None:
            self.categoriesView.showError(f'"{name}" already exists.')
            return

        try:
            allocated = float(amountStr)
        except ValueError:
            self.categoriesView.showError("Allocated amount must be a valid number.")
            return

        if allocated < 0:
            self.categoriesView.showError("Allocated amount cannot be negative.")
            return

        from model.model import Category
        category = Category(name, allocated)
        self.user.addCategory(category)
        self.categoriesView.showSuccess(f'Category "{name}" added.')
        self.categoriesView.clearAddCategoryForm()
        saveToFile(self.user)
        self.refreshCategories()

    def deleteCategory(self, categoryName, moveToName):
        """Called when user confirms category deletion."""
        category = self.user.findCategory(categoryName)
        moveToCategory = self.user.findCategory(moveToName)

        if category is None or moveToCategory is None:
            self.categoriesView.showError("Category not found.")
            return

        try:
            self.user.removeCategory(category, moveToCategory)
        except ValueError as e:
            self.categoriesView.showError(str(e))
            return

        self.categoriesView.showSuccess(
            f'Deleted "{categoryName}". Transactions and budget moved to "{moveToName}".'
        )
        saveToFile(self.user)
        self.refreshCategories()

    # --- transactions logic ---

    def refreshTransactions(self):
        categoryNames = [cat.name for cat in self.user.categories]
        self.transactionsView.updateCategoryDropdown(categoryNames)

        transactionData = []
        for t in reversed(self.user.transactions):
            transactionData.append({
                "category_name": t.category.name,
                "date": t.date.strftime("%d/%m/%Y"),
                "amount": t.amount,
                "description": t.description,
            })
        self.transactionsView.displayAllTransactions(transactionData)

    def addTransaction(self, data):
        """Called when user clicks Add Transaction on the transactions screen."""
        self._processTransaction(data, self.transactionsView)

    # --- shared helper ---

    def _processTransaction(self, data, view):
        """Validate input, create Transaction via model, update view."""
        # validate amount
        try:
            amount = float(data["amount"])
        except ValueError:
            view.showError("Amount must be a valid number.")
            return

        if amount == 0:
            view.showError("Amount cannot be zero.")
            return

        # apply expense/refund sign based on type
        txType = data.get("type", "expense")
        if txType == "expense" and amount > 0:
            amount = -amount
        elif txType == "refund" and amount < 0:
            amount = abs(amount)

        # find category
        category = self.user.findCategory(data["category_name"])
        if category is None:
            view.showError("Category not found.")
            return

        # create transaction via model (validates date + description)
        try:
            transaction = Transaction(category, data["date"], amount, data["description"])
            self.user.addTransaction(transaction)
        except ValueError as e:
            view.showError(str(e))
            return

        view.showSuccess("Transaction added successfully.")
        view.clearForm()
        saveToFile(self.user)

        # refresh whichever screen we're on
        if view == self.dashboardView:
            self.refreshDashboard()
        elif view == self.transactionsView:
            self.refreshTransactions()