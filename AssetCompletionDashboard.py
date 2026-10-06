#!/usr/bin/env python3
import tkinter as tk, json
from tkinter import ttk
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class D(tk.Tk):
 def __init__(self):
  super().__init__();self.title("Project Shonen Asset Completion Dashboard v0.5.0");self.geometry("900x560")
  ttk.Label(self,text="Multi-Output Asset Completion",font=("TkDefaultFont",15,"bold")).pack(anchor="w",padx=12,pady=(12,4))
  ttk.Label(self,text="One logical component can progressively receive TV, Face, TVD, SV and Variation artwork.").pack(anchor="w",padx=12)
  self.t=ttk.Treeview(self,columns=("body","tv","fg","tvd","sv","var"),show="headings")
  for k,w in [("body",140),("tv",80),("fg",80),("tvd",80),("sv",80),("var",90)]:
   self.t.heading(k,text=k.upper());self.t.column(k,width=w,anchor="center")
  self.t["displaycolumns"]=("body","tv","fg","tvd","sv","var");self.t.pack(fill="both",expand=True,padx=12,pady=12)
  self.refresh()
 def refresh(self):
  for x in self.t.get_children():self.t.delete(x)
  lib=ROOT/"library.json"
  if not lib.exists():return
  data=json.load(open(lib,encoding="utf-8"))
  for a in data.get("assets",[]):
   o=a.get("outputs",{})
   st=lambda k:"✓" if o.get(k,{}).get("status")=="complete" else "—"
   self.t.insert("","end",text=a.get("name",""),values=(a.get("body",""),st("TV"),st("FG"),st("TVD"),st("SV"),st("Variation")))
D().mainloop()
