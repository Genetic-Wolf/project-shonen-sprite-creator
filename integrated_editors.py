import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
import app_paths
from PIL import Image,ImageTk,ImageDraw
import json,shutil,os,zipfile,subprocess,xml.etree.ElementTree as ET
import production_pipeline
import body_master
import piece_lifecycle
ROOT=app_paths.DATA_ROOT
RESOURCE_ROOT=app_paths.RESOURCE_ROOT
app_paths.bootstrap()
REG=ROOT/"master_registry.json";LIB=ROOT/"library.json";SET=ROOT/"artist_settings.json"
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
 if out=="TV":
  for x in (48,96):d.line((x,0,x,192),fill=(0,180,255,120))
  for y in (48,96,144):d.line((0,y,144,y),fill=(0,180,255,120))
 elif out=="TVD":
  for x in (48,96):d.line((x,0,x,48),fill=(0,180,255,120))
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
  actions=ttk.Frame(r);actions.pack(fill="x",pady=(4,2))
  ttk.Button(actions,text="Import Artwork",command=self.smart_import).pack(side="left")
  ttk.Button(actions,text="Compatibility Matrix",command=self.compatibility_matrix).pack(side="left",padx=5)
  ttk.Button(actions,text="Production Dashboard",command=self.production_dashboard).pack(side="left",padx=5)
  ttk.Button(actions,text="Continue Artwork",command=self.continue_artwork).pack(side="left",padx=5)
  ttk.Button(actions,text="Approve Piece",command=self.approve_piece).pack(side="left",padx=5)
  ttk.Button(actions,text="Reopen",command=self.reopen_piece).pack(side="left",padx=5)
  ttk.Label(actions,text="Automatically validates and routes PNG artwork to the selected piece.",wraplength=430).pack(side="left",padx=8)
  self.cards=ttk.Frame(r);self.cards.pack(fill="x",pady=8);self.status={}
  for k,(label,size) in OUTS.items():
   f=ttk.LabelFrame(self.cards,text=label,padding=6);f.pack(fill="x",pady=2)
   st=tk.StringVar(value="—");self.status[k]=st;ttk.Label(f,textvariable=st,width=12).pack(side="left")
   ttk.Button(f,text="Edit in Clip Studio Paint",command=lambda x=k:self.workspace(x)).pack(side="left",padx=3)
   ttk.Button(f,text="Import PNG",command=lambda x=k:self.importpng(x)).pack(side="left",padx=3)
   ttk.Button(f,text="Open Artwork",command=lambda x=k:self.openart(x)).pack(side="right")
  self.production=tk.StringVar(value="Production: choose a reusable piece");ttk.Label(r,textvariable=self.production).pack(anchor="w",pady=(2,4))
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
  self.production.set("Lifecycle: "+piece_lifecycle.lifecycle(a,self.reg.get("masters",[])))
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
  path=d/f'EDIT_{a["name"].replace(" ","_")}_{out}.ora'
  if path.exists():
   if not messagebox.askyesno("Workspace already exists","This Clip Studio workspace already exists. Rebuild it from the current body master?\n\nChoose No to keep your existing artwork and open it without changes."):
    self.open_csp(path);return
  ora(path,layers,size)
  (d/"READ_ME_FIRST.txt").write_text("Draw "+a["name"]+" on the DRAW layer. Hide guides/reference before exporting. Export transparent PNG at "+str(size[0])+"x"+str(size[1])+", then return to the creator and click Import PNG.",encoding="utf-8")
  manifest={"schemaVersion":1,"assetId":a["id"],"assetName":a["name"],"category":a.get("category","Other"),"body":a.get("body"),"masterId":a.get("masterId"),"output":out,"expectedSize":list(size),"destination":"assets/outputs/"+out}
  (d/"project_shonen_artwork.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
  self.open_csp(path)
 def open_csp(self,path):
  cfg=load(SET,{})
  exe=Path(cfg.get("clipStudio","")) if cfg.get("clipStudio") else None
  if not exe or not exe.exists():
   if not messagebox.askyesno("Connect Clip Studio Paint","Clip Studio Paint is not connected or its program location has changed. Choose the Clip Studio Paint program now?"):return
   chosen=filedialog.askopenfilename(title="Choose Clip Studio Paint",filetypes=[("Windows program","*.exe"),("All files","*.*")])
   if not chosen:return
   exe=Path(chosen);cfg["clipStudio"]=str(exe);save(SET,cfg)
  try:subprocess.Popen([str(exe),str(path)])
  except Exception as e:messagebox.showerror("Could not open Clip Studio Paint",str(e))
 def approve_piece(self):
  a=self.asset()
  if not a:messagebox.showinfo("Choose a piece","Select a reusable piece first.");return
  ok,report=piece_lifecycle.approve(a,self.reg.get("masters",[]))
  if not ok:
   messagebox.showerror("Piece is not ready","This piece still has "+str(len(report["blockers"]))+" unresolved artwork requirement(s). Use Continue Artwork to finish them.");return
  save(LIB,self.lib);self.select();messagebox.showinfo("Piece approved",a.get("name","Piece")+" is now Production Ready.")
 def reopen_piece(self):
  a=self.asset()
  if not a:return
  if not messagebox.askyesno("Reopen piece","Return this piece to revision so its artwork can be changed?"):return
  piece_lifecycle.reopen(a);save(LIB,self.lib);self.select()
 def production_dashboard(self):
  a=self.asset()
  if not a:messagebox.showinfo("Choose a piece","Select a reusable piece first.");return
  report=production_pipeline.evaluate(a,self.reg.get("masters",[]))
  lines=["Production status: "+report["state"],"","Primary artwork:"]
  for out in production_pipeline.ORDER:lines.append(OUTS[out][0]+": "+report["primary"][out])
  if report["custom"]:
   names={m.get("id"):m.get("name",m.get("id")) for m in self.reg.get("masters",[])};lines+=["","Custom body variants:"]
   for mid,vals in report["custom"].items():
    lines.append(names.get(mid,mid))
    for out in production_pipeline.ORDER:lines.append("  "+OUTS[out][0]+": "+vals[out])
  lines+=["",("All required artwork is complete and validated." if report["complete"] else str(len(report["blockers"]))+" production requirement(s) still need attention.")]
  messagebox.showinfo("Production Dashboard - "+a.get("name","Piece"),chr(10).join(lines))
 def continue_artwork(self):
  a=self.asset()
  if not a:messagebox.showinfo("Choose a piece","Select a reusable piece first.");return
  job=production_pipeline.next_job(a,self.reg.get("masters",[]))
  if not job:messagebox.showinfo("Production Ready",a.get("name","This piece")+" has all required artwork.");return
  if job["kind"]=="primary":self.workspace(job["output"]);return
  m=next((x for x in self.reg.get("masters",[]) if x.get("id")==job.get("masterId")),None)
  if not m:messagebox.showerror("Missing body master","The custom variant references a body master that is no longer registered.");return
  self.variant_workspace(a,m,focus_output=job["output"])
 def compatibility_matrix(self):
  a=self.asset()
  if not a:messagebox.showinfo("Choose a piece","Select a reusable piece first.");return
  w=tk.Toplevel(self);w.title("Compatibility Matrix — "+a.get("name",a.get("id","Piece")));w.geometry("720x620");w.transient(self.winfo_toplevel());w.grab_set()
  ttk.Label(w,text="Body Compatibility Matrix",font=("TkDefaultFont",14,"bold")).pack(anchor="w",padx=14,pady=(14,4))
  ttk.Label(w,text="YES = use this artwork directly. CUSTOM = this body needs its own fitted variant. NO = do not offer this piece for that body. Explicit choices override the broader compatibility rule.",wraplength=680).pack(anchor="w",padx=14,pady=(0,10))
  cv=tk.Canvas(w,highlightthickness=0);sb=ttk.Scrollbar(w,orient="vertical",command=cv.yview);inner=ttk.Frame(cv);cv.create_window((0,0),window=inner,anchor="nw");cv.configure(yscrollcommand=sb.set);inner.bind("<Configure>",lambda e:cv.configure(scrollregion=cv.bbox("all")));cv.pack(side="left",fill="both",expand=True,padx=(14,0));sb.pack(side="right",fill="y",padx=(0,14))
  matrix=(a.get("compatibility") or {}).get("matrix") or {};vars={}
  home=a.get("masterId")
  for row,m in enumerate(self.reg.get("masters",[])):
   ttk.Label(inner,text=m.get("name","Body"),width=28).grid(row=row,column=0,sticky="w",padx=4,pady=4)
   detail=m.get("family","")+" / "+m.get("bodyType","")
   if m.get("family")=="Female":detail+=" / "+m.get("bust","Unspecified")
   ttk.Label(inner,text=detail,width=30).grid(row=row,column=1,sticky="w",padx=4)
   default=matrix.get(m.get("id"))
   if not default:default="YES" if m.get("id")==home else "NO"
   v=tk.StringVar(value=default);vars[m.get("id")]=v
   ttk.Combobox(inner,textvariable=v,values=["YES","CUSTOM","NO"],state="readonly",width=10).grid(row=row,column=2,padx=4)
   def edit_variant(master=m,var=v):
    if var.get()!="CUSTOM":messagebox.showinfo("Choose CUSTOM","Set this body to CUSTOM first, save the matrix, then create its fitted artwork.");return
    self.variant_workspace(a,master)
   ttk.Button(inner,text="Edit Custom Variant",command=edit_variant).grid(row=row,column=3,padx=4)
  def apply():
   c=a.setdefault("compatibility",{})
   c["matrix"]={mid:v.get() for mid,v in vars.items()}
   save(LIB,self.lib);w.destroy();messagebox.showinfo("Compatibility saved","Body compatibility choices were saved for "+a.get("name","this piece")+".")
  ttk.Button(inner,text="Save Compatibility Matrix",command=apply).grid(row=len(vars)+1,column=0,columnspan=3,pady=16)
 def variant_workspace(self,a,m,focus_output=None):
  w=tk.Toplevel(self);w.title("Custom Variant — "+a.get("name","Piece")+" / "+m.get("name","Body"));w.geometry("650x520");w.transient(self.winfo_toplevel())
  ttk.Label(w,text="Custom fitted artwork",font=("TkDefaultFont",13,"bold")).pack(anchor="w",padx=14,pady=(14,4))
  ttk.Label(w,text="This keeps one reusable-piece identity while storing body-specific artwork for "+m.get("name","this body")+".",wraplength=610).pack(anchor="w",padx=14,pady=(0,10))
  variants=a.setdefault("variants",{}).setdefault(m.get("id"),{})
  if focus_output:ttk.Label(w,text="Next required artwork: "+OUTS[focus_output][0]).pack(anchor="w",padx=14,pady=(0,6))
  for out,(label,size) in OUTS.items():
   row=ttk.Frame(w);row.pack(fill="x",padx=14,pady=3);v=variants.get(out,{})
   inherited=out in set(variants.get("_inherit") or [])
   ttk.Label(row,text=label,width=12).pack(side="left");ttk.Label(row,text=("INHERITED" if inherited else ("COMPLETE" if v.get("status")=="complete" else "MISSING")),width=12).pack(side="left")
   def edit(o=out,sz=size):
    mo=m.get("outputs",{}).get(o,{})
    if mo.get("status") not in ("approved","reference") or not mo.get("locked"):messagebox.showerror("Master not ready",m.get("name","Body")+" "+o+" must be approved and locked first.");return
    d=ROOT/"artist_workspace"/"Variants"/a["id"]/m["id"]/o;d.mkdir(parents=True,exist_ok=True)
    p=app_paths.resolve(mo.get("base",""));layers=[("00_GUIDES_DO_NOT_EXPORT",guide(sz,o))]
    if p.exists():
     ref=Image.open(p).convert("RGBA")
     if ref.size==sz:layers.append(("01_BODY_MASTER_REFERENCE_DO_NOT_EXPORT",ref))
    layers.append(("02_DRAW_CUSTOM_VARIANT_HERE",Image.new("RGBA",sz,(0,0,0,0))))
    ora_path=d/f'EDIT_{a["id"]}_{m["id"]}_{o}.ora'
    if not ora_path.exists() or messagebox.askyesno("Workspace exists","Rebuild this custom-variant workspace? Choose No to preserve and open the existing artwork."):ora(ora_path,layers,sz)
    self.open_csp(ora_path)
   def imp(o=out,sz=size):
    p=filedialog.askopenfilename(title="Import custom "+label+" PNG",filetypes=[("PNG","*.png")])
    if not p:return
    im=Image.open(p).convert("RGBA")
    if im.size!=sz:messagebox.showerror("Wrong canvas",f"Expected {sz[0]}x{sz[1]}.");return
    alpha=im.getchannel("A").getextrema()
    if alpha in ((0,0),(255,255)):messagebox.showerror("Transparency required","Custom component artwork must contain visible pixels and transparent background.");return
    d=ROOT/"assets"/"variants"/a["id"]/m["id"];d.mkdir(parents=True,exist_ok=True);dst=d/(o+".png");im.save(dst)
    variants[o]={"status":"complete","path":str(dst.relative_to(ROOT)).replace(chr(92),"/")};save(LIB,self.lib);w.destroy();self.variant_workspace(a,m)
   def toggle_inherit(o=out):
    inherited=set(variants.get("_inherit") or [])
    if o in inherited:inherited.remove(o)
    else:inherited.add(o)
    variants["_inherit"]=sorted(inherited);save(LIB,self.lib);w.destroy();self.variant_workspace(a,m,focus_output=focus_output)
   ttk.Button(row,text="Edit in Clip Studio Paint",command=edit).pack(side="left",padx=3);ttk.Button(row,text="Import PNG",command=imp).pack(side="left",padx=3);ttk.Button(row,text=("Use Custom" if inherited else "Inherit Primary"),command=toggle_inherit).pack(side="left",padx=3)
 def smart_import(self):
  a=self.asset()
  if not a:messagebox.showinfo("Choose a piece","Select the reusable piece this artwork belongs to first.");return
  p=filedialog.askopenfilename(title="Import finished artwork",filetypes=[("PNG artwork","*.png")])
  if not p:return
  p=Path(p)
  try:im=Image.open(p).convert("RGBA")
  except Exception as e:messagebox.showerror("Unreadable artwork",str(e));return
  size=im.size
  matches=[k for k,v in OUTS.items() if v[1]==size]
  # Prefer routing metadata from the Creator workspace when available.
  manifest=None
  for parent in [p.parent]+list(p.parents)[:4]:
   mp=parent/"project_shonen_artwork.json"
   if mp.exists():
    try:manifest=json.loads(mp.read_text(encoding="utf-8"))
    except Exception:manifest=None
    if manifest:break
  if manifest:
   if manifest.get("assetId")!=a.get("id"):
    messagebox.showerror("Different artwork piece","This file belongs to "+str(manifest.get("assetName",manifest.get("assetId")))+". Select that piece before importing it.");return
   out=manifest.get("output")
   if out not in OUTS or tuple(manifest.get("expectedSize",[]))!=size:
    messagebox.showerror("Artwork does not match workspace","The PNG dimensions or output type do not match its Creator workspace.");return
  elif len(matches)==1:out=matches[0]
  elif not matches:
   messagebox.showerror("Unknown canvas size",f"{size[0]}×{size[1]} is not a supported Project Shonen artwork canvas.");return
  else:
   w=tk.Toplevel(self);w.title("Confirm Artwork Type");v=tk.StringVar(value=matches[0])
   ttk.Label(w,text=f"{size[0]}×{size[1]} can represent more than one output. Choose where this artwork belongs.").pack(padx=12,pady=10)
   ttk.Combobox(w,textvariable=v,values=matches,state="readonly").pack(padx=12,pady=4)
   def go():w.destroy();self._install_png(a,v.get(),p,im)
   ttk.Button(w,text="Import Artwork",command=go).pack(pady=12);return
  self._install_png(a,out,p,im)
 def _install_png(self,a,out,p,im):
  m=self.master(a);mo=m.get("outputs",{}).get(out,{}) if m else {}
  if not m or mo.get("status") not in ("approved","reference") or not mo.get("locked"):
   messagebox.showerror("Body artwork not ready","This piece cannot be installed until its matching body output is available and locked.");return
  size=OUTS[out][1]
  if im.size!=size:messagebox.showerror("Wrong canvas",f"{OUTS[out][0]} artwork must be {size[0]}×{size[1]}.");return
  alpha=im.getchannel("A").getextrema()
  if alpha==(0,0):messagebox.showerror("Empty artwork","The PNG is completely transparent.");return
  if alpha==(255,255):messagebox.showerror("Transparency required","Reusable component artwork must keep a transparent background.");return
  d=ROOT/"assets"/"outputs"/out;d.mkdir(parents=True,exist_ok=True);dst=d/f'{a["id"]}_{out}.png';im.save(dst)
  a.setdefault("outputs",{})[out]={"status":"complete","path":str(dst.relative_to(ROOT)).replace("\\","/")}
  if out=="TV":a["path"]=a["outputs"][out]["path"]
  save(LIB,self.lib);self.select();messagebox.showinfo("Artwork installed",a["name"]+" "+OUTS[out][0]+" artwork is now available to the character creator.")
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
  ttk.Button(b,text="Edit in Clip Studio Paint",command=self.workspace).pack(side="left")
  ttk.Button(b,text="Import Master PNG",command=self.replace).pack(side="left",padx=5)
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
 def workspace(self):
  m=self.master();k=self.chosen()
  if not m or not k:messagebox.showinfo("Choose an output","Select an output first.");return
  o=m["outputs"][k]
  if body_master.is_reference(m):messagebox.showerror("Read-only reference","Imported RPG Maker MZ body masters are local alignment references and cannot be edited.");return
  if o.get("locked"):messagebox.showerror("Locked master","Unlock this master output before editing it.");return
  size=tuple(o["size"]);d=ROOT/"artist_workspace"/"Bodies"/m["id"]/k;d.mkdir(parents=True,exist_ok=True)
  layers=[("00_GUIDES_DO_NOT_EXPORT",guide(size,k))]
  rm=next((x for x in self.reg["masters"] if x.get("id")==m.get("referenceMasterId")),None)
  ro=rm.get("outputs",{}).get(k,{}) if rm else {};rp=app_paths.resolve(ro.get("base","")) if ro.get("base") else None
  if rp and rp.exists():
   try:
    ref=Image.open(rp).convert("RGBA")
    if ref.size==size:layers.append(("01_ALIGNMENT_REFERENCE_DO_NOT_EXPORT",ref))
   except Exception:pass
  layers.append((f"02_DRAW_{k}_BODY_HERE",Image.new("RGBA",size,(0,0,0,0))))
  path=d/f'EDIT_{m["key"]}_{k}.ora'
  if path.exists() and not messagebox.askyesno("Workspace already exists","Rebuild this body workspace? Choose No to open your existing artwork without changing it."):
   self.open_csp(path);return
  ora(path,layers,size)
  (d/"project_shonen_body.json").write_text(json.dumps({"schemaVersion":1,"masterId":m["id"],"output":k,"expectedSize":list(size),"destination":o["base"]},indent=2),encoding="utf-8")
  self.open_csp(path)
 def open_csp(self,path):
  cfg=load(SET,{});exe=Path(cfg.get("clipStudio","")) if cfg.get("clipStudio") else None
  if not exe or not exe.exists():
   if not messagebox.askyesno("Connect Clip Studio Paint","Choose the Clip Studio Paint program now?"):return
   chosen=filedialog.askopenfilename(title="Choose Clip Studio Paint",filetypes=[("Windows program","*.exe"),("All files","*.*")])
   if not chosen:return
   exe=Path(chosen);cfg["clipStudio"]=str(exe);save(SET,cfg)
  try:subprocess.Popen([str(exe),str(path)])
  except Exception as e:messagebox.showerror("Could not open Clip Studio Paint",str(e))
 def replace(self):
  m=self.master();k=self.chosen()
  if not m or not k:return
  o=m["outputs"][k]
  if body_master.is_reference(m):messagebox.showerror("Read-only reference","Imported RPG Maker MZ body masters cannot be replaced.");return
  if o.get("locked"):messagebox.showerror("Locked","Unlock this master output before replacing it.");return
  p=filedialog.askopenfilename(filetypes=[("PNG","*.png")])
  if not p:return
  try:im=Image.open(p).convert("RGBA")
  except Exception as e:messagebox.showerror("Unreadable master artwork",str(e));return
  if list(im.size)!=o["size"]:messagebox.showerror("Wrong canvas",f'Expected {o["size"][0]}×{o["size"][1]}.');return
  alpha=im.getchannel("A").getextrema()
  if alpha==(0,0):messagebox.showerror("Empty master","The body master PNG is completely transparent.");return
  if alpha==(255,255):messagebox.showerror("Transparency required","Body master artwork must preserve a transparent background.");return
  dst=ROOT/o["base"];dst.parent.mkdir(parents=True,exist_ok=True);im.save(dst);o["status"]="review";save(REG,self.reg);self.select()
 def approve(self):
  m=self.master();k=self.chosen()
  if not m or not k:return
  o=m["outputs"][k]
  ok,reason=body_master.validate_output(m,k)
  if not ok:messagebox.showerror("Cannot approve master",reason);return
  if not messagebox.askyesno("Approve canonical master","Lock this artwork as the canonical geometry for compatible components?"):return
  o["status"]="approved";o["locked"]=True
  if all(x.get("status")=="approved" and x.get("locked") for x in m["outputs"].values()): m["status"]="production"
  save(REG,self.reg);self.select()
 def unlock(self):
  m=self.master();k=self.chosen()
  if not m or not k:return
  if body_master.is_reference(m):messagebox.showerror("Read-only reference","Imported RPG Maker MZ body masters cannot be revised.");return
  if not messagebox.askyesno("Unlock master","Changing canonical geometry can misalign existing components. Continue?"):return
  o=m["outputs"][k];o["locked"]=False;o["status"]="revision";m["status"]="revision";save(REG,self.reg);self.select()
