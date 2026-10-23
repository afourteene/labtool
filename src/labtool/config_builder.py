def build_tunnel_config(lab, tunnel, credentials_path):
    ingress = [
        {"hostname": lab.hostname(n), "service": n.service}
        for n in lab.nodes
    ]
    ingress.append({"service": "http_status:404"})  # The final mandatory rule
    return {
        "tunnel": tunnel.id,
        "credentials-file": credentials_path,
        "ingress": ingress,
    }