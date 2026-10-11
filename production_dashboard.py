import piece_lifecycle,production_pipeline,compatibility_audit

OUTPUT_LABELS={"TV":"W","FG":"F","TVD":"D","SV":"B","Variation":"P"}

def classify(asset,masters):
    source=str(asset.get("source",""))
    if source.startswith("RPG Maker MZ"):
        return {"state":"Imported MZ Reference","missing":0,"attention":0,"action":"Reference","progress":"","complete":0,"total":0,"integrity":[]}
    report=production_pipeline.evaluate(asset,masters)
    state=piece_lifecycle.lifecycle(asset,masters)
    missing=sum(1 for b in report["blockers"] if b.get("reason")=="missing")
    integrity=compatibility_audit.problems(asset,masters)
    attention=len(report["blockers"])-missing+len(integrity)
    action="Approve" if state=="Review" else ("Ready" if state=="Production Ready" else "Continue Production")
    marks=[];complete=0
    for out in production_pipeline.ORDER:
        value=report["primary"].get(out,"missing");ok=value=="complete";complete+=int(ok);marks.append(OUTPUT_LABELS[out]+("✓" if ok else "·"))
    return {"state":state,"missing":missing,"attention":attention,"action":action,"progress":" ".join(marks),"complete":complete,"total":len(production_pipeline.ORDER),"integrity":integrity}

def bucket(info):
    state=info["state"]
    if state=="Imported MZ Reference":return "Imported References"
    if state=="Needs Attention":return "Needs Attention"
    if state=="Review":return "Ready for Review"
    if state=="Production Ready":return "Production Ready"
    return "In Production"

def queues(assets,masters):
    result={"Needs Attention":[],"In Production":[],"Ready for Review":[],"Production Ready":[],"Imported References":[]}
    for a in assets:
        info=classify(a,masters);result[bucket(info)].append((a,info))
    return result

def body_label(asset,masters):
    comp=asset.get("compatibility") or {};home=comp.get("homeMasterId") or asset.get("masterId") or asset.get("bodyMasterId")
    if home:
        m=next((x for x in masters if x.get("id")==home),None)
        if m:return m.get("name",home)
        return str(home)
    family=comp.get("family") or asset.get("bodyFamily")
    return str(family or "Any Body")

def filter_assets(assets,masters,query="",queue="All",category="All",body="All",sort="Priority"):
    q=query.strip().casefold();rows=[]
    priority={"Needs Attention":0,"Ready for Review":1,"In Production":2,"Production Ready":3,"Imported References":4}
    for a in assets:
        info=classify(a,masters);b=bucket(info);cat=str(a.get("category","Uncategorized"));bl=body_label(a,masters)
        hay=" ".join((str(a.get("name","")),str(a.get("id","")),cat,bl)).casefold()
        if q and q not in hay:continue
        if queue!="All" and b!=queue:continue
        if category!="All" and cat!=category:continue
        if body!="All" and bl!=body:continue
        rows.append((a,info,b,cat,bl))
    if sort=="Name":rows.sort(key=lambda x:str(x[0].get("name","")).casefold())
    elif sort=="Category":rows.sort(key=lambda x:(x[3].casefold(),str(x[0].get("name","")).casefold()))
    elif sort=="Body":rows.sort(key=lambda x:(x[4].casefold(),str(x[0].get("name","")).casefold()))
    else:rows.sort(key=lambda x:(priority.get(x[2],9),-x[1].get("attention",0),-x[1].get("missing",0),str(x[0].get("name","")).casefold()))
    return rows
