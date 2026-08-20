from saveData import loadFromFile
from controllers.AppController import AppController
from controllers.OnboardingController import OnboardingController
from views.OnboardingView import OnboardingView
import customtkinter as ctk

#ctk.set_appearance_mode("dark")

def launchApp(user):
    app = AppController(user)
    app.mainloop()

def launchOnboarding():
    root = ctk.CTk()
    root.geometry("700x650")
    root.title("StudentBudget - Setup")

    controller = OnboardingController()
    view = OnboardingView(root, controller)

    #when onboarding finishes, destroy this window and launch main app
    view.onComplete = lambda user: (root.destroy(), launchApp(user))

    root.mainloop()


user = loadFromFile()

if user is None:
    launchOnboarding()
else:
    launchApp(user)