import piece_lifecycle,production_pipeline

def classify(asset,masters):
    source=str(asset.get("source",""))
    if source.startswith("RPG Maker MZ"):
        return {"state":"Imported MZ Reference","missing":0,"attention":0,"action":"Reference"}
    report=production_pipeline.evaluate(asset,masters)
    state=piece_lifecycle.lifecycle(asset,masters)
    missing=sum(1 for b in report["blockers"] if b.get("reason")=="missing")
    attention=len(report["blockers"])-missing
    action="Approve" if state=="Review" else ("Ready" if state=="Production Ready" else "Continue Production")
    return {"state":state,"missing":missing,"attention":attention,"action":action}

def queues(assets,masters):
    result={"Needs Attention":[],"In Production":[],"Ready for Review":[],"Production Ready":[],"Imported References":[]}
    for a in assets:
        info=classify(a,masters);state=info["state"]
        if state=="Imported MZ Reference":bucket="Imported References"
        elif state=="Needs Attention":bucket="Needs Attention"
        elif state=="Review":bucket="Ready for Review"
        elif state=="Production Ready":bucket="Production Ready"
        else:bucket="In Production"
        result[bucket].append((a,info))
    return result
