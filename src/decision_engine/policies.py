import numpy as np
import pandas as pd

def compose_policies(*policies):
    
    """Combine several policy dicts into one.

    You can set rules at global, segment, region, or cell level. If two rules
    conflict, the later one wins.
    """

    out = {'global':{}, 'segment':{}, 'region':{}, 'cell':{}}

    def merge_scope(dst, src):
        for k,v in src.items():
            if isinstance(v, dict):
                if k not in dst: dst[k] = {}
                for sk,sv in v.items():
                    if isinstance(sv, dict):
                        dst[k][sk] = {**dst[k].get(sk, {}), **sv}
                    else:
                        dst[k][sk] = sv
            else:
                dst[k] = v
                
    for p in policies:
        for key in ['global','segment','region','cell']:
            if key in p:
                merge_scope(out, {key:p[key]})
    return {k:v for k,v in out.items() if v}


def apply_policy(segments_df: pd.DataFrame, policy: dict, effort_coeffs=None, caps=None):
    
    """Apply one policy to the region×segment data.

    The policy changes churn/new/react/exp/cont by small % or basis points (1 bps = 0.01%) at different
    scopes. It caps new/react growth, recalculates flows, and returns the updated table plus total effort.
    """

    if effort_coeffs is None:
        raise ValueError("effort_coeffs is required (pass DEFAULT_EFFORT from the notebook)")
    if caps is None:
        caps = {}
    sim = segments_df.copy()
    sim[['opening','churned','new','reactivated','expansion','contraction']] = sim[['opening','churned','new','reactivated','expansion','contraction']].astype(float)
    sim['churn_delta']=0.0; sim['new_mult']=1.0; sim['reactivated_mult']=1.0; sim['expansion_mult']=1.0; sim['contraction_delta']=0.0

    def update_row(row, lev):
        if not isinstance(lev, dict):
            return row
        if 'churn_bps' in lev: row['churn_delta'] += (lev['churn_bps']/10000.0)*row['opening']
        if 'new_pct'   in lev: row['new_mult']   *= (1.0+lev['new_pct'])
        if 'react_pct' in lev: row['reactivated_mult'] *= (1.0+lev['react_pct'])
        if 'exp_pct'   in lev: row['expansion_mult']   *= (1.0+lev['exp_pct'])
        if 'cont_bps'  in lev: row['contraction_delta'] += (lev['cont_bps']/10000.0)*row['opening']
        return row

    if 'global' in policy:
        sim = sim.apply(lambda r: update_row(r, policy['global']), axis=1)
    if 'segment' in policy:
        for seg, lev in policy['segment'].items():
            m = sim['segment'].eq(seg); sim.loc[m] = sim.loc[m].apply(lambda r: update_row(r, lev), axis=1)
    if 'region' in policy:
        for reg, lev in policy['region'].items():
            m = sim['region'].eq(reg); sim.loc[m] = sim.loc[m].apply(lambda r: update_row(r, lev), axis=1)
    if 'cell' in policy:
        for (reg,seg), lev in policy['cell'].items():
            m = sim['region'].eq(reg) & sim['segment'].eq(seg); sim.loc[m] = sim.loc[m].apply(lambda r: update_row(r, lev), axis=1)

    # Apply caps (keep it simple, only on new/reactivated)
    max_new_uplift = caps.get('max_new_uplift', 0.0)
    max_react_uplift = caps.get('max_react_uplift', 0.0)
    sim['new_mult']   = np.minimum(sim['new_mult'],   1.0 + max_new_uplift)
    sim['reactivated_mult'] = np.minimum(sim['reactivated_mult'], 1.0 + max_react_uplift)

    # Simulated flows
    sim['churned_sim'] = np.maximum(0.0, sim['churned'] - sim['churn_delta'])
    sim['new_sim']   = np.maximum(0.0, sim['new'] * sim['new_mult'])
    sim['reactivated_sim'] = np.maximum(0.0, sim['reactivated'] * sim['reactivated_mult'])
    sim['expansion_sim']   = np.maximum(0.0, sim['expansion'] * sim['expansion_mult'])
    sim['contraction_sim']  = np.maximum(0.0, sim['contraction'] - sim['contraction_delta'])

    # Effort (abstract units)
    e = effort_coeffs; effort = 0.0
    effort += (e['a_churn']*((sim['churn_delta']/sim['opening'].replace(0,np.nan)).fillna(0.0))*sim['accounts']).sum()
    effort += (e['a_new']*(sim['new_mult']-1.0)*sim['accounts']).sum()
    effort += (e['a_react']*(sim['reactivated_mult']-1.0)*sim['accounts']).sum()
    effort += (e['a_exp']*(sim['expansion_mult']-1.0)*sim['accounts']).sum()
    effort += (e['a_cont']*((sim['contraction_delta']/sim['opening'].replace(0,np.nan)).fillna(0.0))*sim['accounts']).sum()

    out = sim[['region','segment','opening']].copy()
    out = out.assign(churned=sim['churned_sim'], new=sim['new_sim'], reactivated=sim['reactivated_sim'], expansion=sim['expansion_sim'], contraction=sim['contraction_sim'], accounts=sim['accounts'])
    return out, float(effort)
