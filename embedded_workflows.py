import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import app_paths
import json,re
ROOT=app_paths.DATA_ROOT
RESOURCE_ROOT=app_paths.RESOURCE_ROOT
app_paths.bootstrap()
REG=ROOT/"master_registry.json";LIB=ROOT/"library.json"
CATEGORIES=["Face / Shape","Face / Eyes","Face / Eyebrows","Face / Nose","Face / Mouth","Face / Ears","Face / Facial Hair","Face / Markings","Face / Dōjutsu","Face / Scars","Face / Tattoos","Face / Clan Markings","Hair / Rear","Hair / Main","Hair / Front","Hair / Ponytail","Hair / Accessories","Clothing / Undershirt","Clothing / Shirt","Clothing / Pants","Clothing / Skirt","Clothing / Belt","Clothing / Gloves","Clothing / Shoes","Armor / Chest","Armor / Shoulders","Armor / Arms","Armor / Legs","Shinobi / Forehead Protector","Shinobi / Village Symbol","Shinobi / Tool Pouch","Shinobi / Kunai Holster","Shinobi / Scrolls","Outerwear / Vest","Outerwear / Coat","Outerwear / Robe","Outerwear / Cloak","Accessories / Head","Accessories / Face","Accessories / Neck","Accessories / Hands","Accessories / Back","Weapons / Back","Weapons / Left Hip","Weapons / Right Hip","Weapons / Left Hand","Weapons / Right Hand","Special / Tail","Special / Wings","Special / Beast Ears","Special / Clan Features","Special / Transformation Features"]
CATKEY={x:x for x in CATEGORIES}
BODYTYPES=["Small","Standard","Tall","Athletic","Chubby","Heavy","Custom"]
FAMILIES=["Female","Male","Youth","Child","Custom"]
def load(p,d):
 try:return json.load(open(p,encoding="utf-8"))
 except:return d
def save(p,d):json.dump(d,open(p,"w",encoding="utf-8"),indent=2)

def new_piece_dialog(parent,on_done=None,preferred_body=None,preferred_category=None):
 data=load(REG,{"masters":[]});lib=load(LIB,{"assets":[]})
 w=tk.Toplevel(parent);w.title("Create Reusable Piece");w.geometry("760x620");w.transient(parent);w.grab_set()
 name=tk.StringVar();cat=tk.StringVar(value=preferred_category if preferred_category in CATEGORIES else "Hair / Front")
 masters=[m["name"] for m in data["masters"]];body=tk.StringVar(value=preferred_body if preferred_body in masters else (masters[0] if masters else ""))
 ttk.Label(w,text="Create Artwork",font=("TkDefaultFont",15,"bold")).pack(anchor="w",padx=18,pady=(18,4))
 ttk.Label(w,text="1. Choose the body this artwork fits.  2. Choose what you are drawing.  3. Give it a normal name. The program handles IDs and files.",wraplength=700).pack(anchor="w",padx=18,pady=(0,12))
 f=ttk.Frame(w);f.pack(fill="x",padx=18)
 for r,(lab,var,vals) in enumerate([("Body",body,masters),("What are you drawing?",cat,CATEGORIES),("Artwork name",name,None)]):
  ttk.Label(f,text=lab).grid(row=r,column=0,sticky="e",padx=6,pady=8)
  if vals is None:ttk.Entry(f,textvariable=var,width=38).grid(row=r,column=1,sticky="w")
  else:ttk.Combobox(f,textvariable=var,values=vals,state="readonly",width=35).grid(row=r,column=1,sticky="w")
 ttk.Label(w,text="After creation this artwork appears immediately in Create Piece. Select it there to create the Clip Studio workspace for Walking, Face, Downed, Battle or Preview art.",wraplength=700).pack(anchor="w",padx=18,pady=16)
 def create():
  n=name.get().strip()
  if not n or not body.get():messagebox.showerror("Missing information","Enter a piece name and choose a body master.");return
  nums=[]
  for a in lib["assets"]:
   m=re.search(r"(\d+)$",a.get("id",""))
   if m:nums.append(int(m.group(1)))
  aid=f"PS-ASSET-{max([3999]+nums)+1:05d}"
  master=next(m for m in data["masters"] if m["name"]==body.get())
  a={"id":aid,"name":n,"category":CATKEY[cat.get()],"body":master["key"],"masterId":master["id"],
     "outputs":{k:{"status":"missing","path":None} for k in ["TV","FG","TVD","SV","Variation"]}}
  lib["assets"].append(a);save(LIB,lib);w.destroy()
  # Existing Asset Studio owns the proven multi-output ORA workflow.
  subprocess.Popen([sys.executable,str(ROOT/"ProjectShonenAssetStudio.py")])
  if on_done:on_done()
 ttk.Button(w,text="Create Artwork",command=create).pack(pady=18)

def new_master_dialog(parent,on_done=None):
 w=tk.Toplevel(parent);w.title("Create New Body Master");w.geometry("590x470");w.transient(parent);w.grab_set()
 family=tk.StringVar(value="Female");kind=tk.StringVar(value="Chubby");name=tk.StringVar(value="Female Chubby")
 data=load(REG,{"masters":[]});refs=["None"]+[m["name"] for m in data["masters"]];ref=tk.StringVar(value=refs[1] if len(refs)>1 else "None")
 ttk.Label(w,text="Create New Master Body Sprite",font=("TkDefaultFont",15,"bold")).pack(anchor="w",padx=18,pady=(18,4))
 ttk.Label(w,text="The artist draws the actual new body in Clip Studio. Existing masters can be used only as alignment references.",wraplength=540).pack(anchor="w",padx=18,pady=(0,12))
 f=ttk.Frame(w);f.pack(fill="x",padx=18)
 rows=[("Family",family,FAMILIES),("Body type",kind,BODYTYPES),("Display name",name,None),("Reference master",ref,refs)]
 for r,(lab,var,vals) in enumerate(rows):
  ttk.Label(f,text=lab).grid(row=r,column=0,sticky="e",padx=6,pady=8)
  if vals:ttk.Combobox(f,textvariable=var,values=vals,state="readonly",width=35).grid(row=r,column=1,sticky="w")
  else:ttk.Entry(f,textvariable=var,width=38).grid(row=r,column=1,sticky="w")
 def auto(*_):
  if family.get()!="Custom" and kind.get()!="Custom":name.set(f"{family.get()} {kind.get()}")
 family.trace_add("write",auto);kind.trace_add("write",auto)
 ttk.Label(w,text="The creator will prepare TV, Face, TVD, SV and Preview master workspaces. Each begins as Draft and must be reviewed before it can be locked for production.",wraplength=530).pack(anchor="w",padx=18,pady=16)
 def create():
  # Delegate actual ORA/master generation to the proven wizard, but artist reaches it from here.
  w.destroy();subprocess.Popen([sys.executable,str(ROOT/"NewBodyMasterWizard.py")])
  if on_done:on_done()
 ttk.Button(w,text="Continue to Master Artwork Setup",command=create).pack(pady=18)
