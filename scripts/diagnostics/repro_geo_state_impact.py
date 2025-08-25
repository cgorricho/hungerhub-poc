#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    import pandas as pd
except Exception as e:
    print(f"ERROR: pandas not available: {e}")
    sys.exit(1)

try:
    from src.utils.paths import get_data_dir
except Exception as e:
    print(f"ERROR: Cannot import get_data_dir from src.utils.paths: {e}")
    sys.exit(1)


def build_state_impact_df():
    data_dir = get_data_dir('processed/real')
    bids = pd.read_parquet(data_dir / 'ACBIDS_ARCHIVE.parquet')
    shares = pd.read_parquet(data_dir / 'ACSHARES.parquet')
    winning_bids = bids[bids['WONLOAD'] == 1.0].copy()
    shares_with_state = shares.dropna(subset=['STATE', 'AFFILIATEWEBID'])
    affiliate_to_state = shares_with_state.set_index('AFFILIATEWEBID')['STATE'].to_dict()
    winning_bids['recipient_state'] = winning_bids['AFFILIATEWEBID'].map(affiliate_to_state)
    state_weight_dist = winning_bids.groupby('recipient_state')['GROSSWEIGHT'].sum().dropna().sort_values(ascending=False)
    state_weight_tons = state_weight_dist / 2204.62262185
    rows = []
    for state, weight_tons in state_weight_tons.items():
        if pd.notna(state) and str(state).strip() != '':
            rows.append({'state': state, 'weight_tons': weight_tons, 'weight_pounds': weight_tons * 2000, 'organization_count': None})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    print("[Diagnostic] Build state_impact_df like enhanced_app Tab 4")
    try:
        df = build_state_impact_df()
        print(f"state_impact_df shape: {df.shape}")
        print(df.head(10).to_string(index=False))
        if df.empty:
            print("WARNING: Empty state_impact_df (check input parquet files)")
    except FileNotFoundError as e:
        print(f"MISSING: {e}")
    except Exception as e:
        print(f"ERROR: {e}")

