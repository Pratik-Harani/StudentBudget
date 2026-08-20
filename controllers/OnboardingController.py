"""
Manages the 3-step first-run setup flow for the app
This controller calls the onboarding view UI to display the screens for each step, 
receives the user's input and validates it. 

Step 1. Enter Monthly Income and Income Source
        - Income must be a positive integer
        
Step 2. Choosing categories
        - Also allows user to rename a default category or create a new category.
        - Must select more than MIN_CATEGORIES and less than MAX_CATEGORIES
        
Step 3. Allocate monthly income to categories
        - Available budget decreases in real time as the user allocates it to categories
        - Should only let the user finish once Available to Budget amount is 0.
        

"""


from model.model import User, Category
from saveData import saveToFile


DEFAULT_CATEGORIES: list[str] = [
    "Rent / Housing",
    "Groceries",
    "Transport",
    "Entertainment",
    "Savings",
    "Other",
]

MIN_CATEGORIES = 3
MAX_CATEGORIES = 15

# Source options shown as buttons on Step 1 
INCOME_SOURCES: list[str] = [
    "Student Loan",
    "Family Support",
    "Part-time Job",
]



class OnboardingController:
    """
    Typical lifecycle
    
    1. Instantiate: ctrl = OnboardingController()
    2. Attach view:  ctrl.set_view(my_view)
    3. The view renders Step 1 and calls ctrl methods as the user interacts.
    4. When ctrl calls view.on_setup_complete(user), hand the user object
       to AppController and destroy the onboarding window.
    """

    def __init__(self):
        # Step 1 state
        self._income_amount: float | None = None   # validated positive float
        self._income_source: str | None = None     # one of INCOME_SOURCES

        # Step 2 state
        # Start with all defaults selected so the user can just deselect
        self._available_categories: list[str] = list(DEFAULT_CATEGORIES)
        self._selected_categories: set[str] = set(DEFAULT_CATEGORIES)

        # Step 3 state 
        # Maps category name -> allocated amount (float, 0.0 by default)
        self._allocations: dict[str, float] = {}

        # Current step
        self._current_step: int = 1

        self._view = None


    def set_view(self, view) -> None:
        """Call this after constructing both controller and view."""
        self._view = view
        self._view.show_step(1)
        self._refresh_next_button()


    # public helpers for the View

    @property
    def available_categories(self) -> list[str]:
        """All category names the user can choose from (including custom ones)."""
        return list(self._available_categories)

    @property
    def selected_categories(self) -> set[str]:
        """Set of currently selected category names."""
        return set(self._selected_categories)

    @property
    def income_sources(self) -> list[str]:
        return list(INCOME_SOURCES)

    # --------- step 1: entering income ----------

    def on_income_amount_changed(self, raw_value: str) -> None:
        """
        Called every time the income text-box content changes.
        Validates and stores the amount; updates Next button state.

        Parameters
        ----------
        raw_value : str
            The current string contents of the income text box.
        """
        self._income_amount = None
        self._view.set_income_error(None)

        stripped = raw_value.strip()
        if stripped == "":
            # Empty – just disable Next, no error message yet
            self._refresh_next_button()
            return

        try:
            value = float(stripped)
        except ValueError:
            self._view.set_income_error("Please enter a valid number.")
            self._refresh_next_button()
            return

        if value <= 0:
            self._view.set_income_error("Income must be a positive amount.")
            self._refresh_next_button()
            return

        self._income_amount = value
        self._view.set_income_error(None)
        self._refresh_next_button()

    def on_income_source_selected(self, source: str) -> None:
        """
        Called when the user clicks one of the income-source buttons.

        Parameters
        ----------
        source : str
            Must be one of INCOME_SOURCES (or a custom string if the UI
            extends the list).
        """
        self._income_source = source
        self._refresh_next_button()

    # --------- step 2: category selection ----------

    def on_category_toggled(self, name: str) -> None:
        """
        Called when a category button is clicked to select or deselect it.

        Parameters
        ----------
        name : str
            Name of the category being toggled.
        """
        if name in self._selected_categories:
            self._selected_categories.discard(name)
        else:
            self._selected_categories.add(name)

        self._validate_category_selection()
        self._refresh_next_button()

    def on_add_custom_category(self) -> None:
        """
        Called when the user clicks "Add custom category".
        Opens a dialog via the view, then adds the result to available
        and selected categories if valid and not a duplicate.
        """
        name = self._view.show_custom_category_dialog()
        if name is None:
            return  # User cancelled

        name = name.strip()
        if not name:
            self._view.set_category_error("Category name cannot be empty.")
            return

        if name.lower() in {c.lower() for c in self._available_categories}:
            self._view.set_category_error(
                f'"{name}" already exists. Choose a different name.'
            )
            return

        if len(self._available_categories) >= MAX_CATEGORIES + 10:
            # Soft guard: don't let the list grow unreasonably
            self._view.set_category_error(
                "Too many categories defined. Remove some before adding more."
            )
            return

        self._available_categories.append(name)
        self._selected_categories.add(name)
        self._view.set_category_error(None)
        self._validate_category_selection()
        self._refresh_next_button()

    def on_rename_category(self, current_name: str) -> None:
        """
        Called when the user wants to rename an existing category.

        Parameters
        ----------
        current_name : str
            The category to rename.
        """
        new_name = self._view.show_rename_dialog(current_name)
        if new_name is None:
            return  # Cancelled

        new_name = new_name.strip()
        if not new_name:
            self._view.set_category_error("Category name cannot be empty.")
            return

        if new_name.lower() in {
            c.lower() for c in self._available_categories if c != current_name
        }:
            self._view.set_category_error(
                f'"{new_name}" already exists. Choose a different name.'
            )
            return

        # Update available list
        idx = self._available_categories.index(current_name)
        self._available_categories[idx] = new_name

        # Update selected set
        if current_name in self._selected_categories:
            self._selected_categories.discard(current_name)
            self._selected_categories.add(new_name)

        # Update any allocation already entered for this category
        if current_name in self._allocations:
            self._allocations[new_name] = self._allocations.pop(current_name)

        self._view.set_category_error(None)

    # --------- step 3: allocations ----------

    def on_allocation_changed(self, category_name: str, raw_value: str) -> None:
        """
        Called whenever the allocation text-box for a category changes.
        Updates the live "available to budget" counter and saves partial state.

        Parameters
        ----------
        category_name : str
            The category whose allocation field changed.
        raw_value : str
            Current raw string content of that text box.
        """
        self._view.set_allocation_error(None)

        stripped = raw_value.strip()

        if stripped == "" or stripped == ".":
            self._allocations[category_name] = 0.0
        else:
            try:
                value = float(stripped)
            except ValueError:
                self._view.set_allocation_error(
                    f'"{category_name}": enter a valid number.'
                )
                self._allocations[category_name] = 0.0
                self._update_available_to_budget()
                self._refresh_next_button()
                return

            if value < 0:
                self._view.set_allocation_error(
                    f'"{category_name}": amount cannot be negative.'
                )
                self._allocations[category_name] = 0.0
                self._update_available_to_budget()
                self._refresh_next_button()
                return

            self._allocations[category_name] = value

        self._update_available_to_budget()
        self._refresh_next_button()

    # --- Navigation from one step to the next

    def on_next(self) -> None:
        """Called when the user clicks the Next / Finish button."""
        if self._current_step == 1:
            if not self._step1_valid():
                return
            self._current_step = 2
            self._validate_category_selection()
            self._refresh_next_button()
            self._view.show_step(2)

        elif self._current_step == 2:
            if not self._step2_valid():
                return
            # Initialise allocations for the chosen categories
            for name in self._selected_categories:
                self._allocations.setdefault(name, 0.0)
            self._current_step = 3
            self._update_available_to_budget()
            self._refresh_next_button()
            self._view.show_step(3)

        elif self._current_step == 3:
            if not self._step3_valid():
                return
            self._finish_setup()

    def on_back(self) -> None:
        """Called when the user clicks the Back button."""
        if self._current_step > 1:
            self._current_step -= 1
            self._refresh_next_button()
            self._view.show_step(self._current_step)
            


    # --- Internal helpers ---

    def _step1_valid(self) -> bool:
        return self._income_amount is not None and self._income_amount > 0

    def _step2_valid(self) -> bool:
        count = len(self._selected_categories)
        return MIN_CATEGORIES <= count <= MAX_CATEGORIES

    def _step3_valid(self) -> bool:
        remaining = self._remaining_to_allocate()
        # Allow a small floating-point tolerance (+-0.01) 
        return abs(remaining) < 0.01

    def _validate_category_selection(self) -> None:
        """Push a helpful message to the view based on selection count."""
        count = len(self._selected_categories)
        if count < MIN_CATEGORIES:
            self._view.set_category_error(
                f"Select at least {MIN_CATEGORIES} categories "
                f"({MIN_CATEGORIES - count} more needed)."
            )
        elif count > MAX_CATEGORIES:
            self._view.set_category_error(
                f"You can select at most {MAX_CATEGORIES} categories "
                f"(deselect {count - MAX_CATEGORIES})."
            )
        else:
            self._view.set_category_error(None)

    def _total_allocated(self) -> float:
        return sum(self._allocations.get(name, 0.0)
                   for name in self._selected_categories)

    def _remaining_to_allocate(self) -> float:
        """Positive means money still to allocate; negative means over-budget."""
        return (self._income_amount or 0.0) - self._total_allocated()

    def _update_available_to_budget(self) -> None:
        self._view.update_available_to_budget(self._remaining_to_allocate())

    def _refresh_next_button(self) -> None:
        """Enable or disable the Next button based on current step validity."""
        if self._current_step == 1:
            enabled = self._step1_valid()
        elif self._current_step == 2:
            enabled = self._step2_valid()
        else:
            enabled = self._step3_valid()
        self._view.set_next_enabled(enabled)

    def _finish_setup(self) -> None:
        """
        Build the User object, persist it, then hand off to the view so it
        can launch the main AppController.
        """
        user = User()
        user.monthly_income = self._income_amount
        user.income_source = self._income_source  # stored for display/info

        for name in self._selected_categories:
            allocated = self._allocations.get(name, 0.0)
            category = Category(name, allocated)
            user.addCategory(category)

        saveToFile(user)
        self._view.on_setup_complete(user)
