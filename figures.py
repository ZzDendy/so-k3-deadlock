"""Menggambar resource-allocation graph dari matriks yang sama dengan banker.py.

Tata letak sengaja dua kolom (proses di kiri, sumber daya di kanan) supaya
garis tidak bersilangan jauh. Garis penuh = assignment (dialokasikan), garis
putus-putus = request (masih dibutuhkan sesuai Need).
"""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

FONT = "DejaVu Sans"
OUT = "results"
BIRU, ORANYE, MERAH = "#3B5B8C", "#B7791F", "#A03B2C"


def kotak_sumber(ax, x, y, leb, ting, label, jumlah):
    ax.add_patch(Rectangle((x - leb / 2, y - ting / 2), leb, ting,
                           facecolor="#FDF2E0", edgecolor=ORANYE, linewidth=1.4,
                           zorder=2))
    ax.text(x, y + ting / 2 - 0.28, f"{label} · {jumlah} instans", ha="center",
            va="center", fontsize=8, fontfamily=FONT, fontweight="bold",
            color=ORANYE, zorder=3)
    for i in range(min(jumlah, 10)):
        dx = -0.36 + (i % 5) * 0.18
        dy = -0.12 - (i // 5) * 0.18
        ax.add_patch(Circle((x + dx, y + dy), 0.032, facecolor=ORANYE,
                            edgecolor="none", zorder=3))


def lingkaran(ax, x, y, label):
    ax.add_patch(Circle((x, y), 0.34, facecolor="#E8EEF7", edgecolor=BIRU,
                        linewidth=1.4, zorder=2))
    ax.text(x, y, label, ha="center", va="center", fontsize=8.6,
            fontfamily=FONT, fontweight="bold", color=BIRU, zorder=3)


def gambar(d, path):
    nama_proses = d["proses"]
    need = d["need"]
    alloc = d["allocation"]
    kunci_sd = list(d["sumber_daya"])

    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    ax.set_xlim(0, 8.8)
    ax.set_ylim(-0.15, 5.2)
    ax.axis("off")

    # proses di kolom kiri, sumber daya di kolom kanan
    x_proses, x_sumber = 1.45, 6.55
    y_proses = [4.55 - i * 0.88 for i in range(len(nama_proses))]
    y_sumber = [4.05 - i * 1.35 for i in range(len(kunci_sd))]

    pos_p = {}
    for n, y in zip(nama_proses, y_proses):
        lingkaran(ax, x_proses, y, n)
        ax.text(x_proses - 0.52, y, d["tugas"][n], ha="right", va="center",
                fontsize=7.2, fontfamily=FONT, color="#444444")
        pos_p[n] = (x_proses, y)

    pos_s = {}
    for k, y in zip(kunci_sd, y_sumber):
        kotak_sumber(ax, x_sumber, y, 1.9, 0.78, d["sumber_daya"][k],
                     d["total"][kunci_sd.index(k)])
        pos_s[k] = (x_sumber, y)

    def titik_sambung(kunci, indeks, total_proses):
        """Titik masuk di tepi kiri kotak sumber daya, disebar vertikal."""
        sx, sy = pos_s[kunci]
        n = max(1, total_proses - 1)
        return (sx - 0.95, sy + 0.22 - (indeks / n) * 0.44)

    def panah(p1, p2, warna, putus):
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=11,
                                     color=warna, linewidth=1.15,
                                     linestyle="--" if putus else "-",
                                     shrinkA=0, shrinkB=0, zorder=1,
                                     alpha=0.85 if putus else 1.0))

    # Assignment: sumber daya -> proses
    for i, n in enumerate(nama_proses):
        for j, k in enumerate(kunci_sd):
            if alloc[i][j] > 0:
                px, py = pos_p[n]
                panah(titik_sambung(k, i, len(nama_proses)),
                      (px + 0.34, py), BIRU, putus=False)

    # Request: proses -> sumber daya
    for i, n in enumerate(nama_proses):
        for j, k in enumerate(kunci_sd):
            if need[i][j] > 0:
                px, py = pos_p[n]
                panah((px + 0.34, py),
                      titik_sambung(k, i, len(nama_proses)), MERAH, putus=True)

    ax.legend(handles=[
        Line2D([0], [0], color=BIRU, linewidth=1.4,
               label="assignment edge (sedang dialokasikan)"),
        Line2D([0], [0], color=MERAH, linewidth=1.4, linestyle="--",
               label="request edge (masih dibutuhkan, dari Need)"),
    ], loc="lower center", bbox_to_anchor=(0.5, -0.03), frameon=False,
        fontsize=7.6, ncol=2)

    sumber = d.get("sumber", "contoh-buku")
    ax.text(0.15, 0.02, f"Sumber angka: matriks {sumber}. Titik pada kotak "
                        "sumber daya menyatakan jumlah instans; garis digambar "
                        "hanya bila nilainya bukan nol.",
            fontsize=7, fontfamily=FONT, color="#555555", style="italic")

    ax.set_title("Resource-allocation graph kasus kebun pintar",
                 fontsize=11, fontfamily=FONT, fontweight="bold", pad=6)

    fig.tight_layout()
    fig.savefig(path, dpi=220, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def jejak_aman(d, path):
    jejak = d["jejak"]
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    label = ["Available\nawal"] + [j["proses"] for j in jejak]
    nilai = [d["available_awal"]] + [j["work_sesudah"] for j in jejak]
    warna = [BIRU, ORANYE, "#2F6B3C"]
    for k, nama in enumerate(d["sumber_daya"]):
        ax.plot(range(len(nilai)), [v[k] for v in nilai], marker="o",
                markersize=4.5, linewidth=1.6, color=warna[k], label=nama)
        ax.annotate(str(nilai[-1][k]), (len(nilai) - 1, nilai[-1][k]),
                    textcoords="offset points", xytext=(7, 0), fontsize=7.5,
                    fontfamily=FONT, color=warna[k], va="center")
    ax.set_xticks(range(len(label)))
    ax.set_xticklabels(label, fontfamily=FONT, fontsize=7.8)
    ax.set_ylabel("Work (instans tersedia)", fontfamily=FONT, fontsize=8.5)
    ax.set_xlabel("Proses yang diselesaikan", fontfamily=FONT, fontsize=8.5)
    ax.tick_params(labelsize=7.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(color="#DDDDDD", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper left")
    ax.set_ylim(0, max(max(v) for v in nilai) * 1.28)
    ax.set_xlim(-0.3, len(nilai) - 0.4)
    ax.set_title("Kenaikan Work sepanjang safe sequence",
                 fontsize=9.8, fontfamily=FONT, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    with open("results/banker.json", encoding="utf-8") as f:
        d = json.load(f)
    gambar(d, f"{OUT}/gambar-rag.png")
    jejak_aman(d, f"{OUT}/gambar-work.png")
    print("gambar:", [f for f in sorted(os.listdir(OUT)) if f.endswith(".png")])


if __name__ == "__main__":
    main()
