import customtkinter as ctk
from tkinter import simpledialog, messagebox

"""
Onboarding screen
Shows the 3-step first-run setup flow for the app
"""

class OnboardingView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        # callback set by main.py to launch the main app
        self.onComplete = None

        # ---------- state used by UI ----------
        self.step_frames = {}
        self.category_buttons = {}
        self.allocation_entries = {}

        self.income_var = ctk.StringVar()
        self.available_label_var = ctk.StringVar(value="Available to budget: £0.00")

        self.income_error_var = ctk.StringVar(value="")
        self.category_error_var = ctk.StringVar(value="")
        self.allocation_error_var = ctk.StringVar(value="")

        self.selected_source = None

        # ---------- layout ----------
        self.pack(fill="both", expand=True)

        self._build_header()
        self._build_steps()
        self._build_navigation()

        # connect to controller AFTER UI is built
        self.controller.set_view(self)

    # Build UI

    def _build_header(self):
        title = ctk.CTkLabel(
            self,
            text="First-Time Setup",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w", padx=20, pady=(20, 10))

    def _build_steps(self):
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self._build_step1()
        self._build_step2()
        self._build_step3()

    def _build_navigation(self):
        nav = ctk.CTkFrame(self)
        nav.pack(fill="x", padx=20, pady=(0, 20))

        self.back_button = ctk.CTkButton(
            nav,
            text="Back",
            command=self.controller.on_back
        )
        self.back_button.pack(side="left", padx=10, pady=10)

        self.next_button = ctk.CTkButton(
            nav,
            text="Next",
            command=self.controller.on_next
        )
        self.next_button.pack(side="right", padx=10, pady=10)

    # ---------------- Step 1 ----------------

    def _build_step1(self):
        frame = ctk.CTkFrame(self.content_frame)
        self.step_frames[1] = frame

        title = ctk.CTkLabel(
            frame,
            text="Step 1: Enter Your Income",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(frame, text="Monthly income").pack(anchor="w", padx=20, pady=(10, 0))

        income_entry = ctk.CTkEntry(frame, textvariable=self.income_var)
        income_entry.pack(fill="x", padx=20, pady=5)

        def on_key(event):
            value = self.income_var.get()
            self.controller.on_income_amount_changed(value)
        income_entry.bind("<KeyRelease>", on_key)

        self.income_error_label = ctk.CTkLabel(
            frame,
            textvariable=self.income_error_var,
            text_color="red"
        )
        self.income_error_label.pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(frame, text="Income source").pack(anchor="w", padx=20, pady=(10, 5))

        self.source_buttons_frame = ctk.CTkFrame(frame)
        self.source_buttons_frame.pack(fill="x", padx=20, pady=5)

        self.source_buttons = {}
        for source in self.controller.income_sources:
            btn = ctk.CTkButton(
                self.source_buttons_frame,
                text=source,
                command=lambda s=source: self._select_income_source(s)
            )
            btn.pack(fill="x", pady=5)
            self.source_buttons[source] = btn

    def _select_income_source(self, source):
        self.selected_source = source

        for name, btn in self.source_buttons.items():
            if name == source:
                btn.configure(fg_color="#144870")
            else:
                btn.configure(fg_color="#1f6aa5")

        self.controller.on_income_source_selected(source)

    # ---------------- Step 2 ----------------

    def _build_step2(self):
        frame = ctk.CTkFrame(self.content_frame)
        self.step_frames[2] = frame

        title = ctk.CTkLabel(
            frame,
            text="Step 2: Choose Categories",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            frame,
            text="Click a category to select or deselect it. Selected categories are highlighted.",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        ).pack(anchor="w", padx=20, pady=(0, 5))

        controls = ctk.CTkFrame(frame)
        controls.pack(fill="x", padx=20, pady=10)

        add_btn = ctk.CTkButton(
            controls,
            text="Add Custom Category",
            command=self._handle_add_custom_category
        )
        add_btn.pack(side="left", padx=5, pady=5)

        self.categories_container = ctk.CTkScrollableFrame(frame, height=260)
        self.categories_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.category_error_label = ctk.CTkLabel(
            frame,
            textvariable=self.category_error_var,
            text_color="red"
        )
        self.category_error_label.pack(anchor="w", padx=20, pady=(0, 10))

        self.refresh_categories()

    def refresh_categories(self):
        for widget in self.categories_container.winfo_children():
            widget.destroy()

        self.category_buttons.clear()

        for name in self.controller.available_categories:
            row = ctk.CTkFrame(self.categories_container)
            row.pack(fill="x", pady=4)

            is_selected = name in self.controller.selected_categories

            toggle_btn = ctk.CTkButton(
                row,
                text=name,
                command=lambda n=name: self._toggle_category(n)
            )
            toggle_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

            if is_selected:
                toggle_btn.configure(fg_color="#144870")
            else:
                toggle_btn.configure(fg_color="#1f6aa5")

            rename_btn = ctk.CTkButton(
                row,
                text="Rename",
                width=80,
                command=lambda n=name: self._rename_category(n)
            )
            rename_btn.pack(side="right")

            self.category_buttons[name] = toggle_btn

    def _toggle_category(self, name):
        self.controller.on_category_toggled(name)
        self.refresh_categories()

    def _handle_add_custom_category(self):
        self.controller.on_add_custom_category()
        self.refresh_categories()

    def _rename_category(self, current_name):
        self.controller.on_rename_category(current_name)
        self.refresh_categories()

    # ---------------- Step 3 ----------------

    def _build_step3(self):
        frame = ctk.CTkFrame(self.content_frame)
        self.step_frames[3] = frame

        title = ctk.CTkLabel(
            frame,
            text="Step 3: Allocate Your Budget",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(anchor="w", padx=20, pady=(20, 10))

        self.available_label = ctk.CTkLabel(
            frame,
            textvariable=self.available_label_var,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.available_label.pack(anchor="w", padx=20, pady=(0, 10))

        self.allocations_container = ctk.CTkScrollableFrame(frame, height=300)
        self.allocations_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.allocation_error_label = ctk.CTkLabel(
            frame,
            textvariable=self.allocation_error_var,
            text_color="red"
        )
        self.allocation_error_label.pack(anchor="w", padx=20, pady=(0, 10))

    def refresh_allocations(self):
        for widget in self.allocations_container.winfo_children():
            widget.destroy()

        self.allocation_entries.clear()

        for name in sorted(self.controller.selected_categories):
            row = ctk.CTkFrame(self.allocations_container)
            row.pack(fill="x", pady=4)

            label = ctk.CTkLabel(row, text=name, width=180, anchor="w")
            label.pack(side="left", padx=(0, 10))

            entry = ctk.CTkEntry(row)
            entry.pack(side="left", fill="x", expand=True)

            entry.bind(
                "<KeyRelease>",
                lambda event, category=name, widget=entry:
                    self.controller.on_allocation_changed(category, widget.get())
            )

            self.allocation_entries[name] = entry

    # =========================================================
    # Methods required by controller
    # =========================================================

    def show_step(self, step: int):
        for frame in self.step_frames.values():
            frame.pack_forget()

        self.step_frames[step].pack(fill="both", expand=True)

        if step == 1:
            self.back_button.configure(state="disabled")
            self.next_button.configure(text="Next")
        elif step == 2:
            self.back_button.configure(state="normal")
            self.next_button.configure(text="Next")
            self.refresh_categories()
        elif step == 3:
            self.back_button.configure(state="normal")
            self.next_button.configure(text="Finish")
            self.refresh_allocations()

    def set_next_enabled(self, enabled: bool):
        self.next_button.configure(state="normal" if enabled else "disabled")

    def set_income_error(self, message):
        self.income_error_var.set("" if message is None else message)

    def set_category_error(self, message):
        self.category_error_var.set("" if message is None else message)

    def set_allocation_error(self, message):
        self.allocation_error_var.set("" if message is None else message)

    def update_available_to_budget(self, amount: float):
        self.available_label_var.set(f"Available to budget: £{amount:.2f}")

    def show_custom_category_dialog(self):
        return simpledialog.askstring("Custom Category", "Enter a category name:")

    def show_rename_dialog(self, current_name: str):
        return simpledialog.askstring("Rename Category", "Enter a new name:", initialvalue=current_name)

    def on_setup_complete(self, user):
        messagebox.showinfo("Setup Complete", "Your budget has been created.")
        if self.onComplete is not None:
            self.onComplete(user)