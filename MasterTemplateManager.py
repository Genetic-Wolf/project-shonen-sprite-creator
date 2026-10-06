#!/usr/bin/env python3
import tkinter as tk,json,os,shutil
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from PIL import Image,ImageTk
ROOT=Path(__file__).resolve().parent
REG=ROOT/"master_registry.json"
OUTS=["TV","FG","TVD","SV","Variation"]
class M(tk.Tk):
 def __init__(self):
  super().__init__();self.title("Project Shonen Master Template Manager v0.7.0");self.geometry("1050x650");self.data=json.load(open(REG,encoding="utf-8"));self.cur=None;self.pic=None;self.build();self.fill()
 def build(self):
  ttk.Label(self,text="Master Template Manager",font=("TkDefaultFont",16,"bold")).pack(anchor="w",padx=12,pady=(12,2))
  ttk.Label(self,text="Approve and lock canonical body artwork before bulk component production. Locked masters protect the library from accidental geometry changes.").pack(anchor="w",padx=12,pady=(0,10))
  p=ttk.Panedwindow(self,orient="horizontal");p.pack(fill="both",expand=True,padx=12,pady=(0,12))
  l=ttk.Frame(p,padding=8);r=ttk.Frame(p,padding=8);p.add(l,weight=2);p.add(r,weight=5)
  self.list=tk.Listbox(l);self.list.pack(fill="both",expand=True);self.list.bind("<<ListboxSelect>>",self.sel)
  ttk.Button(l,text="+ Register New Body Master",command=self.add).pack(fill="x",pady=(8,2))
  self.name=tk.StringVar();ttk.Label(r,textvariable=self.name,font=("TkDefaultFont",14,"bold")).pack(anchor="w")
  self.tree=ttk.Treeview(r,columns=("status","locked","size"),show="headings",height=7)
  for c,t,w in [("status","Status",110),("locked","Locked",90),("size","Canvas",120)]:self.tree.heading(c,text=t);self.tree.column(c,width=w,anchor="center")
  self.tree.pack(fill="x",pady=8);self.tree.bind("<<TreeviewSelect>>",lambda e:self.preview())
  self.canvas=tk.Canvas(r,width=420,height=300,bg="#30343b",highlightthickness=0);self.canvas.pack(fill="both",expand=True,pady=6)
  b=ttk.Frame(r);b.pack(fill="x")
  ttk.Button(b,text="Replace Draft / Base Artwork",command=self.replace).pack(side="left",padx=2)
  ttk.Button(b,text="Approve Selected Output",command=self.approve).pack(side="left",padx=2)
  ttk.Button(b,text="Unlock for Revision",command=self.unlock).pack(side="left",padx=2)
  ttk.Button(b,text="Open Master Folder",command=self.folder).pack(side="right",padx=2)
 def fill(self):
  self.list.delete(0,"end")
  for x in self.data["masters"]:self.list.insert("end",x["name"])
 def master(self):
  if self.cur is None:return None
  return self.data["masters"][self.cur]
 def sel(self,e=None):
  s=self.list.curselection()
  if not s:return
  self.cur=s[0];m=self.master();self.name.set(f'{m["name"]}  •  {m["id"]}')
  for x in self.tree.get_children():self.tree.delete(x)
  for k in OUTS:
   o=m["outputs"][k];self.tree.insert("","end",iid=k,values=(o["status"],"YES" if o["locked"] else "NO",f'{o["size"][0]}×{o["size"][1]}'))
  self.tree.selection_set("TV");self.preview()
 def preview(self):
  m=self.master();s=self.tree.selection()
  if not m or not s:return
  p=ROOT/m["outputs"][s[0]]["base"]
  self.canvas.delete("all")
  if p.exists():
   im=Image.open(p).convert("RGBA");bg=Image.new("RGBA",im.size,(55,59,66,255));bg.alpha_composite(im);bg.thumbnail((500,330),Image.Resampling.NEAREST);self.pic=ImageTk.PhotoImage(bg);self.canvas.create_image(260,165,image=self.pic)
 def replace(self):
  m=self.master();s=self.tree.selection()
  if not m or not s:return
  k=s[0];o=m["outputs"][k]
  if o["locked"]:
   messagebox.showerror("Master locked","Unlock this output before replacing canonical artwork.");return
  p=filedialog.askopenfilename(filetypes=[("PNG","*.png")])
  if not p:return
  im=Image.open(p).convert("RGBA")
  if list(im.size)!=o["size"]:
   messagebox.showerror("Wrong dimensions",f'{k} master must be {o["size"][0]}×{o["size"][1]}.');return
  dst=ROOT/o["base"];dst.parent.mkdir(parents=True,exist_ok=True);im.save(dst);o["status"]="review";self.save();self.sel()
 def approve(self):
  m=self.master();s=self.tree.selection()
  if not m or not s:return
  k=s[0];o=m["outputs"][k]
  if o["status"]=="draft":
   if not messagebox.askyesno("Approve draft?","This output is still marked DRAFT. Approving it locks this exact geometry for component production. Continue only if the artist has reviewed the base artwork."):return
  o["status"]="approved";o["locked"]=True;self.save();self.sel()
 def unlock(self):
  m=self.master();s=self.tree.selection()
  if not m or not s:return
  if not messagebox.askyesno("Unlock canonical master?","Changing an approved master can misalign every existing component built for it. Unlock only for an intentional master revision."):return
  o=m["outputs"][s[0]];o["locked"]=False;o["status"]="revision";self.save();self.sel()
 def add(self):
  
  import subprocess,sys
  subprocess.Popen([sys.executable,str(ROOT/"NewBodyMasterWizard.py")])
 def folder(self):
  m=self.master()
  if not m:return
  p=ROOT/"masters"/m["key"];p.mkdir(parents=True,exist_ok=True)
  try:os.startfile(p)
  except:pass
 def save(self):json.dump(self.data,open(REG,"w",encoding="utf-8"),indent=2)
M().mainloop()
