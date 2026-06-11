"""Dataset schema validation — Great Expectations–style checks without extra deps."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import pandas as pd

REQUIRED_COLUMNS = [
  "Poster_Link", "Title", "Certificate", "Overview", "Runtime (min)",
  "Genre", "Actors", "Director", "Year", "imdbRating",
]


@dataclass
class ValidationReport:
  valid: bool
  row_count: int
  data_hash: str
  errors: list[str] = field(default_factory=list)
  warnings: list[str] = field(default_factory=list)


def _hash_dataframe(df: pd.DataFrame) -> str:
  payload = df[["Title", "Genre", "imdbRating"]].to_csv(index=False).encode()
  return hashlib.sha256(payload).hexdigest()[:16]


def validate_movie_dataframe(df: pd.DataFrame) -> ValidationReport:
  errors: list[str] = []
  warnings: list[str] = []

  missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
  if missing:
    errors.append(f"Missing columns: {missing}")

  if df.empty:
    errors.append("Dataset is empty")

  if "Title" in df.columns:
    dupes = int(df["Title"].duplicated().sum())
    if dupes:
      warnings.append(f"{dupes} duplicate titles detected")

  if "imdbRating" in df.columns:
    invalid = df[(df["imdbRating"].notna()) & ((df["imdbRating"] < 0) | (df["imdbRating"] > 10))]
    if not invalid.empty:
      warnings.append(f"{len(invalid)} rows with imdbRating outside [0, 10]")

  return ValidationReport(
    valid=len(errors) == 0,
    row_count=len(df),
    data_hash=_hash_dataframe(df) if not df.empty and "Title" in df.columns else "",
    errors=errors,
    warnings=warnings,
  )
