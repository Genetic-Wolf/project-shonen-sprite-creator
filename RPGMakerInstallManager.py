#!/usr/bin/env python3
import tkinter as tk,json,shutil,os,time
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SETTINGS=ROOT/"artist_settings.json"
MAP={"TV":"img/characters","FG":"img/faces","TVD":"img/characters","SV":"img/sv_actors","Variation":"generator/Variation"}
class I(tk.Tk):
 def __init__(self):
  super().__init__();self.title("Project Shonen — RPG Maker MZ Install Manager");self.geometry("850x570")
  try:self.cfg=json.load(open(SETTINGS,encoding="utf-8"))
  except:self.cfg={}
  self.project=tk.StringVar(value=self.cfg.get("rpgMakerProject",""));self.build()
 def build(self):
  ttk.Label(self,text="RPG Maker MZ Install Manager",font=("TkDefaultFont",16,"bold")).pack(anchor="w",padx=16,pady=(16,3))
  ttk.Label(self,text="Install completed Project Shonen graphics into your configured RPG Maker project. Existing files are backed up before replacement.",wraplength=800).pack(anchor="w",padx=16,pady=(0,12))
  f=ttk.Frame(self);f.pack(fill="x",padx=16)
  ttk.Entry(f,textvariable=self.project).pack(side="left",fill="x",expand=True);ttk.Button(f,text="Choose Project",command=self.choose).pack(side="left",padx=6)
  self.tree=ttk.Treeview(self,columns=("type","dest","status"),show="headings")
  for c,t,w in [("type","Output",120),("dest","RPG Maker Destination",300),("status","Ready Files",140)]:self.tree.heading(c,text=t);self.tree.column(c,width=w)
  self.tree.pack(fill="both",expand=True,padx=16,pady=14)
  b=ttk.Frame(self);b.pack(fill="x",padx=16,pady=(0,14))
  ttk.Button(b,text="Refresh",command=self.refresh).pack(side="left")
  ttk.Button(b,text="Open Project Graphics",command=self.openproject).pack(side="left",padx=6)
  ttk.Button(b,text="Install All Ready Graphics",command=self.install).pack(side="right")
  self.refresh()
 def choose(self):
  p=filedialog.askdirectory(title="Choose RPG Maker MZ project root")
  if not p:return
  q=Path(p)
  if not (q/"img").exists() or not (q/"data").exists():
   messagebox.showerror("Not an RPG Maker MZ project","Choose the project root containing both the img and data folders.");return
  self.project.set(p);self.cfg["rpgMakerProject"]=p;json.dump(self.cfg,open(SETTINGS,"w",encoding="utf-8"),indent=2);self.refresh()
 def refresh(self):
  for x in self.tree.get_children():self.tree.delete(x)
  for typ,dest in MAP.items():
   src=ROOT/"exports"/typ
   count=len(list(src.glob("*.png"))) if src.exists() else 0
   self.tree.insert("","end",values=(typ,dest,f"{count} PNG"))
 def install(self):
  q=Path(self.project.get())
  if not q.exists() or not (q/"img").exists():messagebox.showerror("Setup required","Choose your RPG Maker MZ project first.");return
  stamp=time.strftime("%Y%m%d-%H%M%S");backup=ROOT/"backups"/stamp;installed=0;backed=0
  for typ,dest in MAP.items():
   src=ROOT/"exports"/typ
   if not src.exists():continue
   dd=q/dest;dd.mkdir(parents=True,exist_ok=True)
   for p in src.glob("*.png"):
    target=dd/p.name
    if target.exists():
     bd=backup/dest;bd.mkdir(parents=True,exist_ok=True);shutil.copy2(target,bd/p.name);backed+=1
    shutil.copy2(p,target);installed+=1
  if installed:
   messagebox.showinfo("Installation complete",f"Installed {installed} graphics.\nBacked up {backed} replaced files.\n\nBackup:\n{backup if backed else 'No existing files were replaced.'}")
  else:messagebox.showinfo("Nothing to install","No ready PNG exports were found yet.")
 def openproject(self):
  q=Path(self.project.get())/"img"
  if q.exists():
   try:os.startfile(q)
   except:pass
I().mainloop()
