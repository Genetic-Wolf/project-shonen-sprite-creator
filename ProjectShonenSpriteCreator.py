#!/usr/bin/env python3
import tkinter as tk,json,os,subprocess,sys
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
import embedded_workflows, integrated_editors, integrated_character_rpg, mz_generator_importer
import app_paths
ROOT=app_paths.RESOURCE_ROOT
DATA_ROOT=app_paths.bootstrap()
SETTINGS=DATA_ROOT/"artist_settings.json"
class App(tk.Tk):
 def __init__(self):
  super().__init__();self.title("Project Shonen Sprite Creator v0.22.0");self.geometry("1280x800");self.minsize(1080,680)
  try:self.cfg=json.load(open(SETTINGS,encoding="utf-8"))
  except:self.cfg={}
  self.build();self.page("characters")
 def build(self):
  h=ttk.Frame(self,padding=12);h.pack(fill="x");ttk.Label(h,text="Project Shonen Sprite Creator",font=("TkDefaultFont",18,"bold")).pack(side="left")
  ttk.Label(h,text="Artist Production Workspace").pack(side="left",padx=12)
  body=ttk.Frame(self);body.pack(fill="both",expand=True)
  n=ttk.Frame(body,padding=10);n.pack(side="left",fill="y");self.content=ttk.Frame(body,padding=12);self.content.pack(side="left",fill="both",expand=True)
  for label,key in [("Characters","characters"),("Reusable Pieces","pieces"),("Body Masters","masters"),("RPG Maker MZ","rpg"),("Library Health","health"),("Settings","settings")]:
   ttk.Button(n,text=label,width=20,command=lambda k=key:self.page(k)).pack(fill="x",pady=3)
 def clear(self):
  for w in self.content.winfo_children():w.destroy()
 def heading(self,a,b):
  ttk.Label(self.content,text=a,font=("TkDefaultFont",16,"bold")).pack(anchor="w");ttk.Label(self.content,text=b,wraplength=900).pack(anchor="w",pady=(2,10))
 def page(self,k):
  self.clear()
  if k=="pieces":
   self.heading("Reusable Pieces","Create and complete all visual representations without leaving the main application.")
   ttk.Button(self.content,text="+ New Reusable Piece",command=lambda:embedded_workflows.new_piece_dialog(self,lambda:self.page("pieces"))).pack(anchor="w",pady=(0,6))
   integrated_editors.PieceEditor(self.content).pack(fill="both",expand=True)
  elif k=="masters":
   self.heading("Body Masters","Create new master body sprites, replace canonical artwork, approve it and lock production geometry.")
   ttk.Button(self.content,text="+ New Body Master",command=lambda:embedded_workflows.new_master_dialog(self,lambda:self.page("masters"))).pack(anchor="w",pady=(0,6))
   integrated_editors.MasterEditor(self.content).pack(fill="both",expand=True)
  elif k=="characters":
   self.heading("Characters","Assemble a character from body-compatible reusable pieces and export an RPG Maker walking sprite.")
   integrated_character_rpg.CharacterBuilder(self.content).pack(fill="both",expand=True)
  elif k=="rpg":
   self.heading("RPG Maker MZ","Review staged graphics and install them with automatic timestamped replacement backups.")
   integrated_character_rpg.RPGInstaller(self.content).pack(fill="both",expand=True)
  elif k=="health":
   self.heading("Library Health","Find broken references and production-readiness problems before they reach RPG Maker.")
   integrated_character_rpg.Health(self.content).pack(fill="both",expand=True)
  else:
   self.heading("Settings","Configure external programs using normal Windows file and folder pickers.")
   mz=tk.StringVar(value=self.cfg.get("rpgMakerProject",""));csp=tk.StringVar(value=self.cfg.get("clipStudio",""))
   ttk.Label(self.content,text="RPG Maker MZ project").pack(anchor="w");ttk.Entry(self.content,textvariable=mz,width=90).pack(anchor="w",pady=4)
   ttk.Button(self.content,text="Choose RPG Maker Project",command=lambda:self.pickdir(mz)).pack(anchor="w")
   ttk.Separator(self.content).pack(fill="x",pady=14)
   ttk.Label(self.content,text="RPG Maker MZ Generator Library",font=("TkDefaultFont",11,"bold")).pack(anchor="w")
   ttk.Label(self.content,text="Import the stock generator assets from your own RPG Maker MZ installation or backup ZIP. Assets stay in your private local library.",wraplength=850).pack(anchor="w",pady=(2,6))
   ttk.Button(self.content,text="Import RPG Maker MZ Generator ZIP",command=self.import_mz_generator).pack(anchor="w",pady=(0,8))
   ttk.Label(self.content,text="Clip Studio Paint",padding=(0,14,0,0)).pack(anchor="w");ttk.Entry(self.content,textvariable=csp,width=90).pack(anchor="w",pady=4)
   ttk.Button(self.content,text="Choose Clip Studio Paint",command=lambda:self.pickexe(csp)).pack(anchor="w")
   def save():
    self.cfg["rpgMakerProject"]=mz.get();self.cfg["clipStudio"]=csp.get();json.dump(self.cfg,open(SETTINGS,"w",encoding="utf-8"),indent=2);messagebox.showinfo("Saved","Settings saved.")
   ttk.Button(self.content,text="Save Settings",command=save).pack(anchor="w",pady=18)
 def import_mz_generator(self):
  p=filedialog.askopenfilename(title="Select RPG Maker MZ generator ZIP",filetypes=[("ZIP archive","*.zip")])
  if not p:return
  try:
   r=mz_generator_importer.import_generator_zip(p)
   messagebox.showinfo("RPG Maker MZ import complete",f"Imported {r['filesImported']} valid files.\nRegistered {r['componentsAdded']} reusable components.\nSkipped {r['invalidPngsSkipped']} invalid PNG entries.\n\nThe stock artwork remains in your private local Sprite Creator data.")
   self.page("characters")
  except Exception as e:messagebox.showerror("Import failed",str(e))
 def run(self,n):
  p=ROOT/n
  if p.exists():subprocess.Popen([sys.executable,str(p)])
 def pickdir(self,v):
  p=filedialog.askdirectory()
  if p:v.set(p)
 def pickexe(self,v):
  p=filedialog.askopenfilename(filetypes=[("Windows program","*.exe"),("All files","*.*")])
  if p:v.set(p)
if __name__ == "__main__":
 if "--self-test" in sys.argv:
  result=app_paths.self_test(); print(json.dumps(result, indent=2))
  try: (app_paths.DATA_ROOT/"self_test_result.json").write_text(json.dumps(result, indent=2),encoding="utf-8")
  except Exception as e: print("Could not write self-test result:",e)
  sys.exit(0 if result["ok"] else 1)
 App().mainloop()
