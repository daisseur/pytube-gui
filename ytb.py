import tkinter as tk
from tkinter import filedialog, Button, Label, Entry, StringVar, Frame, Checkbutton, Menu
from pytube import YouTube
from os import getcwd, remove, name
from os.path import basename, exists
from threading import Thread, Lock
from pyperclip import paste
from time import sleep
from ast import literal_eval

class App:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("Téléchargement vidéo Youtube")
        self.app.geometry("740x740")
        # self.app.iconphoto(False, tk.PhotoImage(file='.ytb.ico'))

        self.lock = Lock()

        self.status_var = StringVar()
        self.url = ""
        self.download_dir = getcwd()
        self.check_var = 0
        self.save_var = 0
        self.urls = []
        self.historique = literal_eval(open(".pytube-history.txt", 'r').read()) if exists(".pytube-history.txt") else {}
        self.status_var.set(''.join(i for i in [self.historique[i] for i in self.historique.keys()]))
        self.threads = []
        self.lock = Lock()

        self.menubar = Menu(self.app)
        self.app.config(menu=self.menubar)

        self.fichier = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Fichier", menu=self.fichier)
        self.fichier.add_command(label="Changer le répertoire", command=self.newdir)
        self.fichier.add_command(label="Depuis le presse-papier", command=self.copy)
        self._historique = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Historique", menu=self._historique)
        self._historique.add_command(label="Enregistrer", command=self.save)
        self._historique.add_checkbutton(label="Enregistrement en continue", command=self.start_save)

        self.folder_label = Label(self.app, text="Répertoire Actuel:" + " " + self.download_dir)
        self.folder_label.pack()
        Label(self.app, text="Entrer l'url de la vidéo Youtube :").pack()
        self.url_entry = Entry(self.app, width=70)
        self.url_entry.pack()
        Button(self.app, text="Télécharger", command=self.download_video).pack()
        Label(self.app, textvariable=self.status_var).pack()
        self.app.mainloop()

    def save(self):
        open(".pytube-history.txt", 'w').write(str(self.historique))

    def start_save(self):
        if self.save_var == 0:
            self.save_var = 1
            Thread(target=self.save_while).start()
        else:
            self.save_var = 0

    def save_while(self):
        print("started")
        save = ''
        while True:
            if self.save_var == 0:
                print("ended")
                break
            if save != self.historique:
                save = self.historique
                open(".pytube-history.txt", 'w').write(str(self.historique))
            sleep(1)


    def copy(self):
        if self.check_var == 0:
            self.check_var = 1
            Thread(target=self.copy_while).start()
        else:
            self.check_var = 0

    def copy_while(self):
        while True:
            clip = paste()
            if "watch?v=" in clip and len(clip) < 30 and clip not in self.urls:
                print(clip)
                self.urls.append(clip)
                self.url = clip
                self.download_video(url=True)
                sleep(1)

    def delete(self, widget, path):
        remove(path)
        widget.destroy()

    def nrow(self, status, path):
        new = Frame(self.app, highlightbackground="blue", highlightthickness=2)
        main_ = Frame(new, width=200)
        Label(main_, text=basename(path)).pack()
        Label(new, text=status, font="green").grid(row=0, column=0, padx=35)
        Label(new, text=path.replace(basename(path), ''), font="blue").grid(row=0, column=1, padx=35)
        Button(new, text="Effacer", command=lambda: self.delete(new, path)).grid(row=0, column=2, padx=35)
        main_.grid(row=1, column=1)
        new.grid_columnconfigure(3)
        new.pack()

    def newdir(self):
        self.download_dir = filedialog.askdirectory()
        self.folder_label.config(text="Répertoire Actuel:" + " " + self.download_dir)
        print("New dir on", self.download_dir)

    def download_(self, url):
        path = self.download_dir
        yt = YouTube(url)
        video = yt.streams.filter(file_extension='mp4', resolution='720p').first()
        video.download(self.download_dir)
        self.historique[url] = ''
        self.nrow("Téléchargée", path + str("\\" if name == "nt" else "/") + video.title + ".mp4")
        self.status_var.set(''.join(i for i in [self.historique[i] for i in self.historique.keys()]))

    def download_video(self, url=False):
        if not url:
            self.url = self.url_entry.get()
            self.url_entry.clipboard_clear()
        print("downloading...", self.url)
        self.historique[self.url] = "En cours - " + self.url + "\n"
        self.status_var.set(''.join(i for i in [self.historique[i] for i in self.historique.keys()]))
        self.threads.append(Thread(target=self.download_, args=(self.url,)))
        self.threads[-1].start()
        print("Thread started")

App()




