import pandas as pd

profiles_df = pd.read_csv("apd_personal_profiles.csv")


def parse_set(s):
    if pd.isna(s) or s == "":
        return set()
    return set(str(v) for v in str(s).split("|"))


def compute_behavior_risk(tx):
   
    cid = tx["customer_id"]

    if cid not in profiles_df.index:
        return 0, ["no_profile"]

    p = profiles_df.loc[cid]
    reasons = []
    total_risk = 0

    amount = tx["amount"]
    hour   = tx["hour_of_day"]
    city   = str(tx["city"])
    country = str(tx["country"])
    device = str(tx["device_type"])
    ip     = str(tx["ip_address"])
    category = str(tx["category"])
    channel  = str(tx["channel"])

    # 1) Amount anomaly
    avg = p["avg_amount"]
    std = p["std_amount"]
    if pd.isna(std) or std == 0:
        z_abs = 0
    else:
        z_abs = abs((amount - avg) / std)

    if 2 <= z_abs < 4:
        total_risk += 10
        reasons.append("amount_slight_anomaly")
    elif 4 <= z_abs < 7:
        total_risk += 25
        reasons.append("amount_strong_anomaly")
    elif z_abs >= 7:
        total_risk += 40
        reasons.append("amount_extreme_anomaly")

    # 2) Hour anomaly
    typical_hours = parse_set(p["typical_hours"])
    if typical_hours and (str(hour) not in typical_hours):
        total_risk += 10
        reasons.append("unusual_hour")

    # 3) City / country anomaly
    home_cities = parse_set(p["home_cities"])
    home_countries = parse_set(p["home_countries"])

    if home_cities and (city not in home_cities):
        total_risk += 10
        reasons.append("new_city")

    if home_countries and (country not in home_countries):
        total_risk += 10
        reasons.append("new_country")

    # 4) Device anomaly
    main_devices = parse_set(p["main_devices"])
    if main_devices and (device not in main_devices):
        total_risk += 20
        reasons.append("new_device")

    # 5) IP anomaly
    top_ips = parse_set(p.get("top_ips", ""))
    if top_ips and (ip not in top_ips):
        total_risk += 10
        reasons.append("new_ip")

    # 6) Recipient anomaly
    top_rec = parse_set(p.get("top_counterparties", ""))
    # if top_rec and (cp_id not in top_rec):
    #     total_risk += 15
    #     reasons.append("new_recipient")

    # 7) Category / channel anomaly
    top_cat = parse_set(p["top_categories"])
    if top_cat and (category not in top_cat):
        total_risk += 5
        reasons.append("unusual_category")

    top_ch = parse_set(p["top_channels"])
    if top_ch and (channel not in top_ch):
        total_risk += 5
        reasons.append("unusual_channel")

    total_risk = int(min(100, total_risk))
    return total_risk, reasons
