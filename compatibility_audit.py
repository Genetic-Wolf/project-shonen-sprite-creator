import production_pipeline

def problems(asset,masters):
    if str(asset.get("source","")).startswith("RPG Maker MZ"):return []
    issues=[];comp=asset.get("compatibility") or {};matrix=comp.get("matrix") or {};known={m.get("id") for m in masters}
    for mid,state in matrix.items():
        if mid not in known:issues.append("Compatibility references missing body "+str(mid))
        if state not in ("YES","NO","CUSTOM"):issues.append("Unknown compatibility state for "+str(mid))
    variants=asset.get("variants") or {}
    for mid,v in variants.items():
        if mid not in known:issues.append("Variant references missing body "+str(mid))
        if matrix.get(mid)!="CUSTOM" and any(k in production_pipeline.ORDER for k in v):issues.append("Custom artwork exists without CUSTOM compatibility for "+str(mid))
    home=comp.get("homeMasterId") or asset.get("masterId") or asset.get("bodyMasterId")
    if home and home not in known:issues.append("Home body is missing: "+str(home))
    return sorted(set(issues))
