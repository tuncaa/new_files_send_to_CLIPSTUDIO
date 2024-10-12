import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from datetime import datetime

class FileCreatedHandler(FileSystemEventHandler):
    def __init__(self, app_path, log_callback):
        self.app_path = app_path
        self.log_callback = log_callback

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            if file_path.endswith('.tmp'):
                return  # .tmpファイルは無視する(web系からの保存で一時生成される場合があるため)
            self.log_callback(f"新しいファイルが作成されました: {file_path}")
            self.open_file_with_app(file_path)

    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path
            if not file_path.endswith('.png'):
                return  # .pngファイル以外は無視する
            self.log_callback(f"ファイルが変更されました: {file_path}")

    def on_moved(self, event):
        if not event.is_directory:
            old_path = event.src_path
            new_path = event.dest_path
            if not new_path.endswith('.png'):
                return  # .pngファイル以外は無視する
            self.log_callback(f"ファイルがリネームされました: {old_path} -> {new_path}")
            self.open_file_with_app(new_path)

    def open_file_with_app(self, file_path):
        try:
            subprocess.run([self.app_path, file_path], check=True)
            self.log_callback(f"{file_path} を {self.app_path} で開きました。")
        except Exception as e:
            self.log_callback(f"エラー: ファイルを開く際にエラーが発生しました: {str(e)}")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ファイル監視アプリ")
        self.geometry("500x400")
        self.app_path = r"C:\Program Files\CELSYS\CLIP STUDIO 1.5\CLIP STUDIO PAINT\CLIPStudioPaint.exe"#エディタのデフォルト設定
        self.folder_to_watch = r"H:\SDXL\EasySdxlWebUi\save" #監視フォルダのデフォルト設定

        # アプリケーションパスのラベルとエントリー
        self.label_app = tk.Label(self, text="アプリケーションのパスを入力:")
        self.label_app.pack(pady=5)

        self.app_entry = tk.Entry(self, width=60)
        self.app_entry.insert(0, self.app_path)
        self.app_entry.pack(pady=5)

        # 監視フォルダのラベルとエントリー
        self.label_folder = tk.Label(self, text="監視するフォルダを入力:")
        self.label_folder.pack(pady=5)

        self.folder_entry = tk.Entry(self, width=60)
        self.folder_entry.insert(0, self.folder_to_watch)
        self.folder_entry.pack(pady=5)

        self.start_button = tk.Button(self, text="監視開始", command=self.start_monitoring)
        self.start_button.pack(pady=20)

        # 監視ステータスラベル
        self.status_label = tk.Label(self, text="監視していません", fg="red")
        self.status_label.pack(pady=10)

        # ログ表示用のテキストボックス
        self.log_text = tk.Text(self, height=10, width=60)
        self.log_text.pack(pady=10)
        self.log_text.config(state='disabled')  # 初期状態は編集不可

    def log_message(self, message):
        # 現在の日時と時刻を取得してフォーマット
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_message = f"{timestamp} {message}"

        # テキストボックスにメッセージを追加
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, full_message + "\n")
        self.log_text.see(tk.END)  # 常に最新のメッセージを表示
        self.log_text.config(state='disabled')

    def start_monitoring(self):
        self.app_path = self.app_entry.get()
        self.folder_to_watch = self.folder_entry.get()

        if not os.path.isfile(self.app_path):
            self.log_message("エラー: 指定したアプリケーションが見つかりません。")
            return

        if not os.path.exists(self.folder_to_watch):
            os.makedirs(self.folder_to_watch)

        event_handler = FileCreatedHandler(self.app_path, self.log_message)
        observer = Observer()
        observer.schedule(event_handler, self.folder_to_watch, recursive=False)
        observer_thread = threading.Thread(target=observer.start)
        observer_thread.daemon = True
        observer_thread.start()

        # 監視ステータスを「監視中」に変更
        self.status_label.config(text="監視中", fg="green")
        self.log_message(f"{self.folder_to_watch} の監視を開始しました。")

if __name__ == "__main__":
    app = App()
    app.mainloop()
