import customtkinter as ctk
from gui.styles import COLORS, FONTS
from auth import login_user, register_user

class LoginFrame(ctk.CTkFrame):

    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=COLORS['bg_dark'])
        self.on_login_success = on_login_success
        self.is_login_mode = True
        self._build_ui()

    def _build_ui(self):
        center = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=20, width=420, height=600)
        center.place(relx=0.5, rely=0.5, anchor='center')
        center.pack_propagate(False)
        inner = ctk.CTkFrame(center, fg_color='transparent')
        inner.pack(expand=True, fill='both', padx=40, pady=30)
        ctk.CTkLabel(inner, text='✅ TaskFlow', font=('Segoe UI', 28, 'bold'), text_color=COLORS['accent']).pack(pady=(10, 2))
        ctk.CTkLabel(inner, text='Smart To-Do Manager', font=FONTS['small'], text_color=COLORS['text_secondary']).pack(pady=(0, 20))
        toggle_frame = ctk.CTkFrame(inner, fg_color=COLORS['bg_secondary'], corner_radius=10)
        toggle_frame.pack(fill='x', pady=(0, 15))
        self.login_btn = ctk.CTkButton(toggle_frame, text='Sign In', font=FONTS['button'], fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'], corner_radius=8, command=lambda: self._switch_mode(True))
        self.login_btn.pack(side='left', expand=True, fill='x', padx=3, pady=3)
        self.register_btn = ctk.CTkButton(toggle_frame, text='Register', font=FONTS['button'], fg_color='transparent', hover_color=COLORS['bg_tertiary'], text_color=COLORS['text_secondary'], corner_radius=8, command=lambda: self._switch_mode(False))
        self.register_btn.pack(side='right', expand=True, fill='x', padx=3, pady=3)
        self.form = ctk.CTkFrame(inner, fg_color='transparent')
        self.form.pack(fill='x', expand=True)
        self._build_login_form()

    def _clear_form(self):
        for w in self.form.winfo_children():
            w.destroy()

    def _switch_mode(self, is_login):
        self.is_login_mode = is_login
        if is_login:
            self.login_btn.configure(fg_color=COLORS['accent'], text_color=COLORS['text_primary'])
            self.register_btn.configure(fg_color='transparent', text_color=COLORS['text_secondary'])
            self._build_login_form()
        else:
            self.register_btn.configure(fg_color=COLORS['accent'], text_color=COLORS['text_primary'])
            self.login_btn.configure(fg_color='transparent', text_color=COLORS['text_secondary'])
            self._build_register_form()

    def _build_login_form(self):
        self._clear_form()
        ctk.CTkLabel(self.form, text='Username', font=FONTS['small'], text_color=COLORS['text_secondary'], anchor='w').pack(fill='x', pady=(5, 2))
        self.login_user_entry = ctk.CTkEntry(self.form, font=FONTS['body'], height=40, fg_color=COLORS['bg_secondary'], border_color=COLORS['border'], placeholder_text='Enter your username')
        self.login_user_entry.pack(fill='x', pady=(0, 8))
        ctk.CTkLabel(self.form, text='Password', font=FONTS['small'], text_color=COLORS['text_secondary'], anchor='w').pack(fill='x', pady=(0, 2))
        self.login_pass_entry = ctk.CTkEntry(self.form, font=FONTS['body'], height=40, show='•', fg_color=COLORS['bg_secondary'], border_color=COLORS['border'], placeholder_text='Enter your password')
        self.login_pass_entry.pack(fill='x', pady=(0, 15))
        self.login_pass_entry.bind('<Return>', lambda e: self._do_login())
        self.login_msg = ctk.CTkLabel(self.form, text='', font=FONTS['small'], text_color=COLORS['danger'])
        self.login_msg.pack(pady=(0, 5))
        ctk.CTkButton(self.form, text='Sign In', font=FONTS['button'], height=42, fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'], corner_radius=10, command=self._do_login).pack(fill='x')

    def _build_register_form(self):
        self._clear_form()
        fields = [('Username', 'Choose a username', False), ('Email', 'your@email.com', False), ('Password', 'At least 6 characters', True), ('Confirm Password', 'Re-enter password', True)]
        self.reg_entries = {}
        for label, ph, is_pw in fields:
            ctk.CTkLabel(self.form, text=label, font=FONTS['small'], text_color=COLORS['text_secondary'], anchor='w').pack(fill='x', pady=(3, 1))
            e = ctk.CTkEntry(self.form, font=FONTS['body'], height=38, fg_color=COLORS['bg_secondary'], border_color=COLORS['border'], placeholder_text=ph, show='•' if is_pw else '')
            e.pack(fill='x', pady=(0, 4))
            self.reg_entries[label] = e
        self.reg_msg = ctk.CTkLabel(self.form, text='', font=FONTS['small'], text_color=COLORS['danger'])
        self.reg_msg.pack(pady=(3, 5))
        ctk.CTkButton(self.form, text='Create Account', font=FONTS['button'], height=42, fg_color=COLORS['success'], hover_color='#2ea043', corner_radius=10, command=self._do_register).pack(fill='x')

    def _do_login(self):
        user, msg = login_user(self.login_user_entry.get(), self.login_pass_entry.get())
        if user:
            self.on_login_success(user)
        else:
            self.login_msg.configure(text=msg, text_color=COLORS['danger'])

    def _do_register(self):
        pw = self.reg_entries['Password'].get()
        cpw = self.reg_entries['Confirm Password'].get()
        if pw != cpw:
            self.reg_msg.configure(text='Passwords do not match.', text_color=COLORS['danger'])
            return
        ok, msg = register_user(self.reg_entries['Username'].get(), self.reg_entries['Email'].get(), pw)
        if ok:
            self.reg_msg.configure(text=msg, text_color=COLORS['success'])
            self.after(1000, lambda: self._switch_mode(True))
        else:
            self.reg_msg.configure(text=msg, text_color=COLORS['danger'])
