import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import app_paths
import json,re
ROOT=app_paths.DATA_ROOT
RESOURCE_ROOT=app_paths.RESOURCE_ROOT
app_paths.bootstrap()
REG=ROOT/"master_registry.json";LIB=ROOT/"library.json"
CATEGORIES=["Face / Shape","Face / Eyes","Face / Eyebrows","Face / Nose","Face / Mouth","Face / Ears","Face / Facial Hair","Face / Markings","Face / Dōjutsu","Face / Scars","Face / Tattoos","Face / Clan Markings","Hair / Rear","Hair / Main","Hair / Front","Hair / Ponytail","Hair / Accessories","Clothing / Undershirt","Clothing / Shirt","Clothing / Pants","Clothing / Skirt","Clothing / Belt","Clothing / Gloves","Clothing / Shoes","Clothing","Armor / Chest","Armor / Shoulders","Armor / Arms","Armor / Legs","Armor","Shinobi / Forehead Protector","Shinobi / Village Symbol","Shinobi / Tool Pouch","Shinobi / Kunai Holster","Shinobi / Scrolls","Outerwear / Vest","Outerwear / Coat","Outerwear / Robe","Outerwear / Cloak","Accessories / Head","Accessories / Head A","Accessories / Head B","Accessories / Face","Accessories / Neck","Accessories / Hands","Accessories / Back","Weapons / Back","Weapons / Left Hip","Weapons / Right Hip","Weapons / Left Hand","Weapons / Right Hand","Special / Tail","Special / Wings","Special / Beast Ears","Special / Clan Features","Special / Transformation Features"]
CATKEY={x:x for x in CATEGORIES}
BODYTYPES=["Small","Standard","Tall","Athletic","Chubby","Heavy","Custom"]
FAMILIES=["Female","Male","Youth","Child","Custom"]
def load(p,d):
 try:return json.load(open(p,encoding="utf-8"))
 except:return d
def save(p,d):json.dump(d,open(p,"w",encoding="utf-8"),indent=2)

def new_piece_dialog(parent,on_done=None,preferred_body=None,preferred_category=None):
 data=load(REG,{"masters":[]});lib=load(LIB,{"assets":[]})
 w=tk.Toplevel(parent);w.title("Create Reusable Piece");w.geometry("760x700");w.transient(parent);w.grab_set()
 name=tk.StringVar();cat=tk.StringVar(value=preferred_category if preferred_category in CATEGORIES else "Hair / Front")
 masters=[m["name"] for m in data["masters"]];body=tk.StringVar(value=preferred_body if preferred_body in masters else (masters[0] if masters else ""))\n scope=tk.StringVar(value="Body Specific");bust=tk.StringVar(value="Any")
 ttk.Label(w,text="Create Artwork",font=("TkDefaultFont",15,"bold")).pack(anchor="w",padx=18,pady=(18,4))
 ttk.Label(w,text="1. Choose the body this artwork fits.  2. Choose what you are drawing.  3. Give it a normal name. The program handles IDs and files.",wraplength=700).pack(anchor="w",padx=18,pady=(0,12))
 f=ttk.Frame(w);f.pack(fill="x",padx=18)
 for r,(lab,var,vals) in enumerate([("Body",body,masters),("What are you drawing?",cat,CATEGORIES),("Artwork name",name,None)]):
  ttk.Label(f,text=lab).grid(row=r,column=0,sticky="e",padx=6,pady=8)
  if vals is None:ttk.Entry(f,textvariable=var,width=38).grid(row=r,column=1,sticky="w")
  else:ttk.Combobox(f,textvariable=var,values=vals,state="readonly",width=35).grid(row=r,column=1,sticky="w")
 ttk.Label(f,text="Compatibility").grid(row=3,column=0,sticky="e",padx=6,pady=8)\n ttk.Combobox(f,textvariable=scope,values=["Body Specific","Family Compatible","Head Compatible","Universal"],state="readonly",width=35).grid(row=3,column=1,sticky="w")\n ttk.Label(f,text="Female bust fit").grid(row=4,column=0,sticky="e",padx=6,pady=8)\n ttk.Combobox(f,textvariable=bust,values=["Any","Small","Medium","Large"],state="readonly",width=35).grid(row=4,column=1,sticky="w")\n ttk.Label(w,text="Body Specific is safest for fitted clothing/armor. Family Compatible shares within the same Male/Female/Youth/Child family. Head Compatible is intended for head/face/hair pieces. Universal is for artwork deliberately aligned across all bodies.",wraplength=700).pack(anchor="w",padx=18,pady=10)
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
  if on_done:on_done()
  messagebox.showinfo("Artwork created","The new reusable piece is registered. Open Create Piece to create/edit its workspace or import finished artwork.")
 ttk.Button(w,text="Create Artwork",command=create).pack(pady=18)

def new_master_dialog(parent,on_done=None):
 w=tk.Toplevel(parent);w.title("Create New Body Master");w.geometry("620x520");w.transient(parent);w.grab_set()
 family=tk.StringVar(value="Female");kind=tk.StringVar(value="Chubby");name=tk.StringVar(value="Female Chubby");bust=tk.StringVar(value="Medium")
 data=load(REG,{"masters":[]});refs=["None"]+[m["name"] for m in data["masters"]];ref=tk.StringVar(value=refs[1] if len(refs)>1 else "None")
 ttk.Label(w,text="Create New Master Body Sprite",font=("TkDefaultFont",15,"bold")).pack(anchor="w",padx=18,pady=(18,4))
 ttk.Label(w,text="The artist draws the actual new body in Clip Studio. Existing masters can be used only as alignment references.",wraplength=540).pack(anchor="w",padx=18,pady=(0,12))
 f=ttk.Frame(w);f.pack(fill="x",padx=18)
 rows=[("Family",family,FAMILIES),("Body type",kind,BODYTYPES),("Female bust profile",bust,["Small","Medium","Large","Not Applicable"]),("Display name",name,None),("Reference master",ref,refs)]
 for r,(lab,var,vals) in enumerate(rows):
  ttk.Label(f,text=lab).grid(row=r,column=0,sticky="e",padx=6,pady=8)
  if vals:ttk.Combobox(f,textvariable=var,values=vals,state="readonly",width=35).grid(row=r,column=1,sticky="w")
  else:ttk.Entry(f,textvariable=var,width=38).grid(row=r,column=1,sticky="w")
 def auto(*_):
  if family.get()!="Custom" and kind.get()!="Custom":name.set(f"{family.get()} {kind.get()}")
 family.trace_add("write",auto);kind.trace_add("write",auto)
 ttk.Label(w,text="The creator will prepare TV, Face, TVD, SV and Preview master workspaces. Each begins as Draft and must be reviewed before it can be locked for production.",wraplength=530).pack(anchor="w",padx=18,pady=16)
 def create():
  n=name.get().strip()
  if not n:messagebox.showerror("Missing name","Give this body master a display name.");return
  if any(m.get("name","").lower()==n.lower() for m in data["masters"]):messagebox.showerror("Body already exists","A body master already uses this name.");return
  slug=re.sub(r"[^A-Za-z0-9]+","_",n).strip("_") or "Custom_Body"
  basekey=slug;used={m.get("key") for m in data["masters"]};i=2
  while slug in used:slug=basekey+"_"+str(i);i+=1
  nums=[]
  for m in data["masters"]:
   hit=re.search(r"(\\d+)$",str(m.get("id","")))
   if hit:nums.append(int(hit.group(1)))
  mid=f"PS-BODY-{max([3999]+nums)+1:05d}"
  sizes={"TV":[144,192],"FG":[144,144],"TVD":[144,48],"SV":[576,384],"Variation":[64,64]}
  outputs={k:{"size":v,"status":"draft","locked":False,"base":f"masters/{slug}/{k}/{mid}_{k}.png"} for k,v in sizes.items()}
  master={"id":mid,"key":slug,"name":n,"family":family.get(),"bodyType":kind.get(),"bust":(bust.get() if family.get()=="Female" else "Not Applicable"),"status":"draft","source":"Project Shonen","outputs":outputs}
  if ref.get()!="None":
   rm=next((m for m in data["masters"] if m.get("name")==ref.get()),None)
   if rm:master["referenceMasterId"]=rm.get("id")
  data["masters"].append(master);save(REG,data);w.destroy()
  if on_done:
   try:on_done(master)
   except TypeError:on_done()
  messagebox.showinfo("Body master created",n+" is registered. Select it below and use Edit in Clip Studio Paint for each output.")
 ttk.Button(w,text="Create Body Master",command=create).pack(pady=18)
