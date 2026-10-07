import tkinter as tk
from tkinter import ttk,messagebox,filedialog
from pathlib import Path
import app_paths
from PIL import Image,ImageTk
import json,shutil,time,re
import asset_package
ROOT=app_paths.DATA_ROOT
RESOURCE_ROOT=app_paths.RESOURCE_ROOT
app_paths.bootstrap()
LIB=ROOT/"library.json";REG=ROOT/"master_registry.json";SET=ROOT/"artist_settings.json"
DEST={"TV":"img/characters","FG":"img/faces","TVD":"img/characters","SV":"img/sv_actors","Variation":"generator/Variation"}
CUSTOMIZATION_FIELDS=[
 ("Face",["Face / Shape","Face / Eyes","Face / Eyebrows","Face / Nose","Face / Mouth","Face / Ears","Face / Facial Hair","Face / Markings","Face / Dōjutsu","Face / Scars","Face / Tattoos","Face / Clan Markings"]),
 ("Hair",["Hair / Rear","Hair / Main","Hair / Front","Hair / Ponytail","Hair / Accessories"]),
 ("Clothing",["Clothing / Undershirt","Clothing / Shirt","Clothing / Pants","Clothing / Skirt","Clothing / Belt","Clothing / Gloves","Clothing / Shoes","Clothing"]),
 ("Armor",["Armor / Chest","Armor / Shoulders","Armor / Arms","Armor / Legs","Armor"]),
 ("Shinobi",["Shinobi / Forehead Protector","Shinobi / Village Symbol","Shinobi / Tool Pouch","Shinobi / Kunai Holster","Shinobi / Scrolls"]),
 ("Outerwear",["Outerwear / Vest","Outerwear / Coat","Outerwear / Robe","Outerwear / Cloak"]),
 ("Accessories",["Accessories / Head","Accessories / Head A","Accessories / Head B","Accessories / Face","Accessories / Neck","Accessories / Hands","Accessories / Back"]),
 ("Weapons",["Weapons / Back","Weapons / Left Hip","Weapons / Right Hip","Weapons / Left Hand","Weapons / Right Hand"]),
 ("Special",["Special / Tail","Special / Wings","Special / Beast Ears","Special / Clan Features","Special / Transformation Features"])
]

def load(p,d):
 try:return json.load(open(p,encoding="utf-8"))
 except:return d
def save(p,d):json.dump(d,open(p,"w",encoding="utf-8"),indent=2)
class CharacterBuilder(ttk.Frame):
 def __init__(self,parent):
  super().__init__(parent);self.lib=load(LIB,{"assets":[]});self.reg=load(REG,{"masters":[]});self.selected=[];self.photo=None;self.preview_out=tk.StringVar(value="TV");self.category=tk.StringVar(value="All");self.build()
 def build(self):
  top=ttk.Frame(self);top.pack(fill="x")
  ttk.Label(top,text="Character name").pack(side="left");self.name=tk.StringVar(value="New Character");ttk.Entry(top,textvariable=self.name,width=24).pack(side="left",padx=6)
  masters=[m["name"] for m in self.reg["masters"]];self.master_name=tk.StringVar(value=masters[0] if masters else "");ttk.Label(top,text="Body master").pack(side="left",padx=(12,0))
  cb=ttk.Combobox(top,textvariable=self.master_name,values=masters,state="readonly",width=22);cb.pack(side="left",padx=6);cb.bind("<<ComboboxSelected>>",self.on_master_changed)
  self.search=tk.StringVar();ttk.Label(top,text="Search").pack(side="left",padx=(12,0));e=ttk.Entry(top,textvariable=self.search,width=18);e.pack(side="left",padx=5);self.search.trace_add("write",lambda *_:self.refresh())
  ttk.Label(top,text="Category").pack(side="left",padx=(10,0));cats=["All"]+sorted({a.get("category","Other") for a in self.lib["assets"]});cc=ttk.Combobox(top,textvariable=self.category,values=cats,state="readonly",width=16);cc.pack(side="left",padx=4);cc.bind("<<ComboboxSelected>>",lambda e:self.refresh())
  pan=ttk.Panedwindow(self,orient="horizontal");pan.pack(fill="both",expand=True,pady=10)
  left=ttk.Frame(pan);mid=ttk.Frame(pan);right=ttk.Frame(pan);pan.add(left,weight=3);pan.add(mid,weight=2);pan.add(right,weight=3)
  ttk.Label(left,text="Customization",font=("TkDefaultFont",11,"bold")).pack(anchor="w")
  slots=ttk.Frame(left);slots.pack(fill="x",pady=(2,6))
  for group,fields in CUSTOMIZATION_FIELDS:
   ttk.Button(slots,text=group,command=lambda fs=fields:self.show_fields(fs)).pack(side="left",padx=1,pady=1)
  self.field_hint=tk.StringVar(value="All customization fields are available. Choose a group above or use Category.")
  ttk.Label(left,textvariable=self.field_hint,wraplength=430).pack(anchor="w",pady=(0,5))
  ttk.Label(left,text="Compatible Pieces",font=("TkDefaultFont",10,"bold")).pack(anchor="w")
  self.countinfo=tk.StringVar(value="0 compatible pieces");ttk.Label(left,textvariable=self.countinfo).pack(anchor="w")
  self.tree=ttk.Treeview(left,columns=("cat","status"),show="tree headings");self.tree.heading("#0",text="Piece");self.tree.heading("cat",text="Category");self.tree.heading("status",text="TV");self.tree.pack(fill="both",expand=True);self.tree.bind("<Double-1>",self.add);self.tree.bind("<<TreeviewSelect>>",self.piece_preview)
  self.pieceinfo=tk.StringVar(value="Select a piece to preview it.");ttk.Label(left,textvariable=self.pieceinfo,wraplength=430).pack(anchor="w",pady=4)
  ttk.Label(mid,text="Selected Components",font=("TkDefaultFont",11,"bold")).pack(anchor="w")
  ttk.Label(mid,text="The base body is always present. Hair, face, clothing and other parts start empty.",wraplength=250).pack(anchor="w",pady=(0,5))
  self.sel=tk.Listbox(mid);self.sel.pack(fill="both",expand=True)
  b=ttk.Frame(mid);b.pack(fill="x",pady=5)
  ttk.Button(b,text="↑",width=4,command=lambda:self.move(-1)).pack(side="left");ttk.Button(b,text="↓",width=4,command=lambda:self.move(1)).pack(side="left",padx=3);ttk.Button(b,text="Remove / None",command=self.remove).pack(side="left");ttk.Button(b,text="Clear All",command=self.clear_components).pack(side="left",padx=3)
  ph=ttk.Frame(right);ph.pack(fill="x")
  ttk.Label(ph,text="Live Preview",font=("TkDefaultFont",11,"bold")).pack(side="left")
  ttk.Combobox(ph,textvariable=self.preview_out,values=["TV","FG","TVD","SV"],state="readonly",width=10).pack(side="right")
  self.preview_out.trace_add("write",lambda *_:self.preview())
  self.canvas=tk.Canvas(right,width=360,height=420,bg="#30343b",highlightthickness=0);self.canvas.pack(fill="both",expand=True)
  self.baseinfo=tk.StringVar(value="Base Body");ttk.Label(right,textvariable=self.baseinfo,font=("TkDefaultFont",10,"bold")).pack(anchor="w",pady=(4,0))
  self.readiness=tk.StringVar();ttk.Label(right,textvariable=self.readiness,wraplength=330).pack(anchor="w",pady=5)
  x=ttk.Frame(right);x.pack(fill="x")
  ttk.Button(x,text="Export Selected Output",command=self.export).pack(side="left")
  ttk.Button(x,text="Export All Ready Outputs",command=self.export_all).pack(side="left",padx=5)
  ttk.Button(x,text="Refresh Preview",command=self.preview).pack(side="left",padx=5)
  y=ttk.Frame(right);y.pack(fill="x",pady=(5,0))
  ttk.Button(y,text="Save Character Project",command=self.save_project).pack(side="left")
  ttk.Button(y,text="Open Character Project",command=self.open_project).pack(side="left",padx=5)
  self.refresh()
 def show_fields(self,fields):
  available={a.get("category","Other") for a in self.lib.get("assets",[])}
  choices=[x for x in fields if x in available]
  if choices:
   self.category.set(choices[0]);self.field_hint.set("Fields: "+", ".join(fields)+". Use Category to select any individual field.")
  else:
   self.category.set("All");self.field_hint.set("These fields are accessible but no compatible artwork has been imported/created for them yet: "+", ".join(fields))
  self.refresh()
 def clear_components(self):
  self.selected=[];self.renderstack();self.preview()
 def currentmaster(self):return next((m for m in self.reg["masters"] if m["name"]==self.master_name.get()),None)
 def on_master_changed(self,event=None):
  # A body change invalidates layers selected for the previous geometry.
  self.selected=[]
  if hasattr(self,"sel"): self.renderstack()
  if hasattr(self,"baseinfo"):
   m=self.currentmaster();self.baseinfo.set("Base Body: "+(m.get("name","None") if m else "None")+" — no cosmetics selected")
  if hasattr(self,"tree") and hasattr(self,"search"): self.refresh()
 def compatible(self,a,m):return a.get("body")==m.get("key") or a.get("masterId")==m.get("id")
 def refresh(self):
  for x in self.tree.get_children():self.tree.delete(x)
  m=self.currentmaster()
  if not m:return
  q=self.search.get().lower().strip()
  shown=0
  for i,a in enumerate(self.lib["assets"]):
   if self.compatible(a,m) and (self.category.get()=="All" or a.get("category","Other")==self.category.get()) and (not q or q in a.get("name","").lower() or q in a.get("category","").lower()):
    o=a.get("outputs",{}).get("TV",{});self.tree.insert("","end",iid=str(i),text=a.get("name",a["id"]),values=(a.get("category",""),"✓" if o.get("status")=="complete" else "missing"));shown+=1
  self.countinfo.set(f"{shown} compatible piece"+("" if shown==1 else "s")+" shown" if shown else "No compatible artwork in this field yet — create or import a reusable piece.")\n  self.preview()
 def piece_preview(self,event=None):
  sel=self.tree.selection()
  if not sel:return
  a=self.lib["assets"][int(sel[0])];outs=[k for k,v in a.get("outputs",{}).items() if v.get("status")=="complete"]
  self.pieceinfo.set(a.get("name",a.get("id",""))+" • "+a.get("category","Other")+" • outputs: "+(", ".join(outs) if outs else "none"))
 def add(self,e=None):
  s=self.tree.selection()
  if not s:return
  i=int(s[0]);a=self.lib["assets"][i];cat=a.get("category","Other")
  # One default piece per exact category; advanced layering can still contain distinct categories.
  self.selected=[x for x in self.selected if self.lib["assets"][x].get("category","Other")!=cat]
  self.selected.append(i);self.renderstack();self.preview()
 def renderstack(self):
  self.sel.delete(0,"end")
  for i in self.selected:
   a=self.lib["assets"][i];self.sel.insert("end",f'{a.get("category","Other")}: {a["name"]}')
 def move(self,d):
  s=self.sel.curselection()
  if not s:return
  i=s[0];j=i+d
  if j<0 or j>=len(self.selected):return
  self.selected[i],self.selected[j]=self.selected[j],self.selected[i];self.renderstack();self.sel.selection_set(j);self.preview()
 def remove(self):
  s=self.sel.curselection()
  if not s:return
  self.selected.pop(s[0]);self.renderstack();self.preview()
 def composite(self,out="TV"):
  m=self.currentmaster()
  if not m:return None,[]
  mo=m["outputs"].get(out,{})
  base=app_paths.resolve(mo.get("base",""))
  if not base.exists():return None,[f"Body master {out} artwork is missing"]
  canvas=Image.open(base).convert("RGBA");missing=[]
  for i in self.selected:
   a=self.lib["assets"][i];o=a.get("outputs",{}).get(out,{})
   if o.get("status")!="complete" or not o.get("path"):missing.append(f'{a["name"]} ({out})');continue
   paths=o.get("paths") or ([o.get("path")] if o.get("path") else [])
   for rel in paths:
    q=app_paths.resolve(rel)
    if q.exists():
     im=Image.open(q).convert("RGBA")
     if im.size==canvas.size:canvas.alpha_composite(im)
     else:missing.append(f'{a["name"]} ({out} wrong size)')
    else:missing.append(f'{a["name"]} ({out} file missing)')
  return canvas,missing
 def master_ready(self,out):
  m=self.currentmaster()
  if not m:return False,"No body master selected"
  o=m["outputs"].get(out,{})
  if o.get("status")=="reference" and o.get("locked"):return True,""
  if o.get("status")!="approved" or not o.get("locked"):return False,f"{out} body master is not Approved + Locked"
  return True,""
 def preview(self):
  out=self.preview_out.get();im,missing=self.composite(out);self.canvas.delete("all")
  if im is None:self.readiness.set(f"{out} preview unavailable.");return
  if out=="TV":frame=im.crop((48,0,96,48))
  elif out=="TVD":frame=im.crop((48,0,96,48)) if im.width>=96 else im
  elif out=="SV":frame=im.crop((0,0,64,64))
  else:frame=im
  frame.thumbnail((320,320),Image.Resampling.NEAREST)
  scale=max(1,min(5,300//max(frame.size)));frame=frame.resize((frame.width*scale,frame.height*scale),Image.Resampling.NEAREST)
  self.photo=ImageTk.PhotoImage(frame);self.canvas.create_image(180,185,image=self.photo)
  ok,why=self.master_ready(out)
  problems=list(missing)
  if not ok:problems.insert(0,why)
  self.readiness.set(f"{out}: production ready." if not problems else "Not ready: "+", ".join(problems))
 def save_project(self):
  m=self.currentmaster()
  if not m:return
  safe=re.sub(r'[^A-Za-z0-9_-]+','_',self.name.get().strip()) or "Character"
  d=ROOT/"character_projects";d.mkdir(parents=True,exist_ok=True);path=d/f"{safe}.pscharacter.json"
  save(path,{"schemaVersion":1,"name":self.name.get().strip(),"masterId":m["id"],"masterKey":m["key"],"layers":[self.lib["assets"][i]["id"] for i in self.selected]})
  messagebox.showinfo("Character project saved",f"Saved {path.name}.")
 def export_package(self):
  lib=load(LIB,{"assets":[]});eligible=[a for a in lib.get("assets",[]) if not str(a.get("source","")).startswith("RPG Maker MZ")]
  if not eligible:messagebox.showinfo("No custom pieces","Create or import a Project Shonen reusable piece first.");return
  win=tk.Toplevel(self);win.title("Export Reusable Piece");win.transient(self.winfo_toplevel());v=tk.StringVar(value=eligible[0].get("name",""))
  ttk.Label(win,text="Choose a custom reusable piece").pack(anchor="w",padx=12,pady=(12,4));cb=ttk.Combobox(win,textvariable=v,values=[a.get("name","") for a in eligible],state="readonly",width=55);cb.pack(padx=12,pady=4)
  def go():
   a=next(x for x in eligible if x.get("name")==v.get());p=filedialog.asksaveasfilename(defaultextension=".psasset",filetypes=[("Project Shonen Asset","*.psasset")],initialfile=re.sub(r'[^A-Za-z0-9_-]+','_',a.get("name","Asset"))+".psasset")
   if not p:return
   try:r=asset_package.export_piece(a["id"],p);win.destroy();messagebox.showinfo("Package exported",f"{r['name']} exported with {r['files']} artwork files.")
   except Exception as e:messagebox.showerror("Export failed",str(e))
  ttk.Button(win,text="Export Package",command=go).pack(padx=12,pady=12)
 def import_package(self):
  p=filedialog.askopenfilename(title="Import Project Shonen reusable piece",filetypes=[("Project Shonen Asset","*.psasset"),("All files","*.*")])
  if not p:return
  try:
   m=asset_package.inspect_package(p);a=m["asset"];lib=load(LIB,{"assets":[]});collision=any(x.get("id")==a.get("id") for x in lib.get("assets",[]));replace=False
   if collision:replace=messagebox.askyesno("Asset already exists",f'{a.get("name")} ({a.get("id")}) already exists. Replace its registered package artwork?')
   if collision and not replace:return
   r=asset_package.import_piece(p,replace=replace);self.status.set(f"Imported portable asset: {r['name']}.");messagebox.showinfo("Package imported",self.status.get())
  except Exception as e:messagebox.showerror("Import failed",str(e))
 def open_project(self):
  d=ROOT/"character_projects";d.mkdir(parents=True,exist_ok=True)
  p=filedialog.askopenfilename(initialdir=d,filetypes=[("Project Shonen Character","*.pscharacter.json"),("JSON","*.json")])
  if not p:return
  data=load(Path(p),{});m=next((m for m in self.reg["masters"] if m.get("id")==data.get("masterId") or m.get("key")==data.get("masterKey")),None)
  if not m:messagebox.showerror("Missing body master","This character references a body master that is not installed.");return
  self.master_name.set(m["name"]);self.name.set(data.get("name","Character"));idx={a.get("id"):i for i,a in enumerate(self.lib["assets"])};ids=data.get("layers",[])
  missing=[x for x in ids if x not in idx];self.selected=[idx[x] for x in ids if x in idx];self.renderstack();self.refresh();self.preview()
  if missing:messagebox.showwarning("Missing pieces","Character opened, but some saved pieces are no longer installed.")
 def export_one(self,out,quiet=False):
  ok,why=self.master_ready(out)
  if not ok:
   if not quiet:messagebox.showerror("Master not production-ready",why+"\
\
Approve and lock this master output on the Body Masters page first.")
   return False
  canvas,missing=self.composite(out)
  if canvas is None or missing:
   if not quiet:messagebox.showerror("Character output incomplete","Complete these assets first:\
\
"+"\
".join(missing))
   return False
  safe=re.sub(r'[^A-Za-z0-9_-]+','_',self.name.get().strip()) or "Character";d=ROOT/"exports"/out;d.mkdir(parents=True,exist_ok=True)
  if out=="TV":fn=f"${safe}.png"
  elif out=="FG":fn=f"{safe}_Face.png"
  elif out=="TVD":fn=f"${safe}_Downed.png"
  else:fn=f"{safe}_SV.png"
  canvas.save(d/fn);return True
 def export(self):
  out=self.preview_out.get()
  if self.export_one(out):messagebox.showinfo("Output ready",f"{out} artwork was exported successfully.\
\
Use the RPG Maker MZ page to install it safely.")
 def export_all(self):
  ready=[];blocked=[]
  for out in ("TV","FG","TVD","SV"):
   if self.export_one(out,quiet=True):ready.append(out)
   else:blocked.append(out)
  messagebox.showinfo("Character export summary","Exported: "+(", ".join(ready) if ready else "none")+"\
Blocked/incomplete: "+(", ".join(blocked) if blocked else "none"))

class TransferCenter(ttk.Frame):
 def __init__(self,parent,app=None):
  super().__init__(parent);self.app=app;self.cfg=load(SET,{});self.status=tk.StringVar(value="Ready. Configure locations once, then use the transfer buttons.");self.build()
 def build(self):
  paths=ttk.LabelFrame(self,text="Connected Programs",padding=10);paths.pack(fill="x",pady=(0,10))
  self.project=tk.StringVar(value=self.cfg.get("rpgMakerProject",""));self.csp=tk.StringVar(value=self.cfg.get("clipStudio",""))
  ttk.Label(paths,text="RPG Maker MZ Project").grid(row=0,column=0,sticky="w");ttk.Entry(paths,textvariable=self.project,width=70).grid(row=0,column=1,sticky="ew",padx=6);ttk.Button(paths,text="Choose",command=self.choose_project).grid(row=0,column=2)
  ttk.Label(paths,text="Clip Studio Paint").grid(row=1,column=0,sticky="w",pady=5);ttk.Entry(paths,textvariable=self.csp,width=70).grid(row=1,column=1,sticky="ew",padx=6);ttk.Button(paths,text="Choose",command=self.choose_csp).grid(row=1,column=2)
  paths.columnconfigure(1,weight=1)
  box=ttk.Frame(self);box.pack(fill="both",expand=True)
  a=ttk.LabelFrame(box,text="RPG Maker MZ",padding=12);a.pack(fill="x",pady=5)
  ttk.Button(a,text="Import Generator ZIP",command=self.import_generator).pack(side="left",padx=4)
  ttk.Button(a,text="Import Generator Folder",command=self.import_generator_folder).pack(side="left",padx=4)
  ttk.Button(a,text="Export / Install Ready Content",command=self.install_ready).pack(side="left",padx=4)
  ttk.Button(a,text="Open RPG Maker Project Folder",command=self.open_project).pack(side="left",padx=4)
  pbox=ttk.LabelFrame(box,text="Portable Project Shonen Assets",padding=12);pbox.pack(fill="x",pady=5)
  ttk.Button(pbox,text="Export Reusable Piece Package",command=self.export_package).pack(side="left",padx=4)
  ttk.Button(pbox,text="Import Reusable Piece Package",command=self.import_package).pack(side="left",padx=4)
  b=ttk.LabelFrame(box,text="Clip Studio Paint",padding=12);b.pack(fill="x",pady=5)
  ttk.Button(b,text="Open Artist Workspace",command=self.open_workspace).pack(side="left",padx=4)
  ttk.Button(b,text="Import Finished PNG",command=lambda:self.goto("pieces")).pack(side="left",padx=4)
  ttk.Button(b,text="Create / Edit Reusable Piece",command=lambda:self.goto("pieces")).pack(side="left",padx=4)
  ttk.Label(self,textvariable=self.status,wraplength=900).pack(anchor="w",pady=12)
  ttk.Label(self,text="Transfers validate destinations and preserve RPG Maker files with timestamped backups before replacement.",wraplength=900).pack(anchor="w")
 def persist(self):
  self.cfg["rpgMakerProject"]=self.project.get();self.cfg["clipStudio"]=self.csp.get();save(SET,self.cfg)
  if self.app is not None:self.app.cfg.update(self.cfg)
 def choose_project(self):
  p=filedialog.askdirectory(title="Choose RPG Maker MZ project")
  if not p:return
  q=Path(p)
  if not (q/"img").exists() or not (q/"data").exists():messagebox.showerror("Not an RPG Maker MZ project","Choose the project root containing the img and data folders.");return
  self.project.set(p);self.persist();self.status.set("RPG Maker MZ project connected.")
 def choose_csp(self):
  p=filedialog.askopenfilename(title="Choose Clip Studio Paint",filetypes=[("Windows program","*.exe"),("All files","*.*")])
  if p:self.csp.set(p);self.persist();self.status.set("Clip Studio Paint connected.")
 def import_generator(self):
  p=filedialog.askopenfilename(title="Select RPG Maker MZ generator ZIP",filetypes=[("ZIP archive","*.zip")])
  if not p:return
  try:
   import mz_generator_importer
   r=mz_generator_importer.import_generator_zip(p);self.status.set(f"Imported {r['filesImported']} files and registered {r['componentsAdded']} components; skipped {r['invalidPngsSkipped']} invalid PNGs.")
   messagebox.showinfo("Import complete",self.status.get())
  except Exception as e:messagebox.showerror("Import failed",str(e))
 def import_generator_folder(self):
  p=filedialog.askdirectory(title="Choose RPG Maker MZ generator folder")
  if not p:return
  try:
   import mz_generator_importer
   r=mz_generator_importer.import_generator_folder(p);self.status.set(f"Imported {r['filesImported']} files and registered {r['componentsAdded']} components; skipped {r['invalidPngsSkipped']} invalid PNGs.")
   messagebox.showinfo("Import complete",self.status.get())
  except Exception as e:messagebox.showerror("Import failed",str(e))
 def install_ready(self):
  q=Path(self.project.get())
  if not (q/"img").exists() or not (q/"data").exists():messagebox.showerror("Setup required","Connect a valid RPG Maker MZ project first.");return
  staged=sum(len(list((ROOT/"exports"/typ).glob("*.png"))) for typ in DEST if (ROOT/"exports"/typ).exists())
  if not staged:messagebox.showinfo("Nothing to transfer","No exported character graphics are staged yet. Export a character first.");return
  if not messagebox.askyesno("Export to RPG Maker MZ",f"Install {staged} staged graphics into the connected RPG Maker MZ project? Existing same-name files will be backed up first."):return
  stamp=time.strftime("%Y%m%d-%H%M%S");bak=ROOT/"backups"/stamp;installed=backed=0
  for typ,dest in DEST.items():
   src=ROOT/"exports"/typ
   if not src.exists():continue
   dd=q/dest;dd.mkdir(parents=True,exist_ok=True)
   for p in src.glob("*.png"):
    target=dd/p.name
    if target.exists():
     bd=bak/dest;bd.mkdir(parents=True,exist_ok=True);shutil.copy2(target,bd/p.name);backed+=1
    shutil.copy2(p,target);installed+=1
  self.status.set(f"Transfer complete: {installed} installed, {backed} replaced files backed up.")
  messagebox.showinfo("Transfer complete",self.status.get())
 def open_project(self):
  q=Path(self.project.get())
  if not q.exists():messagebox.showerror("Project not connected","Choose the RPG Maker MZ project first.");return
  try:__import__("os").startfile(q)
  except Exception as e:messagebox.showerror("Could not open folder",str(e))
 def open_workspace(self):
  d=ROOT/"artist_workspace";d.mkdir(parents=True,exist_ok=True)
  try:__import__("os").startfile(d)
  except Exception as e:messagebox.showerror("Could not open workspace",str(e))
 def goto(self,page):
  if self.app is not None:self.app.page(page)

class RPGInstaller(ttk.Frame):
 def __init__(self,parent):
  super().__init__(parent);self.cfg=load(SET,{});self.build()
 def build(self):
  self.project=tk.StringVar(value=self.cfg.get("rpgMakerProject",""))
  f=ttk.Frame(self);f.pack(fill="x");ttk.Label(f,text="RPG Maker MZ Project").pack(side="left");ttk.Entry(f,textvariable=self.project).pack(side="left",fill="x",expand=True,padx=6);ttk.Button(f,text="Choose",command=self.choose).pack(side="left")
  self.tree=ttk.Treeview(self,columns=("dest","ready"),show="tree headings");self.tree.heading("#0",text="Output");self.tree.heading("dest",text="Destination");self.tree.heading("ready",text="Ready Files");self.tree.pack(fill="both",expand=True,pady=10)
  b=ttk.Frame(self);b.pack(fill="x");ttk.Button(b,text="Refresh",command=self.refresh).pack(side="left");ttk.Button(b,text="Install All Ready Graphics",command=self.install).pack(side="right")
  self.refresh()
 def choose(self):
  p=filedialog.askdirectory()
  if not p:return
  q=Path(p)
  if not (q/"img").exists() or not (q/"data").exists():messagebox.showerror("Not an RPG Maker MZ project","Choose the project root containing img and data.");return
  self.project.set(p);self.cfg["rpgMakerProject"]=p;save(SET,self.cfg)
 def refresh(self):
  for x in self.tree.get_children():self.tree.delete(x)
  for typ,dest in DEST.items():
   d=ROOT/"exports"/typ;n=len(list(d.glob("*.png"))) if d.exists() else 0;self.tree.insert("","end",text=typ,values=(dest,n))
 def install(self):
  q=Path(self.project.get())
  if not (q/"img").exists() or not (q/"data").exists():messagebox.showerror("Setup required","Choose a valid RPG Maker MZ project first.");return
  stamp=time.strftime("%Y%m%d-%H%M%S");bak=ROOT/"backups"/stamp;installed=backed=0
  for typ,dest in DEST.items():
   src=ROOT/"exports"/typ
   if not src.exists():continue
   dd=q/dest;dd.mkdir(parents=True,exist_ok=True)
   for p in src.glob("*.png"):
    target=dd/p.name
    if target.exists():
     bd=bak/dest;bd.mkdir(parents=True,exist_ok=True);shutil.copy2(target,bd/p.name);backed+=1
    shutil.copy2(p,target);installed+=1
  messagebox.showinfo("Installation complete",f"Installed {installed} graphics.\
Backed up {backed} replaced graphics.");self.refresh()

class Health(ttk.Frame):
 def __init__(self,parent):
  super().__init__(parent);self.build()
 def build(self):
  lib=load(LIB,{"assets":[]});reg=load(REG,{"masters":[]});issues=[]
  ids=set()
  for a in lib["assets"]:
   if a.get("id") in ids:issues.append(("ERROR",a.get("name",""),"Duplicate asset ID"))
   ids.add(a.get("id"))
   m=next((m for m in reg["masters"] if m.get("id")==a.get("masterId") or m.get("key")==a.get("body")),None)
   if not m:issues.append(("ERROR",a.get("name",""),"Compatible body master is missing"))
   for k,o in a.get("outputs",{}).items():
    if o.get("status")=="complete" and (not o.get("path") or not (ROOT/o["path"]).exists()):issues.append(("ERROR",a.get("name",""),f"{k} marked complete but file is missing"))
  for m in reg["masters"]:
   for k,o in m["outputs"].items():
    p=app_paths.resolve(o.get("base",""))
    if o.get("status")=="approved" and not p.exists():issues.append(("ERROR",m["name"],f"Approved {k} master file is missing"))
    if o.get("status")!="approved":issues.append(("INFO",m["name"],f"{k} is not production-approved"))
  ttk.Label(self,text=f"Library Health: {len([x for x in issues if x[0]=='ERROR'])} errors, {len([x for x in issues if x[0]=='INFO'])} readiness notices",font=("TkDefaultFont",12,"bold")).pack(anchor="w",pady=(0,8))
  t=ttk.Treeview(self,columns=("level","item","issue"),show="headings");t.heading("level",text="Level");t.heading("item",text="Item");t.heading("issue",text="Finding");t.column("issue",width=520);t.pack(fill="both",expand=True)
  for x in issues:t.insert("","end",values=x)
