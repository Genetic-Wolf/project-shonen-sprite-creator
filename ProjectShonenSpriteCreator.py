#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk,filedialog,messagebox,simpledialog
from PIL import Image,ImageTk,ImageDraw
from pathlib import Path
import json,shutil,os,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
SIZE=(144,192); FW=FH=48
ORDER=['Hair_Back','Clothing_Back','Cloak','Weapon_Back','Accessory_Back','Armor','Eyes','Eyebrows','Mouth','FacialMark','Clothing_Front','Hair_Front','Headgear','Accessory_Front','Weapon_Hip','Weapon_Hand']
LABEL={x:x.replace('_',' ') for x in ORDER}
class App(tk.Tk):
 def __init__(self):
  super().__init__();self.title('Project Shonen Sprite Creator v0.4.0');self.geometry('1240x790');self.minsize(1060,680)
  self.body=tk.StringVar(value='Female_Standard');self.name=tk.StringVar(value='NewCharacter');self.frame=1;self.direction=0;self.after_id=None;self.search=tk.StringVar()
  self.selected={k:None for k in ORDER};self.lib=self.loadjson('library.json',{'assets':[]});self.settings=self.loadjson('settings.json',{'mz_project':''});self.build();self.refresh_library();self.refresh()
 def loadjson(self,n,d):
  try:return json.load(open(ROOT/n,encoding='utf-8'))
  except:return d
 def savejson(self,n,d):json.dump(d,open(ROOT/n,'w',encoding='utf-8'),indent=2)
 def build(self):
  top=ttk.Frame(self,padding=8);top.pack(fill='x');ttk.Label(top,text='PROJECT SHONEN SPRITE CREATOR',font=('TkDefaultFont',15,'bold')).pack(side='left')
  ttk.Label(top,text='Character').pack(side='left',padx=(24,4));ttk.Entry(top,textvariable=self.name,width=18).pack(side='left')
  ttk.Label(top,text='Master').pack(side='left',padx=(14,4));cb=ttk.Combobox(top,textvariable=self.body,values=['Female_Standard','Male_Standard'],state='readonly',width=18);cb.pack(side='left');cb.bind('<<ComboboxSelected>>',lambda e:(self.refresh_library(),self.refresh()))
  ttk.Button(top,text='RPG Maker Setup',command=self.setup_mz).pack(side='right',padx=3);ttk.Button(top,text='Export + Install',command=self.export_install).pack(side='right',padx=3);ttk.Button(top,text='Save Character',command=self.save_character).pack(side='right',padx=3);ttk.Button(top,text='Load',command=self.load_character).pack(side='right',padx=3)
  nb=ttk.Notebook(self);nb.pack(fill='both',expand=True,padx=8,pady=(0,8));create=ttk.Frame(nb);library=ttk.Frame(nb);settings=ttk.Frame(nb);nb.add(create,text='Character Creator');nb.add(library,text='Asset Library');nb.add(settings,text='Project Settings')
  main=ttk.Panedwindow(create,orient='horizontal');main.pack(fill='both',expand=True);left=ttk.Frame(main,padding=8);mid=ttk.Frame(main,padding=8);right=ttk.Frame(main,padding=8);main.add(left,weight=3);main.add(mid,weight=4);main.add(right,weight=3)
  ttk.Label(left,text='Components',font=('TkDefaultFont',12,'bold')).pack(anchor='w');ttk.Entry(left,textvariable=self.search).pack(fill='x',pady=(5,3));self.search.trace_add('write',lambda *_:self.refresh_library())
  self.tree=ttk.Treeview(left,show='tree');self.tree.pack(fill='both',expand=True,pady=4);self.tree.bind('<<TreeviewSelect>>',lambda e:self.asset_preview())
  buttons=ttk.Frame(left);buttons.pack(fill='x');ttk.Button(buttons,text='Use',command=self.use_selected).pack(side='left',fill='x',expand=True,padx=2);ttk.Button(buttons,text='Clear',command=self.clear_slot).pack(side='left',fill='x',expand=True,padx=2)
  ttk.Button(left,text='+ New Piece (Clip Studio)',command=self.new_piece).pack(fill='x',pady=(9,2));ttk.Button(left,text='Import Finished PNG',command=self.import_component).pack(fill='x',pady=2);ttk.Button(left,text='Open Artist Workspace',command=lambda:self.openfolder(ROOT/'artist_workspace')).pack(fill='x',pady=2)
  ttk.Label(mid,text='Live Walking Preview',font=('TkDefaultFont',12,'bold')).pack();self.canvas=tk.Canvas(mid,width=330,height=330,bg='#2d3138',highlightthickness=0);self.canvas.pack(pady=10)
  dirs=ttk.Frame(mid);dirs.pack();
  for t,d in [('Down',0),('Left',1),('Right',2),('Up',3)]:ttk.Button(dirs,text=t,command=lambda x=d:self.setdir(x)).pack(side='left',padx=2)
  self.anim=tk.BooleanVar(value=True);ttk.Checkbutton(mid,text='Animate walk cycle',variable=self.anim,command=self.schedule).pack(pady=7)
  ttk.Label(mid,text='Selected Asset Preview',font=('TkDefaultFont',10,'bold')).pack();self.asset_canvas=tk.Canvas(mid,width=144,height=96,bg='#3a3f47',highlightthickness=0);self.asset_canvas.pack(pady=4)
  ttk.Label(right,text='Current Character',font=('TkDefaultFont',12,'bold')).pack(anchor='w');self.layers=tk.Listbox(right,height=17);self.layers.pack(fill='both',expand=True,pady=5)
  ttk.Label(right,text='Validation',font=('TkDefaultFont',11,'bold')).pack(anchor='w');self.status=tk.Text(right,height=8,state='disabled');self.status.pack(fill='x',pady=4);ttk.Button(right,text='Validate',command=self.validate).pack(fill='x');ttk.Button(right,text='Export RPG Maker TV Sheet',command=self.export).pack(fill='x',pady=3)
  # Library tab
  bar=ttk.Frame(library,padding=10);bar.pack(fill='x');ttk.Label(bar,text='Reusable Asset Library',font=('TkDefaultFont',13,'bold')).pack(side='left');ttk.Button(bar,text='Open Components Folder',command=lambda:self.openfolder(ROOT/'assets/components')).pack(side='right')
  self.lib_text=tk.Text(library,state='disabled');self.lib_text.pack(fill='both',expand=True,padx=10,pady=(0,10))
  # Settings
  sf=ttk.Frame(settings,padding=18);sf.pack(fill='both',expand=True);ttk.Label(sf,text='RPG Maker MZ Integration',font=('TkDefaultFont',13,'bold')).grid(row=0,column=0,columnspan=3,sticky='w');self.mzlabel=ttk.Label(sf,text='');self.mzlabel.grid(row=1,column=0,columnspan=2,sticky='w',pady=10);ttk.Button(sf,text='Choose RPG Maker Project',command=self.setup_mz).grid(row=1,column=2,padx=8);ttk.Label(sf,text='Artist workflow uses layered OpenRaster (.ora) files, which can be opened in Clip Studio Paint. Save a .clip working copy if desired. Only transparent 144×192 PNG component exports are imported back into this creator.',wraplength=720).grid(row=2,column=0,columnspan=3,sticky='w',pady=15);ttk.Button(sf,text='Open Quick Start',command=lambda:self.openfile(ROOT/'ARTIST_WORKFLOW.txt')).grid(row=3,column=0,sticky='w');self.update_settings_label()
 def basepath(self):return ROOT/'assets/bases'/f'{self.body.get()}.png'
 def refresh_library(self):
  if not hasattr(self,'tree'):return
  for i in self.tree.get_children():self.tree.delete(i)
  q=self.search.get().lower().strip()
  for cat in ORDER:
   parent=self.tree.insert('','end',iid='CAT_'+cat,text=LABEL[cat],open=True)
   for a in self.lib.get('assets',[]):
    if a.get('category')==cat and (not a.get('body') or a.get('body')==self.body.get()) and (not q or q in a.get('name','').lower()):self.tree.insert(parent,'end',iid=a['id'],text=a['name'])
  if hasattr(self,'lib_text'):
   lines=[]
   for cat in ORDER:
    items=[a for a in self.lib.get('assets',[]) if a.get('category')==cat]
    if items:lines.append('\n'+LABEL[cat].upper());lines += [f"  {a['name']}  [{a['body']}]  {a['id']}" for a in items]
   self.lib_text.config(state='normal');self.lib_text.delete('1.0','end');self.lib_text.insert('end','\n'.join(lines) if lines else 'No custom components imported yet.');self.lib_text.config(state='disabled')
 def compose(self):
  im=Image.open(self.basepath()).convert('RGBA')
  for cat in ORDER:
   aid=self.selected.get(cat);a=next((x for x in self.lib.get('assets',[]) if x.get('id')==aid),None)
   if a and a.get('body')==self.body.get() and (ROOT/a['path']).exists():im.alpha_composite(Image.open(ROOT/a['path']).convert('RGBA'))
  return im
 def refresh(self):
  im=self.compose();x=self.frame*48;y=self.direction*48;crop=im.crop((x,y,x+48,y+48)).resize((288,288),Image.Resampling.NEAREST);self.tkimg=ImageTk.PhotoImage(crop);self.canvas.delete('all');self.canvas.create_image(165,165,image=self.tkimg)
  self.layers.delete(0,'end');self.layers.insert('end','BASE — '+self.body.get())
  for cat in ORDER:
   aid=self.selected.get(cat)
   if aid:
    a=next((x for x in self.lib.get('assets',[]) if x.get('id')==aid),None);self.layers.insert('end',f'{LABEL[cat]} — {a["name"] if a else aid}')
  self.schedule()
 def schedule(self):
  if self.after_id:
   try:self.after_cancel(self.after_id)
   except:pass
  if self.anim.get():self.after_id=self.after(280,self.tick)
 def tick(self):self.frame={0:1,1:2,2:1}.get(self.frame,1);self.refresh()
 def setdir(self,d):self.direction=d;self.refresh()
 def chosen_asset(self):
  s=self.tree.selection();return next((a for a in self.lib.get('assets',[]) if s and a.get('id')==s[0]),None)
 def chosen_category(self):
  s=self.tree.selection()
  if not s:return None
  if s[0].startswith('CAT_'):return s[0][4:]
  a=self.chosen_asset();return a.get('category') if a else None
 def asset_preview(self):
  a=self.chosen_asset();self.asset_canvas.delete('all')
  if not a:return
  im=Image.open(ROOT/a['path']).convert('RGBA').crop((48,0,96,48)).resize((88,88),Image.Resampling.NEAREST);self.assetimg=ImageTk.PhotoImage(im);self.asset_canvas.create_image(72,48,image=self.assetimg)
 def use_selected(self):
  a=self.chosen_asset()
  if a:self.selected[a['category']]=a['id'];self.refresh()
 def clear_slot(self):
  c=self.chosen_category()
  if c:self.selected[c]=None;self.refresh()
 def next_id(self):
  used={a.get('id') for a in self.lib.get('assets',[])};n=4001
  while f'PS-ASSET-{n:05d}' in used:n+=1
  return f'PS-ASSET-{n:05d}'
 def new_piece(self):
  cat=self.chosen_category() or 'Hair_Front';name=simpledialog.askstring('New Generator Piece',f'Name the new {LABEL[cat]} piece:')
  if not name:return
  safe=''.join(c if c.isalnum() or c in '_-' else '_' for c in name);out=ROOT/'artist_workspace'/self.body.get()/cat/safe;out.mkdir(parents=True,exist_ok=True);base=Image.open(self.basepath()).convert('RGBA');guide=Image.new('RGBA',SIZE,(0,0,0,0));d=ImageDraw.Draw(guide)
  for x in (48,96):d.line((x,0,x,192),fill=(0,180,255,150))
  for y in (48,96,144):d.line((0,y,144,y),fill=(0,180,255,150))
  for r in range(4):
   for c in range(3):ox,oy=c*48,r*48;d.line((ox+24,oy,ox+24,oy+47),fill=(255,0,255,100));d.line((ox,oy+44,ox+47,oy+44),fill=(255,210,0,150))
  blank=Image.new('RGBA',SIZE,(0,0,0,0));self.write_ora(out/f'EDIT_{safe}.ora',[('00_GUIDES_DO_NOT_EXPORT',guide),('01_BASE_REFERENCE_DO_NOT_EXPORT',base),(f'02_DRAW_{cat}_EXPORT_THIS',blank)]);Image.alpha_composite(base,guide).save(out/'REFERENCE.png');blank.save(out/f'EXPORT_{safe}.png');(out/'READ_ME_FIRST.txt').write_text(f'Open EDIT_{safe}.ora in Clip Studio Paint. Draw only on 02_DRAW_{cat}_EXPORT_THIS. Keep canvas 144x192. Hide guide and base reference before exporting the drawing layer to transparent PNG. Then import that PNG into Project Shonen Sprite Creator as {LABEL[cat]}.',encoding='utf-8');self.openfolder(out);messagebox.showinfo('Workspace Ready','Clip Studio workspace created. Open the EDIT_*.ora file, draw the piece, then export only the drawing layer as transparent PNG.')
 def write_ora(self,path,layers):
  tmp=path.parent/'_ora_tmp';shutil.rmtree(tmp,ignore_errors=True);(tmp/'data').mkdir(parents=True);(tmp/'Thumbnails').mkdir();
  for i,(_,im) in enumerate(layers):im.save(tmp/'data'/f'l{i}.png')
  root=ET.Element('image',{'version':'0.0.1','w':'144','h':'192','name':path.stem});stack=ET.SubElement(root,'stack',{'name':'root'})
  for i,(n,_) in enumerate(layers):ET.SubElement(stack,'layer',{'name':n,'src':f'data/l{i}.png','visibility':'visible'})
  ET.ElementTree(root).write(tmp/'stack.xml',encoding='UTF-8',xml_declaration=True);(tmp/'mimetype').write_text('image/openraster');Image.alpha_composite(layers[1][1],layers[0][1]).save(tmp/'mergedimage.png')
  with zipfile.ZipFile(path,'w') as z:
   z.write(tmp/'mimetype','mimetype',compress_type=zipfile.ZIP_STORED);z.write(tmp/'stack.xml','stack.xml');z.write(tmp/'mergedimage.png','mergedimage.png')
   for i in range(len(layers)):z.write(tmp/'data'/f'l{i}.png',f'data/l{i}.png')
  shutil.rmtree(tmp)
 def import_component(self):
  cat=self.chosen_category() or 'Hair_Front';p=filedialog.askopenfilename(title='Choose finished transparent component',filetypes=[('PNG','*.png')]);
  if not p:return
  try:im=Image.open(p).convert('RGBA')
  except Exception as e:messagebox.showerror('Import failed',str(e));return
  issues=[]
  if im.size!=SIZE:issues.append(f'Expected 144×192, received {im.size[0]}×{im.size[1]}.')
  if im.getbbox() is None:issues.append('Image contains no visible artwork.')
  if issues:messagebox.showerror('Component rejected','\n'.join(issues));return
  name=simpledialog.askstring('Register Piece','Reusable piece name:',initialvalue=Path(p).stem)
  if not name:return
  aid=self.next_id();dst=ROOT/'assets/components'/f'{aid}.png';dst.parent.mkdir(parents=True,exist_ok=True);im.save(dst);self.lib.setdefault('assets',[]).append({'id':aid,'name':name,'category':cat,'body':self.body.get(),'path':str(dst.relative_to(ROOT)).replace('\\','/')});self.savejson('library.json',self.lib);self.refresh_library();self.selected[cat]=aid;self.refresh();messagebox.showinfo('Piece Added',f'{name} passed validation and is now available in {LABEL[cat]}.')
 def validate(self):
  issues=[]
  if not self.basepath().exists():issues.append('Canonical base sprite is missing.')
  for cat,aid in self.selected.items():
   if not aid:continue
   a=next((x for x in self.lib.get('assets',[]) if x.get('id')==aid),None)
   if not a:issues.append(f'{LABEL[cat]} registry entry missing.');continue
   p=ROOT/a['path']
   if not p.exists():issues.append(f'{a["name"]}: source PNG missing.');continue
   im=Image.open(p)
   if im.size!=SIZE:issues.append(f'{a["name"]}: canvas is not 144×192.')
   if a.get('body')!=self.body.get():issues.append(f'{a["name"]}: incompatible body master.')
  msg='PASS\nCharacter TV sheet is correctly formatted for export.' if not issues else 'NEEDS ATTENTION\n'+'\n'.join('• '+x for x in issues);self.status.config(state='normal');self.status.delete('1.0','end');self.status.insert('end',msg);self.status.config(state='disabled');return not issues
 def export(self,quiet=False):
  if not self.validate():messagebox.showerror('Export Blocked','Resolve validation issues first.');return None
  n=''.join(c for c in self.name.get() if c.isalnum() or c in '_-') or 'Character';p=ROOT/'exports'/f'${n}.png';p.parent.mkdir(exist_ok=True);self.compose().save(p)
  if not quiet:messagebox.showinfo('Export Complete',f'Created {p.name} in the exports folder.')
  return p
 def export_install(self):
  p=self.export(True)
  if not p:return
  project=self.settings.get('mz_project','')
  if not project:
   if messagebox.askyesno('RPG Maker Project Not Set','Choose the RPG Maker MZ project now?'):self.setup_mz();project=self.settings.get('mz_project','')
  if project:
   dest=Path(project)/'img'/'characters';dest.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest/p.name);messagebox.showinfo('Installed',f'{p.name} was exported and copied directly to:\n{dest}')
  else:messagebox.showinfo('Exported',f'{p.name} was created in the local exports folder.')
 def setup_mz(self):
  p=filedialog.askdirectory(title='Choose RPG Maker MZ project folder')
  if p:self.settings['mz_project']=p;self.savejson('settings.json',self.settings);self.update_settings_label();messagebox.showinfo('Project Saved','RPG Maker MZ project path saved. Export + Install can now copy sprites directly into img/characters.')
 def update_settings_label(self):
  if hasattr(self,'mzlabel'):self.mzlabel.config(text='Current project: '+(self.settings.get('mz_project') or 'Not configured'))
 def save_character(self):
  n=''.join(c for c in self.name.get() if c.isalnum() or c in '_-') or 'Character';d=ROOT/'characters';d.mkdir(exist_ok=True);json.dump({'name':n,'body':self.body.get(),'layers':self.selected},open(d/f'{n}.json','w',encoding='utf-8'),indent=2);messagebox.showinfo('Saved',f'{n} saved.')
 def load_character(self):
  p=filedialog.askopenfilename(initialdir=ROOT/'characters',filetypes=[('Project Shonen Character','*.json')]);
  if p:
   d=json.load(open(p,encoding='utf-8'));self.name.set(d.get('name','Character'));self.body.set(d.get('body','Female_Standard'));self.selected={k:d.get('layers',{}).get(k) for k in ORDER};self.refresh_library();self.refresh()
 def openfolder(self,p):
  p=Path(p);p.mkdir(parents=True,exist_ok=True)
  try:os.startfile(p)
  except:messagebox.showinfo('Folder',str(p))
 def openfile(self,p):
  try:os.startfile(p)
  except:messagebox.showinfo('File',str(p))
App().mainloop()
