import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
import app_paths
from PIL import Image,ImageTk,ImageDraw
import json,shutil,os,zipfile,xml.etree.ElementTree as ET
ROOT=app_paths.DATA_ROOT
RESOURCE_ROOT=app_paths.RESOURCE_ROOT
app_paths.bootstrap()
REG=ROOT/"master_registry.json";LIB=ROOT/"library.json"
OUTS={"TV":("Walking",(144,192)),"FG":("Face",(144,144)),"TVD":("Downed",(144,48)),"SV":("Battle",(576,384)),"Variation":("Preview",(64,64))}
def load(p,d):
 try:return json.load(open(p,encoding="utf-8"))
 except:return d
def save(p,d):json.dump(d,open(p,"w",encoding="utf-8"),indent=2)
def ora(path,layers,size):
 t=path.parent/"_ora";shutil.rmtree(t,ignore_errors=True);(t/"data").mkdir(parents=True);(t/"Thumbnails").mkdir()
 for i,(n,im) in enumerate(layers):im.save(t/"data"/f"layer{i}.png")
 r=ET.Element("image",{"version":"0.0.1","w":str(size[0]),"h":str(size[1]),"name":path.stem});s=ET.SubElement(r,"stack",{"name":"root"})
 for i,(n,im) in enumerate(layers):ET.SubElement(s,"layer",{"name":n,"src":f"data/layer{i}.png","visibility":"visible"})
 ET.ElementTree(r).write(t/"stack.xml",encoding="UTF-8",xml_declaration=True);(t/"mimetype").write_text("image/openraster")
 thumb=layers[-1][1].copy();thumb.thumbnail((256,256));thumb.save(t/"Thumbnails/thumbnail.png")
 with zipfile.ZipFile(path,"w") as z:
  z.write(t/"mimetype","mimetype",compress_type=zipfile.ZIP_STORED);z.write(t/"stack.xml","stack.xml");z.write(t/"Thumbnails/thumbnail.png","Thumbnails/thumbnail.png")
  for i in range(len(layers)):z.write(t/"data"/f"layer{i}.png",f"data/layer{i}.png")
 shutil.rmtree(t)
def guide(size,out):
 im=Image.new("RGBA",size,(0,0,0,0));d=ImageDraw.Draw(im);d.rectangle((0,0,size[0]-1,size[1]-1),outline=(255,210,0,180))
 if out in ("TV","TVD"):
  for x in (48,96):d.line((x,0,x,192),fill=(0,180,255,120))
  for y in (48,96,144):d.line((0,y,144,y),fill=(0,180,255,120))
 elif out=="SV":
  for x in range(64,576,64):d.line((x,0,x,384),fill=(0,180,255,100))
  for y in range(64,384,64):d.line((0,y,576,y),fill=(0,180,255,100))
 else:d.line((size[0]//2,0,size[0]//2,size[1]-1),fill=(255,0,255,100))
 return im

class LibraryGallery(ttk.Frame):
 def __init__(self,parent,kind="pieces"):
  super().__init__(parent);self.kind=kind;self.photos=[];self.build()
 def build(self):
  data=load(LIB,{"assets":[]}).get("assets",[]) if self.kind=="pieces" else load(REG,{"masters":[]}).get("masters",[])
  if not data:
   ttk.Label(self,text="Nothing is available yet. Import RPG Maker MZ generator artwork or create new Project Shonen artwork.",wraplength=700).pack(pady=30);return
  cv=tk.Canvas(self,highlightthickness=0);sb=ttk.Scrollbar(self,orient="vertical",command=cv.yview);inner=ttk.Frame(cv);inner.bind("<Configure>",lambda e:cv.configure(scrollregion=cv.bbox("all")));cv.create_window((0,0),window=inner,anchor="nw");cv.configure(yscrollcommand=sb.set);cv.pack(side="left",fill="both",expand=True);sb.pack(side="right",fill="y")
  for n,item in enumerate(data):
   card=ttk.LabelFrame(inner,text=item.get("name",item.get("id","Item")),padding=6);card.grid(row=n//4,column=n%4,padx=5,pady=5,sticky="nsew")
   p=None
   if self.kind=="pieces":
    o=item.get("outputs",{}).get("Variation") or item.get("outputs",{}).get("TV",{});p=app_paths.resolve(o.get("path","")) if o.get("path") else None
   else:
    o=item.get("outputs",{}).get("TV",{});p=app_paths.resolve(o.get("base","")) if o.get("base") else None
   if p and p.exists():
    try:
     im=Image.open(p).convert("RGBA");
     if im.width>=96 and im.height>=48:im=im.crop((48,0,96,48))
     im.thumbnail((96,96),Image.Resampling.NEAREST);ph=ImageTk.PhotoImage(im);self.photos.append(ph);ttk.Label(card,image=ph).pack()
    except Exception:ttk.Label(card,text="Preview unavailable",width=18).pack(pady=25)
   else:ttk.Label(card,text="Preview unavailable",width=18).pack(pady=25)
   ttk.Label(card,text=item.get("category",item.get("status","")),wraplength=150).pack()

class PieceEditor(ttk.Frame):
 def __init__(self,parent):
  super().__init__(parent);self.lib=load(LIB,{"assets":[]});self.reg=load(REG,{"masters":[]});self.current=None;self.pic=None;self.build()
 def build(self):
  pan=ttk.Panedwindow(self,orient="horizontal");pan.pack(fill="both",expand=True)
  l=ttk.Frame(pan,padding=6);r=ttk.Frame(pan,padding=6);pan.add(l,weight=2);pan.add(r,weight=5)
  self.list=tk.Listbox(l);self.list.pack(fill="both",expand=True);self.list.bind("<<ListboxSelect>>",self.select)
  for a in self.lib["assets"]:self.list.insert("end",a.get("name",a["id"]))
  self.name=tk.StringVar(value="Select a reusable piece");ttk.Label(r,textvariable=self.name,font=("TkDefaultFont",13,"bold")).pack(anchor="w")
  self.cards=ttk.Frame(r);self.cards.pack(fill="x",pady=8);self.status={}
  for k,(label,size) in OUTS.items():
   f=ttk.LabelFrame(self.cards,text=label,padding=6);f.pack(fill="x",pady=2)
   st=tk.StringVar(value="—");self.status[k]=st;ttk.Label(f,textvariable=st,width=12).pack(side="left")
   ttk.Button(f,text="Create Clip Studio Workspace",command=lambda x=k:self.workspace(x)).pack(side="left",padx=3)
   ttk.Button(f,text="Import PNG",command=lambda x=k:self.importpng(x)).pack(side="left",padx=3)
   ttk.Button(f,text="Open Artwork",command=lambda x=k:self.openart(x)).pack(side="right")
  self.preview=tk.Canvas(r,width=360,height=260,bg="#30343b",highlightthickness=0);self.preview.pack(fill="both",expand=True)
 def asset(self):
  return self.lib["assets"][self.current] if self.current is not None else None
 def select(self,e=None):
  s=self.list.curselection()
  if not s:return
  self.current=s[0];a=self.asset();self.name.set(a["name"])
  for k in OUTS:
   o=a.get("outputs",{}).get(k,{})
   self.status[k].set("✓ COMPLETE" if o.get("status")=="complete" and o.get("path") else "— MISSING")
 def master(self,a):
  return next((m for m in self.reg["masters"] if m.get("id")==a.get("masterId") or m.get("key")==a.get("body")),None)
 def workspace(self,out):
  a=self.asset()
  if not a:return
  label,size=OUTS[out];m=self.master(a)
  if not m: messagebox.showerror("No body master","This piece is not linked to a valid body master.");return
  mo=m["outputs"].get(out,{})
  if mo.get("status") not in ("approved","reference") or not mo.get("locked"):
   messagebox.showerror("Master not production-ready",f"{m['name']} {out} is still {mo.get('status','draft')}. Replace, review, approve and lock the body master before creating production reusable artwork.");return
  d=ROOT/"artist_workspace"/"Pieces"/a["id"]/out;d.mkdir(parents=True,exist_ok=True)
  ref=None
  if m:
   p=app_paths.resolve(mo.get("base",""))
   if p.exists() and Image.open(p).size==size:ref=Image.open(p).convert("RGBA")
  layers=[("00_GUIDES_DO_NOT_EXPORT",guide(size,out))]
  if ref is not None:layers.append(("01_BODY_MASTER_REFERENCE_DO_NOT_EXPORT",ref))
  blank=Image.new("RGBA",size,(0,0,0,0));layers.append((f"02_DRAW_{out}_HERE",blank))
  path=d/f'EDIT_{a["name"].replace(" ","_")}_{out}.ora';ora(path,layers,size)
  (d/"READ_ME_FIRST.txt").write_text(f"Draw {a['name']} on the DRAW layer. Hide guides/reference before exporting. Export transparent PNG at {size[0]}x{size[1]}, then return to the creator and click Import PNG.
",encoding="utf-8")
  try:os.startfile(path)
  except:pass
 def importpng(self,out):
  a=self.asset()
  if not a:return
  m=self.master(a);mo=m.get("outputs",{}).get(out,{}) if m else {}
  if not m or mo.get("status") not in ("approved","reference") or not mo.get("locked"):
   messagebox.showerror("Master not production-ready","Reusable artwork cannot be imported as complete until its body master output is approved and locked.");return
  p=filedialog.askopenfilename(filetypes=[("PNG","*.png")])
  if not p:return
  im=Image.open(p).convert("RGBA");size=OUTS[out][1]
  if im.size!=size:messagebox.showerror("Wrong canvas",f"{OUTS[out][0]} artwork must be {size[0]}×{size[1]}.");return
  d=ROOT/"assets/outputs"/out;d.mkdir(parents=True,exist_ok=True);dst=d/f'{a["id"]}_{out}.png';im.save(dst)
  a.setdefault("outputs",{})[out]={"status":"complete","path":str(dst.relative_to(ROOT)).replace("\\","/")}
  if out=="TV":a["path"]=a["outputs"][out]["path"]
  save(LIB,self.lib);self.select()
 def openart(self,out):
  a=self.asset()
  if not a:return
  o=a.get("outputs",{}).get(out,{})
  if not o.get("path"):return
  p=ROOT/o["path"]
  try:os.startfile(p)
  except:pass

class MasterEditor(ttk.Frame):
 def __init__(self,parent):
  super().__init__(parent);self.reg=load(REG,{"masters":[]});self.cur=None;self.build()
 def build(self):
  pan=ttk.Panedwindow(self,orient="horizontal");pan.pack(fill="both",expand=True)
  l=ttk.Frame(pan,padding=6);r=ttk.Frame(pan,padding=6);pan.add(l,weight=2);pan.add(r,weight=5)
  self.list=tk.Listbox(l);self.list.pack(fill="both",expand=True);self.list.bind("<<ListboxSelect>>",self.select)
  for m in self.reg["masters"]:self.list.insert("end",m["name"])
  self.title=tk.StringVar(value="Select a body master");ttk.Label(r,textvariable=self.title,font=("TkDefaultFont",13,"bold")).pack(anchor="w")
  self.tree=ttk.Treeview(r,columns=("status","locked","canvas"),show="tree headings")
  self.tree.heading("#0",text="Output")
  for c,t in [("status","Status"),("locked","Locked"),("canvas","Canvas")]:self.tree.heading(c,text=t)
  self.tree.pack(fill="both",expand=True,pady=8)
  b=ttk.Frame(r);b.pack(fill="x")
  ttk.Button(b,text="Replace Master PNG",command=self.replace).pack(side="left")
  ttk.Button(b,text="Approve + Lock",command=self.approve).pack(side="left",padx=5)
  ttk.Button(b,text="Unlock for Revision",command=self.unlock).pack(side="left")
 def master(self):return self.reg["masters"][self.cur] if self.cur is not None else None
 def select(self,e=None):
  s=self.list.curselection()
  if not s:return
  self.cur=s[0];m=self.master();self.title.set(m["name"])
  for x in self.tree.get_children():self.tree.delete(x)
  for k,o in m["outputs"].items():self.tree.insert("","end",iid=k,text=OUTS.get(k,(k,None))[0],values=(o.get("status"),"YES" if o.get("locked") else "NO",f'{o["size"][0]}×{o["size"][1]}'))
 def chosen(self):
  s=self.tree.selection();return s[0] if s else None
 def replace(self):
  m=self.master();k=self.chosen()
  if not m or not k:return
  o=m["outputs"][k]
  if o.get("locked"):messagebox.showerror("Locked","Unlock this master output before replacing it.");return
  p=filedialog.askopenfilename(filetypes=[("PNG","*.png")])
  if not p:return
  im=Image.open(p).convert("RGBA")
  if list(im.size)!=o["size"]:messagebox.showerror("Wrong canvas",f'Expected {o["size"][0]}×{o["size"][1]}.');return
  dst=ROOT/o["base"];dst.parent.mkdir(parents=True,exist_ok=True);im.save(dst);o["status"]="review";save(REG,self.reg);self.select()
 def approve(self):
  m=self.master();k=self.chosen()
  if not m or not k:return
  o=m["outputs"][k]
  if not messagebox.askyesno("Approve canonical master","Lock this artwork as the canonical geometry for compatible components?"):return
  o["status"]="approved";o["locked"]=True
  if all(x.get("status")=="approved" and x.get("locked") for x in m["outputs"].values()): m["status"]="production"
  save(REG,self.reg);self.select()
 def unlock(self):
  m=self.master();k=self.chosen()
  if not m or not k:return
  if not messagebox.askyesno("Unlock master","Changing canonical geometry can misalign existing components. Continue?"):return
  o=m["outputs"][k];o["locked"]=False;o["status"]="revision";m["status"]="revision";save(REG,self.reg);self.select()
