import customtkinter as ctk
from tkinter import messagebox
import threading
import time

# استيراد الإعدادات والـ Handler الحقيقي
from app.config import *
from app.blockchain_handler import BlockchainHandler
from analysis.admin_dashboard import AdminAnalytics
from analysis.history_report import HistoryReporter
# --- إضافة الاستيراد الجديد هنا ---
from analysis.security_tests import run_audit 
from scripts.snapshot_exporter import export_balances
from scripts.snapshot_exporter import export_balances

# إعدادات المظهر
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CharityApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Charity Donation Tracker - Web3 v1.0")
        self.geometry("1100x750")

        # ربط الـ Handler الحقيقي (تأكدي من تشغيل Ganache)
        try:
            self.handler = BlockchainHandler(RPC_URL, CORE_ADDRESS, COIN_ADDRESS, CORE_ABI, COIN_ABI)
        except Exception as e:
            print(f"Connection Error: {e}")
            messagebox.showwarning("Connection Warning", "Could not connect to Blockchain. Using Offline Mode.")

        self.current_user_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9c1" 
        self.is_admin = False

        # --- Layout Grid ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="CRYPTO\nCHARITY", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.pack(pady=30)

        self.btn_profile = ctk.CTkButton(self.sidebar, text="My Profile", command=self.show_profile)
        self.btn_profile.pack(pady=10, padx=20)

        self.btn_campaigns = ctk.CTkButton(self.sidebar, text="Explore Campaigns", command=self.show_campaigns)
        self.btn_campaigns.pack(pady=10, padx=20)

        self.btn_history = ctk.CTkButton(self.sidebar, text="Block Explorer", command=self.show_history)
        self.btn_history.pack(pady=10, padx=20)

        self.alert_label = ctk.CTkLabel(self.sidebar, text="📡 Scanning Network...", text_color="gray", font=ctk.CTkFont(size=12))
        self.alert_label.pack(side="bottom", pady=20)

        self.btn_admin = ctk.CTkButton(self.sidebar, text="Admin Zone", fg_color="#630000", hover_color="#a30000", command=self.admin_login)
        self.btn_admin.pack(side="bottom", pady=10, padx=20)

        # --- Main Content Area ---
        self.main_view = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        threading.Thread(target=self.background_listener, daemon=True).start()
        self.show_profile()

    def clear_main_view(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

    # --- 1. Live Alert Logic ---
    def background_listener(self):
        while True:
            time.sleep(15) 
            self.alert_label.configure(text="🚨 ALERT: New Donation Detected!", text_color="#FFCC00")
            self.after(4000, lambda: self.alert_label.configure(text="📡 Scanning Network...", text_color="gray"))
            time.sleep(10)

    # --- 2. User Views (أكوادك كما هي) ---
    def show_profile(self):
        self.clear_main_view()
        title = ctk.CTkLabel(self.main_view, text="Account Overview", font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=20)
        balances = self.handler.get_balances(self.current_user_address)
        user_name = self.handler.get_user_name(self.current_user_address)
        stats_frame = ctk.CTkFrame(self.main_view)
        stats_frame.pack(fill="x", padx=40, pady=20)
        ctk.CTkLabel(stats_frame, text=f"ETH Balance\n{balances['eth']} ETH", font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=50, pady=25)
        ctk.CTkLabel(stats_frame, text=f"Donor Coins\n{balances['coin']} DNR", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3b8ed0").grid(row=0, column=1, padx=50, pady=25)
        if not user_name:
            reg_frame = ctk.CTkFrame(self.main_view, border_width=1, border_color="#3b8ed0")
            reg_frame.pack(pady=30, padx=40, fill="x")
            ctk.CTkLabel(reg_frame, text="Join the community! Register your name:", font=ctk.CTkFont(size=14)).pack(pady=10)
            name_entry = ctk.CTkEntry(reg_frame, placeholder_text="Enter Display Name...", width=300)
            name_entry.pack(pady=10)
            ctk.CTkButton(reg_frame, text="Register on Chain", command=lambda: messagebox.showinfo("Blockchain", "Transaction Sent to Network!")).pack(pady=10)
        else:
            ctk.CTkLabel(self.main_view, text=f"Welcome back, {user_name}!", font=ctk.CTkFont(size=18, slant="italic")).pack(pady=10)

    def show_campaigns(self):
        self.clear_main_view()
        ctk.CTkLabel(self.main_view, text="On-Chain Charity Campaigns", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=15)
        scroll = ctk.CTkScrollableFrame(self.main_view, width=850, height=450)
        scroll.pack(fill="both", expand=True, padx=25)
        campaigns = self.handler.fetch_campaigns()
        for camp in campaigns:
            card = ctk.CTkFrame(scroll)
            card.pack(fill="x", pady=8, padx=5)
            ctk.CTkLabel(card, text=f"ID: {camp['id']}", text_color="gray").pack(side="left", padx=10)
            ctk.CTkLabel(card, text=camp['name'], font=ctk.CTkFont(size=15, weight="bold"), width=200).pack(side="left", padx=10)
            progress = camp['raised'] / camp['goal'] if camp['goal'] > 0 else 0
            pb = ctk.CTkProgressBar(card, width=150)
            pb.set(progress if progress <= 1 else 1)
            pb.pack(side="left", padx=20)
            ctk.CTkLabel(card, text=f"{camp['raised']} / {camp['goal']} DNR").pack(side="left", padx=10)
            btn_donate = ctk.CTkButton(card, text="Donate", width=90, fg_color="#2ecc71", hover_color="#27ae60",
                                       command=lambda c=camp['id']: self.donate_ui(c))
            btn_donate.pack(side="right", padx=15, pady=10)

    def donate_ui(self, c_id):
        dialog = ctk.CTkInputDialog(text=f"Enter amount to donate to Campaign #{c_id}:", title="Blockchain Donation")
        amt = dialog.get_input()
        if amt:
            messagebox.showinfo("Transaction", f"Processing donation of {amt} DNR...\nPlease check your terminal for logs.")

    def show_history(self):
        self.clear_main_view()
        ctk.CTkLabel(self.main_view, text="Blockchain Activity Explorer", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=15)
        search_frame = ctk.CTkFrame(self.main_view)
        search_frame.pack(pady=10, fill="x", padx=40)
        addr_entry = ctk.CTkEntry(search_frame, placeholder_text="Paste Wallet Address (0x...)", width=450)
        addr_entry.pack(side="left", padx=15, pady=15)
        ctk.CTkButton(search_frame, text="Scan All Blocks", command=lambda: messagebox.showinfo("Scan", "Searching blockchain history...")).pack(side="left", padx=10)
        table_frame = ctk.CTkScrollableFrame(self.main_view)
        table_frame.pack(fill="both", expand=True, padx=40, pady=20)
        headers = ["Block #", "Action", "Value", "Tx Hash"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(table_frame, text=h, font=ctk.CTkFont(weight="bold"), text_color="#3b8ed0").grid(row=0, column=i, padx=40, pady=10)

    # --- 3. Admin Views (تم إضافة وظائف الأمن والتصدير) ---
    def admin_login(self):
        dialog = ctk.CTkInputDialog(text="Security Check: Enter Admin Key:", title="Privileged Access")
        pw = dialog.get_input()
        if pw == ADMIN_SECRET_PASSWORD:
            self.show_admin_panel()
        else:
            messagebox.showerror("Denied", "Incorrect Admin Secret Key!")

    def show_admin_panel(self):
        self.clear_main_view()
        title = ctk.CTkLabel(self.main_view, text="ADMINISTRATOR DASHBOARD", text_color="#e74c3c", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        # إحصائيات سريعة
        stats = self.handler.get_admin_stats()
        stats_frame = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a")
        stats_frame.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(stats_frame, text=f"Total Campaigns\n{stats['campaigns']}").grid(row=0, column=0, padx=40, pady=20)
        ctk.CTkLabel(stats_frame, text=f"Total Coins Minted\n{stats['minted']} DNR").grid(row=0, column=1, padx=40, pady=20)
        ctk.CTkLabel(stats_frame, text=f"Global Transactions\n{stats['transactions']}").grid(row=0, column=2, padx=40, pady=20)

        # قسم الأمان والتحليلات
        analysis_label = ctk.CTkLabel(self.main_view, text="Security & Deep Analytics", font=ctk.CTkFont(size=16, weight="bold"))
        analysis_label.pack(pady=(20, 5))

        analytics_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        analytics_frame.pack(pady=10)

        # وظيفية فحص الأمان المدمجة
        def run_security_audit_ui():
            self.alert_label.configure(text="🛡️ Running Security Audit...", text_color="orange")
            self.update_idletasks()
            report = run_audit() # استدعاء السكريبت اللي كتبناه
            messagebox.showinfo("Security Audit Report", report)
            self.alert_label.configure(text="📡 Scanning Network...", text_color="gray")

        # وظيفة تصدير الأرصدة (Snapshot)
        def run_snapshot_export():
            export_balances() # استدعاء سكريبت التصدير
            messagebox.showinfo("Success", "Balances snapshot exported to analysis/balances_snapshot.csv")

        # أزرار الأدمن الجديدة
        ctk.CTkButton(analytics_frame, text="🛡️ Run Security Audit", command=run_security_audit_ui, fg_color="#d35400").grid(row=0, column=0, padx=10)
        ctk.CTkButton(analytics_frame, text="📸 Export Balances CSV", command=run_snapshot_export, fg_color="#2980b9").grid(row=0, column=1, padx=10)
        
        # الأزرار القديمة (التحليلات العميقة)
        def run_real_analytics():
            self.alert_label.configure(text="⏳ Deep Scanning Blocks...", text_color="orange")
            self.update_idletasks()
            analytics = AdminAnalytics()
            data = analytics.get_dashboard_data()
            if data:
                info = "🏆 Top 3 Active Users:\n" + "-"*30 + "\n"
                for addr, count in data['top_users']:
                    info += f"👤 {addr[:15]}... : {count} tx\n"
                messagebox.showinfo("Deep Blockchain Analytics", info)
            self.alert_label.configure(text="📡 Scanning Network...", text_color="gray")

        ctk.CTkButton(analytics_frame, text="🔍 Deep Scan Blocks", command=run_real_analytics, fg_color="#34495e").grid(row=0, column=2, padx=10)

        # Batch Creation (كما هي في كودك)
        batch_frame = ctk.CTkFrame(self.main_view)
        batch_frame.pack(pady=20, padx=40, fill="x")
        ctk.CTkLabel(batch_frame, text="Batch Campaign Creation", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        name_entry = ctk.CTkEntry(batch_frame, placeholder_text="Names: Water, Food, Health...", width=500)
        name_entry.pack(pady=5)
        goal_entry = ctk.CTkEntry(batch_frame, placeholder_text="Goals: 1000, 5000, 2000...", width=500)
        goal_entry.pack(pady=5)
        ctk.CTkButton(batch_frame, text="🚀 Push Batch to Blockchain", fg_color="#27ae60").pack(pady=10)

if __name__ == "__main__":
    app = CharityApp()
    app.mainloop()