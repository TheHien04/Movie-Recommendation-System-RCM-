"""Single source of truth for movie dataset loading and preprocessing."""
import logging
import os

import pandas as pd

from app.data.validation import validate_movie_dataframe

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../../data/movie.csv")

_df = None
_validation_report = None


def get_validation_report():
  get_dataframe()
  return _validation_report


def get_dataframe() -> pd.DataFrame:
    global _df, _validation_report
    if _df is None:
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Không tìm thấy file: {DATA_PATH}")
        _df = pd.read_csv(
            DATA_PATH,
            dtype={"imdbRating": float, "rottenRating": float, "tmdbRating": float},
        )
        _validation_report = validate_movie_dataframe(_df)
        if not _validation_report.valid:
            raise ValueError(f"Movie dataset invalid: {_validation_report.errors}")
        for warning in _validation_report.warnings:
            logger.warning("Dataset validation: %s", warning)
        _df["title_lower"] = _df["Title"].str.lower()
        _df["Genre"] = _df["Genre"].fillna("").str.lower()
        _df["Actors"] = (
            _df["Actors"].fillna("").str.lower().str.replace(", ", ",", regex=False)
        )
        _df["Director"] = _df["Director"].fillna("").str.lower()
        _df["Overview"] = _df["Overview"].fillna("")
        _df["content_text"] = (
            _df["Title"]
            + " "
            + _df["Genre"]
            + " "
            + _df["Actors"]
            + " "
            + _df["Director"]
            + " "
            + _df["Overview"]
        ).str.lower()
    return _df
