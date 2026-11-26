from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "simulation" / "raw"
PROCESSED = ROOT / "data" / "simulation" / "processed"
SEED = 2027

# Prototype ticker universe: verify symbols and industry classifications
# against an official HOSE listing snapshot before empirical research.
GROUPS = {
"Banking": "ACB BID CTG EIB HDB LPB MBB MSB OCB SHB SSB STB TCB TPB VCB VIB VPB NAB ABB VAB".split(),
"Real Estate": "BCM CII DIG DXG D2D HDC HDG IJC KBC KDH NLG NVL PDR QCG SCR SJS TCH VHM VRE SZC".split(),
"Securities & Finance": "AGR APG BSI CTS FTS HCM MBS ORS SSI TVS VCI VDS VIX VND BIC BVH BMI MIG VNR VFS".split(),
"Industry & Construction": "BMP CAV CTD DGC DHA ECN GEX GMD HBC HPG HT1 KSB NKG PC1 PHR REE SMC TLG VGC HHV".split(),
"Food & Beverage": "ANV ASM DBC FMC HAG HNG KDC LSS MSN PAN SAB SBT VHC VNM BAF IDI NAF QNS TAR ACL".split(),
"Retail & Consumer": "DGW FRT MWG PET PNJ VPL VTP AST CMV COM HAX HTV SVC TNA TMT VTO VOS VSC VIP HHS".split(),
"Energy & Utilities": "BSR CNG GAS GSP OIL PVD PVT PLX PXS PGC PCT TCO TLP POW NT2 PPC TV2 CHP VSH PGD".split(),
"Technology & Telecom": "CMG ELC FPT ICT ITD SAM SGT ST8 VGI YEG FOX CTR VNZ DAG TTN VTC ONE SRA VEC VLA".split(),
}
VOL = {"Banking":.24,"Real Estate":.38,"Securities & Finance":.42,"Industry & Construction":.31,
       "Food & Beverage":.23,"Retail & Consumer":.30,"Energy & Utilities":.34,"Technology & Telecom":.33}
BETA = {"Banking":1.0,"Real Estate":1.3,"Securities & Finance":1.4,"Industry & Construction":1.05,
        "Food & Beverage":.8,"Retail & Consumer":1.0,"Energy & Utilities":1.1,"Technology & Telecom":1.15}

def make_universe():
    pairs, seen = [], set()
    for industry, symbols in GROUPS.items():
        if len(symbols) != 20:
            raise ValueError(f"{industry}: expected 20 symbols, got {len(symbols)}")
        for symbol in symbols:
            if symbol in seen:
                raise ValueError(f"Duplicate ticker: {symbol}")
            seen.add(symbol)
            pairs.append((symbol, industry))
    if len(pairs) != 160:
        raise ValueError(f"Expected 160 unique tickers, got {len(pairs)}")
    return pairs

def main():
    rng = np.random.default_rng(SEED)
    pairs = make_universe()
    dates = pd.bdate_range("2020-01-01", "2025-12-31")
    year = dates.year.to_numpy()
    mu = np.select([year==2020,year==2021,year==2022,year==2023,year>=2024],
                   [-.0001,.0005,-.0003,.00045,.00035], default=.0002)
    sigma = np.select([year==2020,year==2021,year==2022,year==2023,year>=2024],
                      [.023,.014,.018,.014,.012], default=.015)
    market_return = rng.normal(mu, sigma)
    regime = np.select([year==2020,year==2021,year==2022,year==2023],
                       ["COVID_SHOCK","RECOVERY","DOWNTURN","RECOVERY"], default="GROWTH")
    market = pd.DataFrame({"date":dates,"market_return":market_return,"market_regime":regime})
    frames = []
    for n,(ticker,industry) in enumerate(pairs,1):
        vol, beta = VOL[industry], BETA[industry]
        ret = np.clip(rng.normal(.055,.065)/252 + beta*market_return +
                      rng.normal(0,vol/np.sqrt(252)*.72,len(dates)), -.12,.12)
        previous = np.empty(len(dates)); close = np.empty(len(dates))
        previous[0] = rng.uniform(12000,95000)
        for i in range(len(dates)):
            if i: previous[i] = close[i-1]
            close[i] = previous[i]*np.exp(ret[i])
        op = previous*np.exp(rng.normal(0,vol/np.sqrt(252)*.22,len(dates)))
        intraday = np.abs(rng.normal(.006,.003,len(dates)))
        high = np.maximum(op,close)*(1+intraday)
        low = np.minimum(op,close)*(1-intraday*rng.uniform(.6,1,len(dates)))
        adj = close*np.exp(rng.normal(0,.00002,len(dates)))
        volume = np.maximum(1000,rng.lognormal(14,.85)*(
            1+np.minimum(np.abs(ret)*15,2.5))*rng.lognormal(0,.32,len(dates))).astype("int64")
        f = pd.DataFrame({"date":dates,"ticker":ticker,"industry":industry,
            "open":op.round(2),"high":high.round(2),"low":low.round(2),
            "close":close.round(2),"adjusted_close":adj.round(2),"volume":volume,
            "turnover":(close*volume).round(2),"market_return":market_return,"market_regime":regime})
        f["next_day_return"] = np.log(f.adjusted_close.shift(-1)/f.adjusted_close)
        f["next_day_price"] = f.adjusted_close.shift(-1)
        f["data_type"] = "SYNTHETIC"
        f["data_source"] = "SIMULATED_NOT_MARKET_DATA"
        frames.append(f)
        if n % 20 == 0: print(f"Generated {n}/160 tickers")
    df = pd.concat(frames,ignore_index=True).sort_values(["ticker","date"]).reset_index(drop=True)
    assert df.ticker.nunique()==160
    assert (df.low<=df.open).all() and (df.low<=df.close).all()
    assert (df.high>=df.open).all() and (df.high>=df.close).all()
    assert (df.volume>=0).all() and (df.close>0).all()
    RAW.mkdir(parents=True,exist_ok=True); PROCESSED.mkdir(parents=True,exist_ok=True)
    df.to_csv(RAW/"hose_160_stocks_synthetic_2020_2025.csv",index=False,encoding="utf-8-sig")
    ready=df.dropna(subset=["next_day_return","next_day_price"])
    ready.to_csv(PROCESSED/"hose_model_ready.csv",index=False,encoding="utf-8-sig")
    with pd.ExcelWriter(RAW/"HOSE_160_STOCKS_SIMULATION.xlsx",engine="openpyxl") as writer:
        df.to_excel(writer,index=False,sheet_name="Daily_Data")
        pd.DataFrame(pairs,columns=["ticker","industry"]).to_excel(writer,index=False,sheet_name="Ticker_Universe")
        market.to_excel(writer,index=False,sheet_name="Market_Data")
    print(f"Done: {len(df):,} rows, {df.ticker.nunique()} tickers.")
    print("All prices and volumes are SYNTHETIC, not actual HOSE market observations.")

if __name__ == "__main__":
    main()
