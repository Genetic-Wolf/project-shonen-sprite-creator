#!/usr/bin/env python3
import tkinter as tk,json,re,os,shutil,zipfile,xml.etree.ElementTree as ET
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
REG=ROOT/"master_registry.json"
OUTS={"TV":(144,192),"FG":(144,144),"TVD":(144,192),"SV":(576,384),"Variation":(144,144)}
class Wizard(tk.Tk):
 def __init__(self):
  super().__init__();self.title("Project Shonen — New Body Master Wizard v0.8.0");self.geometry("720x570")
  self.sex=tk.StringVar(value="Female");self.body=tk.StringVar(value="Chubby");self.name=tk.StringVar(value="Female Chubby")
  self.parent=tk.StringVar(value="Female Standard");self.bust=tk.StringVar(value="Universal / N/A")
  self.build()
 def build(self):
  ttk.Label(self,text="Create New Body Master",font=("TkDefaultFont",16,"bold")).pack(anchor="w",padx=18,pady=(18,4))
  ttk.Label(self,text="No IDs, filenames, JSON, or RPG Maker folders are required. The wizard creates the complete master workspace.",wraplength=650).pack(anchor="w",padx=18,pady=(0,14))
  f=ttk.Frame(self);f.pack(fill="x",padx=18)
  rows=[
   ("Body family / sex class",self.sex,["Female","Male","Youth","Child","Custom"]),
   ("Body type",self.body,["Small","Standard","Tall","Athletic","Chubby","Heavy","Custom"]),
   ("Display name",self.name,None),
   ("Start from reference",self.parent,["Female Standard","Male Standard","None"]),
   ("Bust fit profile",self.bust,["Universal / N/A","Small","Medium","Large","Small + Medium","Medium + Large","Custom"])
  ]
  for i,(lab,var,vals) in enumerate(rows):
   ttk.Label(f,text=lab).grid(row=i,column=0,sticky="e",padx=6,pady=7)
   if vals: ttk.Combobox(f,textvariable=var,values=vals,state="readonly",width=35).grid(row=i,column=1,sticky="w",pady=7)
   else: ttk.Entry(f,textvariable=var,width=38).grid(row=i,column=1,sticky="w",pady=7)
  self.sex.trace_add("write",self.autoname);self.body.trace_add("write",self.autoname)
  ttk.Separator(self).pack(fill="x",padx=18,pady=14)
  ttk.Label(self,text="The new master will receive:",font=("TkDefaultFont",11,"bold")).pack(anchor="w",padx=18)
  ttk.Label(self,text="• TV walking master  • Face master  • TVD/downed master\n• SV battle master  • Variation/preview master\n• Clip Studio-compatible layered ORA workspace for every output\n• automatic registry entry and approval tracking",justify="left").pack(anchor="w",padx=28,pady=8)
  ttk.Button(self,text="Create Body Master Workspace",command=self.create).pack(pady=18)
 def autoname(self,*a):
  if self.body.get()!="Custom" and self.sex.get()!="Custom":self.name.set(f"{self.sex.get()} {self.body.get()}")
 def create(self):
  name=self.name.get().strip()
  if not name:return
  data=json.load(open(REG,encoding="utf-8"))
  if any(x["name"].lower()==name.lower() for x in data["masters"]):
   messagebox.showerror("Already exists","A body master with this name already exists.");return
  key=re.sub(r"[^A-Za-z0-9]+","_",name).strip("_");mid="PS-MASTER-"+re.sub(r"[^A-Z0-9]+","-",name.upper()).strip("-")
  md=ROOT/"masters"/key;md.mkdir(parents=True,exist_ok=True)
  outputs={}
  parent=next((x for x in data["masters"] if x["name"]==self.parent.get()),None)
  for out,size in OUTS.items():
   base=Image.new("RGBA",size,(0,0,0,0))
   # Parent is reference only; never copied into the DRAW layer.
   ref=None
   if parent:
    pp=ROOT/parent["outputs"][out]["base"]
    if pp.exists() and Image.open(pp).size==size:ref=Image.open(pp).convert("RGBA")
   guide=Image.new("RGBA",size,(0,0,0,0));d=ImageDraw.Draw(guide);d.rectangle((0,0,size[0]-1,size[1]-1),outline=(255,210,0,180))
   if out in ("TV","TVD"):
    for x in (48,96):d.line((x,0,x,192),fill=(0,180,255,120))
    for y in (48,96,144):d.line((0,y,144,y),fill=(0,180,255,120))
   elif out=="SV":
    for x in range(64,576,64):d.line((x,0,x,384),fill=(0,180,255,100))
    for y in range(64,384,64):d.line((0,y,576,y),fill=(0,180,255,100))
   else:d.line((size[0]//2,0,size[0]//2,size[1]-1),fill=(255,0,255,110))
   p=md/f"{out}_BASE_DRAFT.png";base.save(p)
   layers=[("00_GUIDES_DO_NOT_EXPORT",guide)]
   if ref is not None:layers.append(("01_PARENT_REFERENCE_DO_NOT_EXPORT",ref))
   layers.append((f"02_DRAW_{out}_MASTER_HERE",base))
   self.ora(md/f"EDIT_{key}_{out}_MASTER.ora",layers,size)
   outputs[out]={"status":"draft","locked":False,"size":list(size),"base":str(p.relative_to(ROOT)).replace("\\","/")}
  entry={"id":mid,"name":name,"key":key,"sexClass":self.sex.get().lower(),"bodyClass":self.body.get().lower(),
         "bustFitProfile":self.bust.get(),"parentReference":parent["id"] if parent else None,"status":"development","outputs":outputs}
  data["masters"].append(entry);json.dump(data,open(REG,"w",encoding="utf-8"),indent=2)
  (md/"MASTER_INSTRUCTIONS.txt").write_text(f"""PROJECT SHONEN BODY MASTER: {name}
1. Open each EDIT_*_MASTER.ora in Clip Studio Paint.
2. Parent artwork is REFERENCE ONLY. Draw the new body on the DRAW MASTER layer.
3. Preserve every canvas/grid exactly.
4. Export each finished master as a transparent PNG at the listed native size.
5. Use Master Template Manager to replace the draft output with the finished PNG.
6. Review it visually, then APPROVE + LOCK it.
7. Do not mass-produce compatible clothing/hair/etc. until the relevant output is approved and locked.

Body family: {self.sex.get()}
Body type: {self.body.get()}
Bust fit profile: {self.bust.get()}
Parent reference: {self.parent.get()}
""",encoding="utf-8")
  try:os.startfile(md)
  except:pass
  messagebox.showinfo("Body master created",f"{name} has been registered.\n\nIts five Clip Studio master workspaces are ready.")
 def ora(self,path,layers,size):
  t=path.parent/"_ora_tmp";shutil.rmtree(t,ignore_errors=True);(t/"data").mkdir(parents=True);(t/"Thumbnails").mkdir()
  for i,(n,im) in enumerate(layers):im.save(t/"data"/f"layer{i}.png")
  r=ET.Element("image",{"version":"0.0.1","w":str(size[0]),"h":str(size[1]),"name":path.stem});s=ET.SubElement(r,"stack",{"name":"root"})
  for i,(n,im) in enumerate(layers):ET.SubElement(s,"layer",{"name":n,"src":f"data/layer{i}.png","visibility":"visible"})
  ET.ElementTree(r).write(t/"stack.xml",encoding="UTF-8",xml_declaration=True);(t/"mimetype").write_text("image/openraster")
  thumb=layers[-1][1].copy();thumb.thumbnail((256,256));thumb.save(t/"Thumbnails/thumbnail.png")
  with zipfile.ZipFile(path,"w") as z:
   z.write(t/"mimetype","mimetype",compress_type=zipfile.ZIP_STORED);z.write(t/"stack.xml","stack.xml");z.write(t/"Thumbnails/thumbnail.png","Thumbnails/thumbnail.png")
   for i in range(len(layers)):z.write(t/"data"/f"layer{i}.png",f"data/layer{i}.png")
  shutil.rmtree(t)
Wizard().mainloop()
