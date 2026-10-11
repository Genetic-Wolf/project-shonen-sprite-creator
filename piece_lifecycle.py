import production_pipeline

def lifecycle(asset,masters):
    report=production_pipeline.evaluate(asset,masters)
    approved=asset.get("approved") is True
    if report["complete"] and approved:return "Production Ready"
    if report["complete"]:return "Review"
    if any(x["reason"] not in ("missing",) for x in report["blockers"]):return "Needs Attention"
    if any((asset.get("outputs") or {}).get(k,{}).get("path") for k in production_pipeline.ORDER):return "Needs Artwork"
    return "Draft"

def can_approve(asset,masters):
    report=production_pipeline.evaluate(asset,masters)
    return report["complete"],report

def approve(asset,masters):
    ok,report=can_approve(asset,masters)
    if not ok:return False,report
    asset["approved"]=True
    asset["status"]="production"
    return True,report

def reopen(asset):
    asset["approved"]=False
    asset["status"]="revision"
