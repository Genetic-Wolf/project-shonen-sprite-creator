#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import app_paths
from PIL import Image, ImageTk, ImageDraw
import json, shutil, os, zipfile, xml.etree.ElementTree as ET

ROOT=app_paths.DATA_ROOT
RESOURCE_ROOT=app_paths.RESOURCE_ROOT
app_paths.bootstrap()
OUTPUTS={
 "TV":{"label":"Walking (TV)","size":(144,192),"help":"Map/walking sprite component"},
 "FG":{"label":"Face (FG)","size":(144,144),"help":"Face generator component"},
 "TVD":{"label":"Downed (TVD)","size":(144,192),"help":"Downed/damaged component"},
 "SV":{"label":"Battle (SV)","size":(576,384),"help":"Side-view battle component"},
 "Variation":{"label":"Preview","size":(144,144),"help":"Generator/library preview"}
}
CATS=["Hair_Back","Hair_Front","Eyes","Eyebrows","Mouth","FacialMark","Clothing_Back","Clothing_Front","Armor","Cloak","Headgear","Accessory_Back","Accessory_Front","Weapon_Back","Weapon_Hip","Weapon_Hand"]
FRIEND={x:x.replace("_"," ") for x in CATS}

class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title("Project Shonen Sprite Creator v0.6.0 — Complete Asset Workspace"); self.geometry("1280x780"); self.minsize(1100,680)
  self.libpath=ROOT/"library.json"; self.lib=self.loadlib(); self.body=tk.StringVar(value="Female_Standard"); self.search=tk.StringVar()
  self.current=None; self.preview_img=None
  self.build(); self.populate()
 def loadlib(self):
  if self.libpath.exists():
   try:
    d=json.load(open(self.libpath,encoding="utf-8"))
    for a in d.get("assets",[]):
     a.setdefault("outputs",{})
     if a.get("path"): a["outputs"].setdefault("TV",{"status":"complete","path":a["path"]})
     for k in OUTPUTS:a["outputs"].setdefault(k,{"status":"missing","path":None})
    return d
   except:pass
  return {"assets":[]}
 def save(self): json.dump(self.lib,open(self.libpath,"w",encoding="utf-8"),indent=2)
 def build(self):
  top=ttk.Frame(self,padding=10);top.pack(fill="x")
  ttk.Label(top,text="Project Shonen Asset Studio",font=("TkDefaultFont",16,"bold")).pack(side="left")
  ttk.Label(top,text="Master:").pack(side="left",padx=(30,5))
  b=ttk.Combobox(top,textvariable=self.body,values=["Female_Standard","Male_Standard"],state="readonly",width=18);b.pack(side="left");b.bind("<<ComboboxSelected>>",lambda e:self.populate())
  ttk.Button(top,text="Open Artist Workspace",command=lambda:self.openfolder(ROOT/"artist_workspace")).pack(side="right")
  pane=ttk.Panedwindow(self,orient="horizontal");pane.pack(fill="both",expand=True,padx=10,pady=(0,10))
  left=ttk.Frame(pane,padding=8);mid=ttk.Frame(pane,padding=8);right=ttk.Frame(pane,padding=8);pane.add(left,weight=3);pane.add(mid,weight=4);pane.add(right,weight=4)
  ttk.Label(left,text="Asset Library",font=("TkDefaultFont",12,"bold")).pack(anchor="w")
  ttk.Entry(left,textvariable=self.search).pack(fill="x",pady=(5,5));self.search.trace_add("write",lambda *a:self.populate())
  self.tree=ttk.Treeview(left,columns=("cat",),show="tree headings");self.tree.heading("#0",text="Piece");self.tree.heading("cat",text="Category");self.tree.column("cat",width=120);self.tree.pack(fill="both",expand=True)
  self.tree.bind("<<TreeviewSelect>>",self.select)
  ttk.Button(left,text="+ New Logical Piece",command=self.new_asset).pack(fill="x",pady=(8,2))
  ttk.Button(left,text="Duplicate Piece Record",command=self.duplicate).pack(fill="x",pady=2)
  ttk.Label(mid,text="Selected Piece",font=("TkDefaultFont",12,"bold")).pack(anchor="w")
  self.titlevar=tk.StringVar(value="Select an asset");ttk.Label(mid,textvariable=self.titlevar,font=("TkDefaultFont",13,"bold")).pack(anchor="w",pady=(6,2))
  self.metavar=tk.StringVar();ttk.Label(mid,textvariable=self.metavar).pack(anchor="w")
  self.cards=ttk.Frame(mid);self.cards.pack(fill="both",expand=True,pady=10)
  self.cardwidgets={}
  for k,info in OUTPUTS.items():
   f=ttk.LabelFrame(self.cards,text=info["label"],padding=8);f.pack(fill="x",pady=3)
   st=tk.StringVar(value="MISSING");ttk.Label(f,textvariable=st,width=12).pack(side="left")
   ttk.Button(f,text="Create Clip Studio Workspace",command=lambda x=k:self.create_workspace(x)).pack(side="left",padx=3)
   ttk.Button(f,text="Import Finished PNG",command=lambda x=k:self.import_output(x)).pack(side="left",padx=3)
   ttk.Button(f,text="Preview",command=lambda x=k:self.preview(x)).pack(side="right")
   self.cardwidgets[k]=(f,st)
  ttk.Label(right,text="Output Preview & Validation",font=("TkDefaultFont",12,"bold")).pack(anchor="w")
  self.canvas=tk.Canvas(right,width=390,height=390,bg="#30343b",highlightthickness=0);self.canvas.pack(fill="both",expand=True,pady=8)
  self.status=tk.Text(right,height=8,state="disabled");self.status.pack(fill="x")
  ttk.Button(right,text="Validate Entire Asset",command=self.validate_all).pack(fill="x",pady=(8,2))
  ttk.Button(right,text="Open Multi-Output Guide",command=lambda:self.openfile(ROOT/"MULTI_OUTPUT_WORKFLOW.txt")).pack(fill="x",pady=2)
 def populate(self):
  for x in self.tree.get_children():self.tree.delete(x)
  q=self.search.get().lower().strip()
  for a in self.lib.get("assets",[]):
   if a.get("body") and a.get("body")!=self.body.get():continue
   if q and q not in a.get("name","").lower() and q not in a.get("category","").lower():continue
   self.tree.insert("","end",iid=a["id"],text=a.get("name",a["id"]),values=(FRIEND.get(a.get("category"),a.get("category","")),))
 def getasset(self):
  return next((a for a in self.lib.get("assets",[]) if a.get("id")==self.current),None)
 def select(self,e=None):
  s=self.tree.selection()
  if not s:return
  self.current=s[0];a=self.getasset()
  self.titlevar.set(a.get("name",a["id"]));self.metavar.set(f'{a["id"]}   •   {FRIEND.get(a.get("category"),a.get("category",""))}   •   {a.get("body","Universal")}')
  for k,(f,st) in self.cardwidgets.items():
   o=a.get("outputs",{}).get(k,{})
   st.set("✓ COMPLETE" if o.get("status")=="complete" and o.get("path") else "— MISSING")
  for k in OUTPUTS:
   if a.get("outputs",{}).get(k,{}).get("status")=="complete":self.preview(k);break
 def new_asset(self):
  w=tk.Toplevel(self);w.title("New Reusable Piece");w.transient(self);w.grab_set()
  name=tk.StringVar();cat=tk.StringVar(value="Hair_Front")
  ttk.Label(w,text="Create one logical reusable piece",font=("TkDefaultFont",12,"bold")).grid(row=0,column=0,columnspan=2,padx=14,pady=(14,8),sticky="w")
  ttk.Label(w,text="Name").grid(row=1,column=0,padx=14,pady=5,sticky="e");ttk.Entry(w,textvariable=name,width=36).grid(row=1,column=1,padx=14,pady=5)
  ttk.Label(w,text="Category").grid(row=2,column=0,padx=14,pady=5,sticky="e");ttk.Combobox(w,textvariable=cat,values=CATS,state="readonly",width=33).grid(row=2,column=1,padx=14,pady=5)
  def go():
   n=name.get().strip()
   if not n:return
   nums=[]
   for a in self.lib["assets"]:
    m=re.search(r"(\d+)$",a.get("id",""))
    if m:nums.append(int(m.group(1)))
   num=max([3999]+nums)+1;aid=f"PS-ASSET-{num:05d}"
   a={"id":aid,"name":n,"category":cat.get(),"body":self.body.get(),"outputs":{k:{"status":"missing","path":None} for k in OUTPUTS}}
   self.lib["assets"].append(a);self.save();w.destroy();self.populate();self.tree.selection_set(aid);self.tree.see(aid);self.select()
  ttk.Button(w,text="Create Piece",command=go).grid(row=3,column=0,columnspan=2,pady=14)
 def duplicate(self):
  a=self.getasset()
  if not a:return
  nums=[int(m.group(1)) for x in self.lib["assets"] if (m:=re.search(r"(\d+)$",x.get("id","")))]
  aid=f"PS-ASSET-{max([3999]+nums)+1:05d}";b={"id":aid,"name":a["name"]+" Copy","category":a["category"],"body":a.get("body"),"outputs":{k:{"status":"missing","path":None} for k in OUTPUTS}}
  self.lib["assets"].append(b);self.save();self.populate()
 def base_for(self,out):
  # Use approved TV bases where available. Other outputs get reference-safe blank until their pose master is approved.
  if out=="TV":
   p=app_paths.resolve(Path("assets/bases")/f"{self.body.get()}.png")
   if p.exists():return Image.open(p).convert("RGBA")
  return Image.new("RGBA",OUTPUTS[out]["size"],(0,0,0,0))
 def create_workspace(self,out):
  a=self.getasset()
  if not a:messagebox.showinfo("Select a piece","Select or create a reusable piece first.");return
  size=OUTPUTS[out]["size"];safe=re.sub(r"[^A-Za-z0-9_-]+","_",a["name"])
  d=ROOT/"artist_workspace"/a.get("body","Universal")/a["id"]/out;d.mkdir(parents=True,exist_ok=True)
  base=self.base_for(out);guide=Image.new("RGBA",size,(0,0,0,0));dr=ImageDraw.Draw(guide)
  dr.rectangle((0,0,size[0]-1,size[1]-1),outline=(255,210,0,180))
  if out=="TV":
   for x in (48,96):dr.line((x,0,x,192),fill=(0,180,255,150))
   for y in (48,96,144):dr.line((0,y,144,y),fill=(0,180,255,150))
  elif out=="SV":
   for x in range(64,576,64):dr.line((x,0,x,384),fill=(0,180,255,120))
   for y in range(64,384,64):dr.line((0,y,576,y),fill=(0,180,255,120))
  else:
   dr.line((size[0]//2,0,size[0]//2,size[1]-1),fill=(255,0,255,110))
  blank=Image.new("RGBA",size,(0,0,0,0));Image.alpha_composite(base,guide).save(d/"REFERENCE_DO_NOT_EXPORT.png");blank.save(d/f"EXPORT_{safe}_{out}.png")
  self.write_ora(d/f"EDIT_{safe}_{out}.ora",[("00_GUIDES_DO_NOT_EXPORT",guide),("01_BASE_REFERENCE_DO_NOT_EXPORT",base),(f"02_DRAW_{out}_EXPORT_THIS",blank)])
  (d/"READ_ME_FIRST.txt").write_text(f"""PROJECT SHONEN — {a['name']} — {OUTPUTS[out]['label']}
Open EDIT_{safe}_{out}.ora in Clip Studio Paint.
Draw only on the 02_DRAW layer.
Keep the canvas exactly {size[0]}x{size[1]}.
Do not flatten the guide/reference into your artwork.
Hide guide/reference layers before exporting.
Export the drawing against transparency as PNG.
Return here and click Import Finished PNG for {OUTPUTS[out]['label']}.
The program keeps this artwork attached to {a['id']} automatically.
""",encoding="utf-8")
  self.openfolder(d);messagebox.showinfo("Workspace ready",f"{OUTPUTS[out]['label']} workspace created.\n\nOpen the EDIT_*.ora file in Clip Studio Paint.")
 def write_ora(self,path,layers):
  tmp=path.parent/"_ora";shutil.rmtree(tmp,ignore_errors=True);(tmp/"data").mkdir(parents=True);(tmp/"Thumbnails").mkdir()
  for i,(n,img) in enumerate(layers):img.save(tmp/"data"/f"layer{i}.png")
  root=ET.Element("image",{"version":"0.0.1","w":str(layers[0][1].width),"h":str(layers[0][1].height),"name":path.stem});stack=ET.SubElement(root,"stack",{"name":"root"})
  for i,(n,img) in enumerate(layers):ET.SubElement(stack,"layer",{"name":n,"src":f"data/layer{i}.png","visibility":"visible"})
  ET.ElementTree(root).write(tmp/"stack.xml",encoding="UTF-8",xml_declaration=True);(tmp/"mimetype").write_text("image/openraster")
  thumb=layers[-1][1].copy();thumb.thumbnail((256,256));thumb.save(tmp/"Thumbnails/thumbnail.png")
  with zipfile.ZipFile(path,"w") as z:
   z.write(tmp/"mimetype","mimetype",compress_type=zipfile.ZIP_STORED);z.write(tmp/"stack.xml","stack.xml");z.write(tmp/"Thumbnails/thumbnail.png","Thumbnails/thumbnail.png")
   for i in range(len(layers)):z.write(tmp/"data"/f"layer{i}.png",f"data/layer{i}.png")
  shutil.rmtree(tmp)
 def import_output(self,out):
  a=self.getasset()
  if not a:return
  p=filedialog.askopenfilename(title=f"Import {OUTPUTS[out]['label']} transparent PNG",filetypes=[("PNG","*.png")])
  if not p:return
  try:im=Image.open(p).convert("RGBA")
  except Exception as e:messagebox.showerror("Cannot open image",str(e));return
  if im.size!=OUTPUTS[out]["size"]:
   messagebox.showerror("Wrong canvas",f'{OUTPUTS[out]["label"]} must be {OUTPUTS[out]["size"][0]}x{OUTPUTS[out]["size"][1]}.\nReceived {im.width}x{im.height}.');return
  if im.getbbox() is None and not messagebox.askyesno("Empty artwork","This PNG is completely transparent. Import it anyway?"):return
  d=ROOT/"assets/outputs"/out;d.mkdir(parents=True,exist_ok=True);dst=d/f'{a["id"]}_{out}.png';im.save(dst)
  a["outputs"][out]={"status":"complete","path":str(dst.relative_to(ROOT)).replace("\\","/")}
  if out=="TV":a["path"]=a["outputs"][out]["path"]
  self.save();self.select();messagebox.showinfo("Representation added",f"{OUTPUTS[out]['label']} is now COMPLETE for {a['name']}.")
 def preview(self,out):
  a=self.getasset()
  if not a:return
  o=a.get("outputs",{}).get(out,{})
  p=ROOT/o.get("path","") if o.get("path") else None
  if not p or not p.exists():
   self.canvas.delete("all");self.canvas.create_text(195,195,text=f"{OUTPUTS[out]['label']}\nMISSING",fill="white",font=("TkDefaultFont",15,"bold"),justify="center");return
  im=Image.open(p).convert("RGBA");bg=Image.new("RGBA",im.size,(55,59,66,255));bg.alpha_composite(im);bg.thumbnail((370,370),Image.Resampling.NEAREST)
  self.preview_img=ImageTk.PhotoImage(bg);self.canvas.delete("all");self.canvas.create_image(195,195,image=self.preview_img)
 def validate_all(self):
  a=self.getasset()
  if not a:return
  lines=[];complete=0
  for k,info in OUTPUTS.items():
   o=a.get("outputs",{}).get(k,{})
   if o.get("status")!="complete" or not o.get("path"):lines.append(f"— {info['label']}: missing");continue
   p=ROOT/o["path"]
   if not p.exists():lines.append(f"✗ {info['label']}: registered file missing");continue
   try:
    im=Image.open(p)
    if im.size!=info["size"]:lines.append(f"✗ {info['label']}: wrong dimensions {im.size}")
    else:lines.append(f"✓ {info['label']}: complete");complete+=1
   except:lines.append(f"✗ {info['label']}: unreadable PNG")
  lines.append(f"\nCompletion: {complete}/{len(OUTPUTS)} representations")
  self.status.config(state="normal");self.status.delete("1.0","end");self.status.insert("end","\n".join(lines));self.status.config(state="disabled")
 def openfolder(self,p):
  p.mkdir(parents=True,exist_ok=True)
  try:os.startfile(p)
  except:
   try:os.system(f'xdg-open "{p}" >/dev/null 2>&1 &')
   except:pass
 def openfile(self,p):
  try:os.startfile(p)
  except:self.openfolder(p.parent)
App().mainloop()
