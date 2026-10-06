#!/usr/bin/env python3
import tkinter as tk,json,os,shutil
from tkinter import ttk,messagebox
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class W(tk.Tk):
 def __init__(self):
  super().__init__();self.title("Project Shonen New Character Art Workspace");self.geometry("560x330")
  d=json.load(open(ROOT/"master_registry.json",encoding="utf-8"));self.ms=d["masters"];self.master=tk.StringVar(value=self.ms[0]["name"]);self.name=tk.StringVar(value="New Character")
  ttk.Label(self,text="Create Character Art Workspace",font=("TkDefaultFont",15,"bold")).pack(anchor="w",padx=16,pady=(16,4))
  ttk.Label(self,text="Creates one organized folder containing the approved/draft master references for every supported representation.").pack(anchor="w",padx=16,pady=(0,14))
  f=ttk.Frame(self);f.pack(fill="x",padx=16)
  ttk.Label(f,text="Character name").grid(row=0,column=0,sticky="e",padx=4,pady=6);ttk.Entry(f,textvariable=self.name,width=32).grid(row=0,column=1,pady=6)
  ttk.Label(f,text="Body master").grid(row=1,column=0,sticky="e",padx=4,pady=6);ttk.Combobox(f,textvariable=self.master,values=[x["name"] for x in self.ms],state="readonly",width=29).grid(row=1,column=1,pady=6)
  ttk.Button(self,text="Create Complete Art Workspace",command=self.go).pack(pady=20)
 def go(self):
  m=next(x for x in self.ms if x["name"]==self.master.get());safe="".join(c if c.isalnum() or c in "_-" else "_" for c in self.name.get().strip()) or "Character"
  d=ROOT/"artist_workspace"/"Characters"/safe;d.mkdir(parents=True,exist_ok=True)
  manifest={"character":self.name.get(),"masterId":m["id"],"masterKey":m["key"],"outputs":{}}
  for k,o in m["outputs"].items():
   od=d/k;od.mkdir(exist_ok=True);src=ROOT/o["base"]
   if src.exists():shutil.copy2(src,od/f'{k}_MASTER_REFERENCE_{o["status"].upper()}.png')
   (od/"STATUS.txt").write_text(f'{k}\nMaster status: {o["status"]}\nLocked: {o["locked"]}\nCanvas: {o["size"][0]}x{o["size"][1]}\n',encoding="utf-8")
   manifest["outputs"][k]={"masterStatus":o["status"],"locked":o["locked"]}
  (d/"character_art_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
  (d/"READ_ME_FIRST.txt").write_text("This folder groups all visual representations for one character. APPROVED+LOCKED masters are safe for production. DRAFT/REVISION masters are reference-only until approved in Master Template Manager.\n",encoding="utf-8")
  try:os.startfile(d)
  except:pass
  messagebox.showinfo("Workspace created",f"Complete art workspace created for {self.name.get()}.")
W().mainloop()
