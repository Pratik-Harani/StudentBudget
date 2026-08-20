"""
Defines the base classes and their methods for the app. 

An object of the User class is the single source of truth for the app
It stores a list of transaction objects and category objects. 

"""

from datetime import datetime

class Transaction:
    # An object of class Transaction represents a single transaction, with all of its information.
    # This class uses setters for fields that require validation before storing, such as description and date. 

    def __init__(self, category, date, amount, description):
        self.category = category
        self.date = date
        self.amount = amount
        self.description = description

    @property
    def description(self):
        return self._description

    
    @description.setter
    def description(self, value):
        words = value.strip().split()
        if len(words) > 100:
            raise ValueError("Description cannot be more than 100 words")
        self._description = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        try:
            parsedDate = datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Date must be in DD/MM/YYYY format")

        if parsedDate > datetime.now():
            raise ValueError("Date cannot be in the future")

        self._date = parsedDate



class Category:
    # An object of class Category represents a single spending category in the app.

    def __init__(self, name, allocatedAmount):
        self.name = name
        self.allocatedAmount = allocatedAmount

    def currentAmount(self, transactions):
        currentAmount = self.allocatedAmount
        for t in transactions:
            if t.category is self:
                currentAmount += t.amount
        return currentAmount

    def spentAmount(self, transactions):
        spent = 0
        for t in transactions:
            if t.category is self and t.amount < 0:
                spent += abs(t.amount)
        return spent

    def getTransactions(self, transactions):
        return [t for t in transactions if t.category is self]


class User:
    # An object of class User is the single source of truth for the app.
    # It stores a list of categories and a list of global transactions.  

    def __init__(self):
        self.categories = []
        self.transactions = []
        self.monthly_income = 0

    def addTransaction(self, transaction):
        self.transactions.append(transaction)

    def addCategory(self, category):
        self.categories.append(category)

    def removeCategory(self, category, moveToCategory):
        if category is moveToCategory:
            raise ValueError("Cannot move transactions to the same category being deleted.")
        if category not in self.categories:
            raise ValueError("Category not found.")
        if moveToCategory not in self.categories:
            raise ValueError("Target category not found.")

        # move all transactions to the target category
        for t in self.transactions:
            if t.category is category:
                t.category = moveToCategory

        # add the deleted category's allocated amount to the target
        moveToCategory.allocatedAmount += category.allocatedAmount

        self.categories.remove(category)

    def findCategory(self, name):
        for category in self.categories:
            if category.name.lower() == name.lower():
                return category
        return None

    def totalSpent(self):
        total = 0
        for t in self.transactions:
            if t.amount < 0:
                total += abs(t.amount)
        return total

    def totalAllocated(self):
        total = 0
        for cat in self.categories:
            total += cat.allocatedAmount
        return total

    def availableToBudget(self):
        return self.monthly_income - self.totalAllocated()

    def recentTransactions(self, limit=5):
        indexed = list(enumerate(self.transactions))
        indexed.sort(key=lambda pair: (pair[1].date, pair[0]), reverse=True)
        return [t for i, t in indexed[:limit]]

    def reallocateBudget(self, fromCategory, toCategory, amount):
        if fromCategory is toCategory:
            raise ValueError("Cannot transfer to the same category.")
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        remaining = fromCategory.currentAmount(self.transactions)
        if amount > remaining:
            raise ValueError(f"Not enough budget in {fromCategory.name}. Only £{remaining:.2f} remaining.")
        fromCategory.allocatedAmount -= amount
        toCategory.allocatedAmount += amount

    def getSpendingAlerts(self):
        #Returns list of dicts for categories at >80% spending.
        alerts = []
        for cat in self.categories:
            if cat.allocatedAmount > 0:
                spent = cat.spentAmount(self.transactions)
                ratio = spent / cat.allocatedAmount
                if ratio >= 0.8:
                    alerts.append({
                        "name": cat.name,
                        "percentage": int(ratio * 100),
                        "remaining": cat.currentAmount(self.transactions),
                    })
        return alerts