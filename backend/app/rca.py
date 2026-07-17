# 

def validate_rca(incident):
    return incident.rca is not None and len(incident.rca.strip()) > 0