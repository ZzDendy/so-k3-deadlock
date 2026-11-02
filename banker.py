"""Algoritma Banker untuk kasus sumber daya kebun pintar.

Membaca matriks dari matriks.json, menghitung Need, mencari safe sequence,
lalu menguji permintaan sumber daya. Semua angka yang dipakai laporan berasal
dari keluaran skrip ini.

Jalankan: python3 banker.py            (cetak ringkas + tulis results/banker.json)
          python3 banker.py --periksa  (tambah pemeriksaan konsistensi total)
"""
import argparse
import json
import os

MATRIKS = "matriks.json"
KELUAR = "results/banker.json"


def baca_matriks(path=MATRIKS):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def need(d):
    return [[m - a for a, m in zip(alloc, mx)]
            for alloc, mx in zip(d["allocation"], d["max"])]


def total_alokasi(d):
    n = len(d["sumber_daya"])
    return [sum(row[j] for row in d["allocation"]) for j in range(n)]


def aman(available, alloc, need_mat, nama):
    """Kembalikan (safe?, urutan, jejak). jejak = list dict per iterasi."""
    n = len(nama)
    work = list(available)
    finish = [False] * n
    urutan = []
    jejak = []

    while len(urutan) < n:
        dipilih = None
        for i in range(n):
            if not finish[i] and all(kebutuhan <= sisa for kebutuhan, sisa
                                     in zip(need_mat[i], work)):
                dipilih = i
                break
        if dipilih is None:
            break
        sebelum = list(work)
        work = [s + a for s, a in zip(work, alloc[dipilih])]
        finish[dipilih] = True
        urutan.append(nama[dipilih])
        jejak.append({
            "proses": nama[dipilih],
            "need": need_mat[dipilih],
            "work_sebelum": sebelum,
            "work_sesudah": list(work),
        })

    return len(urutan) == n, urutan, jejak


def uji_permintaan(d, available, alloc, need_mat, nama, proses, request):
    """Terapkan algoritma resource-request. Kembalikan dict hasil uji."""
    i = nama.index(proses)
    lewat_need = all(r <= n for r, n in zip(request, need_mat[i]))
    lewat_avail = all(r <= a for r, a in zip(request, available))

    hasil = {
        "proses": proses,
        "request": list(request),
        "request_le_need": lewat_need,
        "request_le_available": lewat_avail,
    }

    if not (lewat_need and lewat_avail):
        hasil.update({"dikabulkan": False, "alasan": "gagal pemeriksaan awal"})
        return hasil, available, alloc, need_mat

    avail_baru = [a - r for a, r in zip(available, request)]
    alloc_baru = [list(row) for row in alloc]
    alloc_baru[i] = [a + r for a, r in zip(alloc_baru[i], request)]
    need_baru = [list(row) for row in need_mat]
    need_baru[i] = [n - r for n, r in zip(need_baru[i], request)]

    safe, urutan, jejak = aman(avail_baru, alloc_baru, need_baru, nama)
    hasil.update({
        "available_sesudah": avail_baru,
        "allocation_baru": alloc_baru[i],
        "need_baru": need_baru[i],
        "safe": safe,
        "urutan": urutan,
        "dikabulkan": safe,
        "alasan": "safe state" if safe else "menyebabkan unsafe state",
    })

    if safe:
        return hasil, avail_baru, alloc_baru, need_baru
    return hasil, available, alloc, need_mat


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--matriks", default=MATRIKS)
    p.add_argument("--periksa", action="store_true")
    a = p.parse_args()

    d = baca_matriks(a.matriks)
    nama = d["proses"]
    alloc = d["allocation"]
    need_mat = need(d)
    available = d["available"]
    total = d["total"]

    print(f"Sumber daya: {', '.join(f'{k}={v}' for k, v in d['sumber_daya'].items())}")
    print(f"Total instans: {tuple(total)}")
    print(f"Available awal: {tuple(available)}")
    print()

    print("| Proses | Tugas | Allocation | Max | Need |")
    print("|---|---|---|---|---|")
    for i, n in enumerate(nama):
        print(f"| {n} | {d['tugas'][n]} | {tuple(alloc[i])} | "
              f"{tuple(d['max'][i])} | {tuple(need_mat[i])} |")

    if a.periksa:
        ta = total_alokasi(d)
        jumlah = [x + y for x, y in zip(ta, available)]
        print()
        print(f"Σ Allocation = {tuple(ta)}")
        print(f"Σ Allocation + Available = {tuple(jumlah)}")
        print(f"Total instans            = {tuple(total)}")
        cocok = jumlah == total
        print("konsisten" if cocok else "TIDAK KONSISTEN")

    safe, urutan, jejak = aman(available, alloc, need_mat, nama)
    print()
    print(f"Safe state: {'YA' if safe else 'TIDAK'}")
    print(f"Safe sequence: <{', '.join(urutan)}>")
    print()
    print("| Iterasi | Proses | Need | Work sebelum | Work sesudah |")
    print("|---|---|---|---|---|")
    for i, j in enumerate(jejak, start=1):
        print(f"| {i} | {j['proses']} | {tuple(j['need'])} | "
              f"{tuple(j['work_sebelum'])} | {tuple(j['work_sesudah'])} |")

    hasil_uji = []
    avail_jalan = list(available)
    alloc_jalan = [list(r) for r in alloc]
    need_jalan = [list(r) for r in need_mat]

    for uji in d.get("permintaan_uji", []):
        hasil, avail_jalan, alloc_jalan, need_jalan = uji_permintaan(
            d, avail_jalan, alloc_jalan, need_jalan, nama,
            uji["proses"], uji["request"])
        hasil["label"] = uji["label"]
        hasil["catatan"] = uji.get("catatan", "")
        hasil_uji.append(hasil)

        print()
        print(f"--- {uji['label']}: {uji['proses']} meminta {tuple(uji['request'])} ---")
        print(f"  Request <= Need      : {hasil['request_le_need']}")
        print(f"  Request <= Available : {hasil['request_le_available']}")
        if "available_sesudah" in hasil:
            print(f"  Available percobaan  : {tuple(hasil['available_sesudah'])}")
            print(f"  Allocation baru      : {tuple(hasil['allocation_baru'])}")
            print(f"  Need baru            : {tuple(hasil['need_baru'])}")
        print(f"  Hasil                : "
              f"{'DIKABULKAN' if hasil['dikabulkan'] else 'DITOLAK'} "
              f"({hasil['alasan']})")

    os.makedirs("results", exist_ok=True)
    with open(KELUAR, "w", encoding="utf-8") as f:
        json.dump({
            "keterangan": d.get("keterangan", ""),
            "sumber": d.get("sumber", ""),
            "proses": nama,
            "tugas": d["tugas"],
            "sumber_daya": d["sumber_daya"],
            "total": total,
            "available_awal": available,
            "allocation": alloc,
            "max": d["max"],
            "need": need_mat,
            "total_alokasi": total_alokasi(d),
            "safe": safe,
            "safe_sequence": urutan,
            "jejak": jejak,
            "uji_permintaan": hasil_uji,
        }, f, indent=2)
    print(f"\ntersimpan: {KELUAR}")


if __name__ == "__main__":
    main()
