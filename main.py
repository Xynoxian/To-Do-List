from database import initialize_database
from gui.app import App

def main():
    initialize_database()
    app = App()
    app.mainloop()
if __name__ == '__main__':
    main()
