import pandas as pd
import pytest
from src.data_validation import load_transactions, REQUIRED_COLUMNS

def frame(): return pd.DataFrame({c:[0,1] for c in REQUIRED_COLUMNS})
def test_valid_binary_target(tmp_path):
 p=tmp_path/"valid.csv"; frame().to_csv(p,index=False); assert load_transactions(p)["Class"].tolist()==[0,1]
def test_invalid_target(tmp_path):
 d=frame(); d["Class"]=[0,2]; p=tmp_path/"bad.csv"; d.to_csv(p,index=False)
 with pytest.raises(ValueError,match="binary"): load_transactions(p)
def test_missing_column(tmp_path):
 p=tmp_path/"bad.csv"; frame().drop(columns="V1").to_csv(p,index=False)
 with pytest.raises(ValueError,match="missing required columns"): load_transactions(p)
def test_missing_file_message(tmp_path):
 with pytest.raises(FileNotFoundError,match="creditcard.csv"): load_transactions(tmp_path/"absent.csv")


def test_duplicate_split_audit_reports_overlap_and_conflict():
    from src.data_validation import duplicate_split_audit
    data = frame().iloc[[0, 0, 1, 1]].copy().reset_index(drop=True)
    data["Class"] = [0, 0, 1, 1]
    audit = duplicate_split_audit(data, [0, 2], [1, 3])
    assert audit["duplicate_extra_rows"] == 2
    assert audit["duplicate_groups"] == 2
    assert audit["cross_split_feature_groups"] == 2
    assert audit["cross_split_rows"] == 4
    assert audit["conflicting_target_groups"] == 0

    data.loc[1, "Class"] = 1
    audit = duplicate_split_audit(data, [0, 2], [1, 3])
    assert audit["conflicting_target_groups"] == 1
