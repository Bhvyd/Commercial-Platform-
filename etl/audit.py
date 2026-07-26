"""Audit stage: records what each pipeline stage did, and quarantines rejected rows."""
from datetime import datetime, timezone

import pandas as pd

from database.connection import SessionLocal
from database.models import EtlAuditLog, RejectedRecord


def log_stage(batch_id: str, stage: str, rows_in: int, rows_out: int, rows_rejected: int, started_at: datetime, notes: str = "") -> None:
    with SessionLocal() as session:
        session.add(
            EtlAuditLog(
                batch_id=batch_id,
                stage=stage,
                rows_in=rows_in,
                rows_out=rows_out,
                rows_rejected=rows_rejected,
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
                notes=notes,
            )
        )
        session.commit()


def log_rejected(batch_id: str, stage: str, rejected: pd.DataFrame, id_column: str = "source_row_id") -> None:
    if rejected.empty:
        return
    with SessionLocal() as session:
        records = [
            RejectedRecord(
                batch_id=batch_id,
                stage=stage,
                source_row_id=str(row.get(id_column, "")),
                reason=str(row.get("reason", ""))[:300],
                raw_payload=str(row.to_dict())[:2000],
            )
            for _, row in rejected.iterrows()
        ]
        session.add_all(records)
        session.commit()
