import binascii
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.exceptions import InvalidTag
from securecrypto import aes_utils


def show_result(label, value):
    result_label.config(text=label)
    result_entry.config(state="normal")
    result_entry.delete(0, tk.END)
    result_entry.insert(0, value)
    result_entry.config(state="readonly")


def encrypt():
    pw = password_entry.get()
    if not pw:
        messagebox.showerror("Lỗi", "Nhập mật khẩu trước khi mã hoá!")
        return
    file = filedialog.askopenfilename(title="Chọn file cần mã hoá")
    if not file:
        return
    key = aes_utils.encrypt_file_aes(file, pw)
    show_result("Key (base64) – lưu lại để giải mã:", key)
    messagebox.showinfo("Thành công", f"Đã mã hoá:\n{file}.enc")


def decrypt():
    key = password_entry.get()
    if not key:
        messagebox.showerror("Lỗi", "Nhập key base64 trước khi giải mã!")
        return
    file = filedialog.askopenfilename(title="Chọn file .enc cần giải mã",
                                      filetypes=[("Encrypted", "*.enc"),
                                                 ("All files", "*")])
    if not file:
        return
    try:
        out = aes_utils.decrypt_file_aes(file, key)
    except (InvalidTag, ValueError, binascii.Error):
        messagebox.showerror("Lỗi", "Sai key hoặc file bị hỏng!")
        return
    show_result("Output:", out)
    messagebox.showinfo("Thành công", f"Đã giải mã:\n{out}")


root = tk.Tk()
root.title("SecureCrypto GUI")
root.resizable(False, False)
frame = tk.Frame(root, padx=16, pady=12)
frame.pack()
tk.Label(frame, text="SecureCrypto – AES-256-GCM",
         font=("Arial", 14, "bold")).pack(pady=(0, 10))
tk.Label(frame, text="Mật khẩu (mã hoá) / Key base64 (giải mã):").pack(anchor="w")
password_entry = tk.Entry(frame, show="*", width=50)
password_entry.pack(pady=(2, 10))
btn_frame = tk.Frame(frame)
btn_frame.pack()
tk.Button(btn_frame, text="Encrypt", width=12, command=encrypt).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Decrypt", width=12, command=decrypt).grid(row=0, column=1, padx=5)
result_label = tk.Label(frame, text="Kết quả:")
result_label.pack(anchor="w", pady=(12, 2))
result_entry = tk.Entry(frame, width=50, state="readonly")
result_entry.pack()

if __name__ == "__main__":
    root.mainloop()
