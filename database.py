"""
Supabase database client untuk TPID Dashboard Kab. Pekalongan
"""
import os
import requests
import pandas as pd
from datetime import date, datetime
from typing import Optional


HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def _get(table: str, params: dict = None) -> list:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.get(url, headers=HEADERS, params=params or {})
    r.raise_for_status()
    return r.json()

def _post(table: str, data: dict) -> dict:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json()

def _patch(table: str, match: dict, data: dict) -> dict:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in match.items()}
    r = requests.patch(url, headers=HEADERS, params=params, json=data)
    r.raise_for_status()
    return r.json()

def _delete(table: str, match: dict):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in match.items()}
    r = requests.delete(url, headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()

# ── KOMODITAS ────────────────────────────────────────────────────────────────

def get_komoditas() -> pd.DataFrame:
    data = _get("komoditas", {"select": "*", "order": "nama_komoditas.asc"})
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id_komoditas", "nama_komoditas", "satuan"])

def add_komoditas(nama: str, satuan: str) -> dict:
    return _post("komoditas", {"nama_komoditas": nama, "satuan": satuan})

def update_komoditas(id_komoditas: int, nama: str, satuan: str) -> dict:
    return _patch("komoditas", {"id_komoditas": id_komoditas}, {"nama_komoditas": nama, "satuan": satuan})

def delete_komoditas(id_komoditas: int):
    return _delete("komoditas", {"id_komoditas": id_komoditas})

# ── PASAR ────────────────────────────────────────────────────────────────────

def get_pasar() -> pd.DataFrame:
    data = _get("pasar", {"select": "*", "order": "nama_pasar.asc"})
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id_pasar", "nama_pasar", "kabupaten", "kecamatan"])

def add_pasar(nama: str, kabupaten: str, kecamatan: str) -> dict:
    return _post("pasar", {"nama_pasar": nama, "kabupaten": kabupaten, "kecamatan": kecamatan})

def update_pasar(id_pasar: int, nama: str, kabupaten: str, kecamatan: str) -> dict:
    return _patch("pasar", {"id_pasar": id_pasar}, {"nama_pasar": nama, "kabupaten": kabupaten, "kecamatan": kecamatan})

def delete_pasar(id_pasar: int):
    return _delete("pasar", {"id_pasar": id_pasar})

# ── HARGA HARIAN ──────────────────────────────────────────────────────────────

def get_harga_harian(
    tgl_mulai: Optional[str] = None,
    tgl_selesai: Optional[str] = None,
    id_komoditas: Optional[int] = None,
    id_pasar: Optional[int] = None,
) -> pd.DataFrame:
    params = {
        "select": "tanggal,harga,id_komoditas,id_pasar,komoditas(nama_komoditas,satuan),pasar(nama_pasar,kabupaten,kecamatan)",
        "order": "tanggal.desc",
        "limit": 10000,
    }
    if tgl_mulai:
        params["tanggal"] = f"gte.{tgl_mulai}"
    if tgl_selesai:
        params["tanggal"] = f"lte.{tgl_selesai}"
    if id_komoditas:
        params["id_komoditas"] = f"eq.{id_komoditas}"
    if id_pasar:
        params["id_pasar"] = f"eq.{id_pasar}"
    data = _get("harga_harian", params)
    if not data:
        return pd.DataFrame()
    rows = []
    for r in data:
        rows.append({
            "tanggal": r["tanggal"],
            "harga": r["harga"],
            "id_komoditas": r["id_komoditas"],
            "id_pasar": r["id_pasar"],
            "nama_komoditas": r.get("komoditas", {}).get("nama_komoditas", "") if r.get("komoditas") else "",
            "satuan": r.get("komoditas", {}).get("satuan", "") if r.get("komoditas") else "",
            "nama_pasar": r.get("pasar", {}).get("nama_pasar", "") if r.get("pasar") else "",
            "kabupaten": r.get("pasar", {}).get("kabupaten", "") if r.get("pasar") else "",
            "kecamatan": r.get("pasar", {}).get("kecamatan", "") if r.get("pasar") else "",
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df

def add_harga_harian(tanggal: str, id_komoditas: int, id_pasar: int, harga: int) -> dict:
    return _post("harga_harian", {
        "tanggal": tanggal,
        "id_komoditas": id_komoditas,
        "id_pasar": id_pasar,
        "harga": harga,
    })

def delete_harga_harian(tanggal: str, id_komoditas: int, id_pasar: int):
    url = f"{SUPABASE_URL}/rest/v1/harga_harian"
    params = {
        "tanggal": f"eq.{tanggal}",
        "id_komoditas": f"eq.{id_komoditas}",
        "id_pasar": f"eq.{id_pasar}",
    }
    r = requests.delete(url, headers=HEADERS, params=params)
    r.raise_for_status()

# ── INFLASI ───────────────────────────────────────────────────────────────────

def get_inflasi(
    tahun: Optional[int] = None,
    bulan: Optional[int] = None,
    level_wilayah: Optional[str] = None,
) -> pd.DataFrame:
    params = {"select": "*", "order": "tahun.desc,bulan.desc", "limit": 5000}
    if tahun:
        params["tahun"] = f"eq.{tahun}"
    if bulan:
        params["bulan"] = f"eq.{bulan}"
    if level_wilayah:
        params["level_wilayah"] = f"eq.{level_wilayah}"
    data = _get("inflasi", params)
    return pd.DataFrame(data) if data else pd.DataFrame(
        columns=["id_inflasi", "tahun", "bulan", "level_wilayah", "nama_wilayah",
                 "inflasi_mtm", "inflasi_ytd", "inflasi_yoy", "created_at"])

def add_inflasi(tahun: int, bulan: int, level_wilayah: str, nama_wilayah: str,
                mtm: float, ytd: float, yoy: float) -> dict:
    return _post("inflasi", {
        "tahun": tahun, "bulan": bulan,
        "level_wilayah": level_wilayah, "nama_wilayah": nama_wilayah,
        "inflasi_mtm": mtm, "inflasi_ytd": ytd, "inflasi_yoy": yoy,
    })

def update_inflasi(id_inflasi: int, tahun: int, bulan: int, level_wilayah: str,
                   nama_wilayah: str, mtm: float, ytd: float, yoy: float) -> dict:
    return _patch("inflasi", {"id_inflasi": id_inflasi}, {
        "tahun": tahun, "bulan": bulan,
        "level_wilayah": level_wilayah, "nama_wilayah": nama_wilayah,
        "inflasi_mtm": mtm, "inflasi_ytd": ytd, "inflasi_yoy": yoy,
    })

def delete_inflasi(id_inflasi: int):
    return _delete("inflasi", {"id_inflasi": id_inflasi})
