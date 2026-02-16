from legendmeta import LegendMetadata

#data path for metadata
data_path = "/global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/latest"
meta = LegendMetadata(f"{data_path}/inputs")

def get_exposure_order(period, orders:list|None = None):
    """
    Get the exposure either for all orders (orders = None) or just a subset
    """
    exposure = 0
    for run, info in meta.datasets.runinfo[f"p{period}"].items():
    
        if ("phy" in info):
    
            chmap = meta.channelmap(info.phy.start_key)
    
            for det in chmap:
                
                if chmap[det].system=="geds" and chmap[det].analysis.usability=="on":

                    if orders is None or chmap[det].production.order in orders:
                        mass =chmap[det].production.mass_in_g/1000
                        exposure+=mass*info.phy.livetime_in_s/60/60/24/365.25
    
    return exposure

def get_exposure_det(period, dets:list|None = None):
    """
    Get the exposure either for all detectors (dets = None) or just a subset
    """
    exposure = 0
    for run, info in meta.datasets.runinfo[f"p{period}"].items():
    
        if ("phy" in info):
    
            chmap = meta.channelmap(info.phy.start_key)
    
            for det in chmap:
                
                if chmap[det].system=="geds" and chmap[det].analysis.usability=="on":

                    if dets is None or chmap[det].name in dets:
                        mass =chmap[det].production.mass_in_g/1000
                        exposure+=mass*info.phy.livetime_in_s/60/60/24/365.25
    
    return exposure

def get_exposure_string(period, string:list|None = None):
    """Get the exposure either for all strings (string = None) or just a subset"""
    exposure = 0
    for run, info in meta.datasets.runinfo[f"p{period}"].items():
    
        if ("phy" in info):
    
            chmap = meta.channelmap(info.phy.start_key)
    
            for det in chmap:
                
                if chmap[det].system=="geds" and chmap[det].analysis.usability=="on":

                    if string is None or chmap[det].location.string in string:
                        mass =chmap[det].production.mass_in_g/1000
                        exposure+=mass*info.phy.livetime_in_s/60/60/24/365.25
    
    return exposure
