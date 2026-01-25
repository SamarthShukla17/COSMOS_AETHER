import lightkurve as lk

def fetch_star_data(target_name="TIC 27491137"): # Example target
    print(f"AETHER: Intercepting data for {target_name}...")
    search_result = lk.search_lightcurve(target_name, author="SPOC")
    if not search_result:
        return None
    lc = search_result.download()
    # Flatten and remove outliers (known noise) to leave only "True Unknowns"
    return lc.flatten().remove_nans()

if __name__ == "__main__":
    data = fetch_star_data()
    data.plot()
    