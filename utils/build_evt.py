import awkward as ak
import numpy as np
import re
from lgdo import lh5, Table, VectorOfVectors

def get_table_names(tcm):
    """Extract table names from tcm.attrs['tables'] and return them as a dictionary."""
    raw = tcm.attrs["tables"]
    cleaned = raw.strip("[]").replace(" ", "").replace("'", "")
    tables = cleaned.split(",")
    tables = [tab.split("/")[-1] for tab in tables if len(tab) > 21]
    return {idx:uid for idx, uid in enumerate(tables)}

def build_evt(
    tcm: VectorOfVectors,
    stp_file: str,
    hit_file: str,
    evt_file: str
):
  """Simple event building code that returns fileds including the evtid, smeared energy, LAr energy and mulitplicity"""
    tcm_ak = tcm.view_as("ak")
    #geds
    channels = tcm_ak.table_key
    mask_geds = (channels != 0)
    tcm_geds = tcm_ak[mask_geds]
    
    num_tcm = ak.num(tcm_geds.row_in_table)
    flat_tcm = ak.Array({k: ak.flatten(tcm_geds[k]) for k in tcm_geds.fields})
    
    flat_evt_geds = None
    for table in lh5.ls(hit_file, "hit/"):
        # extract the uid from the table name
        uid = int(re.search(r"(?<=hit/det)\d+", table).group())
        rows_in_table = flat_tcm.row_in_table[flat_tcm.table_key == uid].to_numpy()
        data = lh5.read(f"{table}/smeared_energy", hit_file, idx=rows_in_table).view_as("ak")
        flat_evt_geds = ak.concatenate((flat_evt_geds, data)) if flat_evt_geds is not None else data
    smeared_energy = ak.unflatten(flat_evt_geds, num_tcm)
    
    #lar 
    mask_lar = ak.any(channels == 0, axis = -1)
    tcm_lar = tcm_ak[mask_lar]
    idx_lar = ak.local_index(tcm_ak, axis = 0)[mask_lar]
    
    length = len(tcm)
    energy_lar = ak.sum(lh5.read(f"stp/det000/edep", stp_file).view_as("ak"), axis = -1)
    lar = np.zeros(length)
    lar[idx_lar] = energy_lar

    #write event as awkawrd
    evt = ak.Array({"evtid": ak.local_index(tcm_ak, axis = 0),
                "smeared_energy": smeared_energy,
                "lar": lar, 
                "multiplicity": num_tcm})
    EVT = Table(evt)
    lh5.write(EVT, "evt", evt_file, wo_mode= "overwrite_file")
    
