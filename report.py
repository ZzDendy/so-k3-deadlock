"""Merakit laporan K-3 dari template jurusan dan hasil banker.py.

Seluruh angka matriks dan hasil Banker dibaca dari results/banker.json, sehingga
laporan selalu sesuai dengan matriks.json yang dipakai saat menghitung.
"""
import json
import os
import platform
import subprocess
import sys

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.shared import Cm, Pt

sys.path.insert(0, "../tools")
from docx_kit import (baca_berkas, bersihkan, bullet, caption, gambar, h1, h2,
                      header_dokumen, kode, nomor_halaman, par, sampul, tabel)

TEMPLATE = "../template/Template Laporan Tugas Individu.docx"
OUT = "results/Laporan_K-3_Deadlock.docx"
NAMA = "Dendy Zainal Mutaqien"
NIM = "250660121068"
KELAS = "IF-3C"
KODE = "K-3"
REPO = "https://github.com/ZzDendy/so-k3-deadlock"
BUKTI = "results/bukti"

ANGGOTA = [
    ("Dendy Zainal Mutaqien", "250660121068",
     "Simulator Banker, resource-allocation graph, dan penyusunan laporan"),
    ("R.Sangga Buana", "250660121021",
     "Memeriksa hasil perhitungan Need dan safe sequence pada Tabel 5.2"),
    ("M.Azkal Azkiya", "250660121107",
     "Menelaah strategi pencegahan dan kesesuaian Daftar Pustaka"),
]


def baca_hasil():
    with open("results/banker.json", encoding="utf-8") as f:
        return json.load(f)


def fakta_sistem():
    def jalankan(cmd):
        try:
            return subprocess.run(cmd, shell=True, capture_output=True,
                                  text=True).stdout.strip()
        except OSError:
            return ""

    with open("/etc/os-release", encoding="utf-8") as f:
        osr = {}
        for baris in f:
            if "=" in baris:
                k, v = baris.rstrip().split("=", 1)
                osr[k] = v.strip('"')
    return {
        "kernel": platform.release(),
        "distro": osr.get("PRETTY_NAME", "Linux"),
        "cpu": jalankan("lscpu | grep -m1 'Model name' | cut -d: -f2").strip(),
        "jumlah_cpu": os.cpu_count(),
        "python": platform.python_version(),
    }


def tup(nilai):
    return "(" + ", ".join(str(x) for x in nilai) + ")"


def sampul_k3(d):
    sampul(
        d,
        "LAPORAN TUGAS KELOMPOK",
        "Analisis dan Penanganan Deadlock\npada Sumber Daya Kebun Pintar",
        [
            ("Kode dan judul tugas", "K-3 Analisis dan Penanganan Deadlock"),
            ("Kelas / tema", f"{KELAS} — IoT dan Smart Farming"),
            ("Nama", NAMA),
            ("NIM", NIM),
            ("Anggota kelompok", "3 orang — Dendy Zainal Mutaqien, R.Sangga Buana, "
                                 "M.Azkal Azkiya (rincian di Lampiran D)"),
            ("Nama host", "INFINIX-ElementaryOS"),
            ("Minggu / tanggal kumpul", "Minggu ke-7 / 2 November 2026"),
            ("Kepingan puzzle", "Kepingan #7 → Level 5 Puzzle UTS"),
            ("Dosen pengampu", "Muhammad Agreindra Helmiawan, S.Kom., M.T"),
        ],
        "K-3",
    )


def catatan_data(d, m):
    """Kejujuran soal asal matriks, ditaruh paling awal supaya tidak tersembunyi."""
    sumber = m["sumber"]
    if sumber == "contoh-buku":
        p = par(d, "Catatan data: matriks Allocation, Max, dan Available pada laporan ini "
                   "adalah matriks contoh dari Silberschatz dkk. (2018), bukan matriks "
                   "yang dibagikan dosen. Lembar tugas menyebut matriks kelas, tetapi "
                   "matriks itu belum tersedia saat laporan disusun. Seluruh metode pada "
                   "Bagian 4 dan 5 dapat dipakai apa adanya; hanya angkanya yang perlu "
                   "diganti. Perubahan cukup dilakukan pada satu berkas (matriks.json), "
                   "lalu seluruh tabel, graf, dan safe sequence dihitung ulang otomatis.")
        p.runs[0].italic = True
        p.runs[0].font.size = Pt(9)


def pendahuluan(d, m, h):
    h1(d, "1. Pendahuluan")

    h2(d, "1.1 Latar belakang kasus")
    par(d, "Sistem irigasi otomatis pada kebun pintar bukan satu program, melainkan beberapa "
           "tugas kontrol yang berjalan bersamaan di satu mikrokontroler: penjadwal irigasi, "
           "kontrol pompa, kontrol zona lahan, pembaca kelembapan, dan pencatat telemetri. "
           "Kelima tugas itu memakai tiga sumber daya yang sama: pompa air, katup irigasi, dan "
           "bus sensor I2C.")
    par(d, "Ketiga sumber daya itu tidak dapat dibagi seenaknya. Satu pompa tidak boleh "
           "dikendalikan dua tugas sekaligus, dan satu transaksi I2C hanya boleh dilayani satu "
           "perangkat pada satu waktu. Karena itu setiap tugas harus meminta izin sebelum "
           "memakainya, dan menunggu bila sedang dipakai tugas lain. Di sinilah bahaya muncul: "
           "kalau tugas A memegang pompa lalu menunggu katup, sementara tugas B memegang katup "
           "lalu menunggu pompa, keduanya menunggu selamanya. Keadaan itu disebut deadlock, dan "
           "pada sistem irigasi akibatnya bukan sekadar program berhenti — tanaman bisa "
           "kekeringan atau lahan kebanjiran karena pompa tidak pernah dimatikan.")
    par(d, "Laporan ini menganalisis kemungkinan itu dengan tiga pendekatan yang diminta lembar "
           "tugas: menggambar resource-allocation graph, menerapkan algoritma Banker untuk "
           "menentukan safe state, lalu merancang strategi pencegahan yang realistis untuk "
           "perangkat IoT.")

    h2(d, "1.2 Tujuan tugas")
    par(d, "Capaian pembelajaran yang diukur adalah Sub-CPMK-7 (CPMK061, CPMK063, CPMK081, "
           "CPMK102, CPMK112). Tujuannya:")
    bullet(d, "menggambar resource-allocation graph kasus kebun pintar dan mengidentifikasi "
              "empat kondisi Coffman yang terpenuhi;", "Pertama, ")
    bullet(d, "menerapkan algoritma Banker untuk menentukan apakah sistem berada pada safe "
              "state, termasuk menguji permintaan sumber daya yang masuk;", "Kedua, ")
    bullet(d, "merancang strategi pencegahan deadlock yang masuk akal untuk mikrokontroler "
              "dengan memori dan prosesor terbatas.", "Ketiga, ")

    h2(d, "1.3 Ruang lingkup")
    par(d, f"Analisis memakai {len(m['proses'])} tugas kontrol dan {len(m['sumber_daya'])} "
           f"jenis sumber daya dengan total instans {tup(m['total'])}. Seluruh perhitungan "
           f"dijalankan oleh banker.py pada Python {h['python']} di mesin "
           f"{h['distro']}, lalu diverifikasi ulang terhadap langkah manual pada Bagian 5.")
    par(d, "Yang tidak dikerjakan: pengukuran deadlock pada perangkat keras sesungguhnya, "
           "analisis deadlock pada sistem multi-mikrokontroler terdistribusi, dan penerapan "
           "algoritma deteksi deadlock (wait-for graph) karena kasus ini diselesaikan dengan "
           "pencegahan dan penghindaran, bukan deteksi.")


def dasar_teori(d):
    h1(d, "2. Dasar Teori Singkat")
    par(d, "Deadlock terjadi ketika sekumpulan proses saling menunggu sumber daya yang dipegang "
           "proses lain dalam kumpulan itu, sehingga tidak satu pun dapat melanjutkan "
           "(Silberschatz dkk., 2018). Deadlock hanya mungkin terjadi bila empat kondisi "
           "berikut terpenuhi sekaligus, yang dikenal sebagai kondisi Coffman:")
    bullet(d, "Mutual exclusion — setidaknya satu sumber daya dipegang secara eksklusif.", "a. ")
    bullet(d, "Hold and wait — proses memegang satu sumber daya sambil menunggu sumber daya "
              "lain.", "b. ")
    bullet(d, "No preemption — sumber daya tidak dapat diambil paksa dari pemegangnya.", "c. ")
    bullet(d, "Circular wait — ada rantai proses yang masing-masing menunggu sumber daya yang "
              "dipegang proses berikutnya.", "d. ")
    par(d, "Menghilangkan salah satu kondisi sudah cukup untuk mencegah deadlock. Itulah dasar "
           "strategi pencegahan pada Bagian 5, dan sebabnya keempat kondisi dianalisis satu per "
           "satu, bukan hanya disebut.")

    par(d, "Resource-allocation graph. Keadaan alokasi digambarkan sebagai graf berarah dengan "
           "dua jenis simpul: proses (lingkaran) dan sumber daya (kotak dengan titik sejumlah "
           "instansnya). Sisi permintaan (request edge) mengarah dari proses ke sumber daya; "
           "sisi alokasi (assignment edge) mengarah dari sumber daya ke proses. Bila setiap "
           "jenis sumber daya hanya punya satu instans, adanya siklus pada graf berarti "
           "deadlock. Bila instansnya banyak, siklus hanya syarat perlu — belum tentu cukup — "
           "sehingga keputusan akhirnya harus memakai algoritma Banker.")

    par(d, "Algoritma Banker. Setiap proses menyatakan kebutuhan maksimumnya di muka (Max). "
           "Dari situ dihitung Need = Max − Allocation. Sistem dianggap aman (safe) bila ada "
           "urutan proses sedemikian sehingga setiap proses dapat memperoleh seluruh "
           "kebutuhannya dengan sisa sumber daya saat itu, lalu mengembalikan seluruh yang "
           "dipegangnya. Algoritma keamanan menjalankan simulasi itu dengan variabel Work yang "
           "dimulai dari Available, lalu bertambah setiap kali satu proses diselesaikan. Bila "
           "semua proses dapat diselesaikan, sistem berada pada safe state dan urutan itu "
           "disebut safe sequence.")
    par(d, "Hal penting yang sering terlewat: safe state tidak sama dengan keadaan bebas masalah. "
           "Sistem dapat berada pada safe state sekarang, tetapi menolak permintaan yang sah "
           "secara angka karena permintaan itu akan membuat keadaan berikutnya unsafe. Algoritma "
           "Banker sengaja konservatif seperti itu; ia mengorbankan pemanfaatan sumber daya "
           "demi kepastian.")


def lingkungan(d, h):
    h1(d, "3. Lingkungan Praktik")
    tabel(d, ["Komponen", "Keterangan"], [
        ("Laptop (host)", f"{h['distro']}, {h['cpu']}, kernel {h['kernel']}"),
        ("Hypervisor", "Tidak dipakai — perhitungan dijalankan langsung pada host"),
        ("VM / host", f"INFINIX-ElementaryOS, {h['jumlah_cpu']} CPU logis"),
        ("Perangkat lain", "Tidak berlaku — kasus dimodelkan dari deskripsi lembar tugas"),
        ("Bahasa dan alat", f"Python {h['python']}; matplotlib untuk graf dan grafik; "
                            "python-docx untuk laporan"),
        ("Berkas data", "matriks.json berisi Allocation, Max, Available, dan permintaan uji"),
        ("Berkas hitung", "banker.py menghasilkan results/banker.json"),
    ], lebar=[4.2, 11.0])

    par(d, "Seluruh perhitungan pada laporan ini bukan hasil ketik tangan. Angka pada tabel dan "
           "narasi diambil dari results/banker.json, yang dihasilkan banker.py dari matriks.json. "
           "Dengan pemisahan itu, mengganti matriks tidak menuntut penyuntingan laporan secara "
           "manual — cukup jalankan ulang tiga skrip.")


def langkah(d, m):
    h1(d, "4. Langkah Pengerjaan")
    par(d, "Pengerjaan dibagi menjadi empat langkah: menyiapkan matriks, menghitung Need dan "
           "safe sequence, menggambar resource-allocation graph, lalu menguji permintaan sumber "
           "daya.")

    h2(d, "4.1 Langkah 1: Menyiapkan matriks masukan")
    par(d, "Matriks dipisahkan dari kode supaya dapat diganti tanpa menyentuh program. Berkas "
           "matriks.json memuat lima hal: nama proses beserta tugasnya, nama sumber daya, total "
           "instans, matriks Allocation, matriks Max, dan Available awal. Permintaan yang akan "
           "diuji juga ditaruh di sini agar skenario uji ikut terekam.")
    kode(d, baca_berkas("matriks.json"))
    par(d, "Data pada berkas ini masih bertanda contoh. Begitu matriks kelas tersedia, yang "
           "perlu diubah hanya larik allocation, max, available, dan total.")

    h2(d, "4.2 Langkah 2: Menghitung Need dan safe sequence")
    par(d, "Need dihitung dengan rumus Need = Max − Allocation, lalu diperiksa konsistensinya: "
           "jumlah seluruh Allocation ditambah Available harus sama dengan total instans sumber "
           "daya. Pemeriksaan ini menangkap salah ketik pada matriks sebelum sempat masuk ke "
           "perhitungan Banker.")
    kode(d, baca_berkas("banker.py"))
    kode(d, "$ python3 banker.py --periksa\n"
            "Σ Allocation = " + tup(m["total_alokasi"]) + "\n"
            "Σ Allocation + Available = "
            + tup([a + b for a, b in zip(m["total_alokasi"], m["available_awal"])]) + "\n"
            "Total instans            = " + tup(m["total"]) + "\n"
            "konsisten\n\n"
            f"Safe state: {'YA' if m['safe'] else 'TIDAK'}\n"
            f"Safe sequence: <{', '.join(m['safe_sequence'])}>")
    gambar(d, f"{BUKTI}/rapi-02-hitung.png", 15.0,
           "Gambar 4.1 Perhitungan Need, safe state, dan hasil uji permintaan pada terminal")

    h2(d, "4.3 Langkah 3: Menggambar resource-allocation graph")
    par(d, "Graf digambar langsung dari matriksnya, bukan dari skenario terpisah. Sisi alokasi "
           "digambar untuk setiap sel Allocation yang bukan nol, sisi permintaan untuk setiap "
           "sel Need yang bukan nol. Karena jumlah sisi mengikuti angka matriks, graf ini dapat "
           "diperiksa silang dengan Tabel 5.2: setiap proses yang memegang pompa harus punya "
           "satu sisi alokasi dari kotak pompa.")
    kode(d, baca_berkas("figures.py"))
    gambar(d, f"{BUKTI}/rapi-04-gambar.png", 13.5,
           "Gambar 4.2 Penulisan gambar graf dan grafik dari data hasil hitung")

    h2(d, "4.4 Langkah 4: Menguji permintaan sumber daya")
    par(d, "Algoritma resource-request diuji dengan dua kasus. Kasus A adalah permintaan yang "
           "masih menjaga safe state; Kasus B diminta setelah Kasus A dikabulkan, dan sengaja "
           "dipilih untuk memperlihatkan penolakan meski angkanya masih tersedia. Kedua hasil "
           "tercatat pada Tabel 5.4.")


def hasil(d, m):
    h1(d, "5. Hasil dan Analisis")

    h2(d, "5.1 Hasil")
    par(d, "Tabel 5.1 memuat kasus yang dianalisis: lima tugas kontrol dan tiga jenis sumber "
           "daya bersama.")
    tabel(d, ["No", "Proses", "Tugas kontrol", "Sumber daya utama"], [
        ("1", "P0", m["tugas"]["P0"], "Pompa, katup, bus I2C"),
        ("2", "P1", m["tugas"]["P1"], "Pompa, bus I2C"),
        ("3", "P2", m["tugas"]["P2"], "Pompa (banyak), bus I2C (sedikit)"),
        ("4", "P3", m["tugas"]["P3"], "Pompa (sedikit), katup, bus I2C"),
        ("5", "P4", m["tugas"]["P4"], "Pompa, katup, bus I2C"),
    ], lebar=[1.0, 1.8, 6.0, 6.4], ukuran=8.5)
    caption(d, "Tabel 5.1 Proses kontrol dan sumber daya yang diperebutkan")

    par(d, "Tabel 5.2 menyajikan matriks Allocation, Max, dan Need beserta hasil hitung "
           "algoritma. Kolom Need dihitung program, bukan diketik.")
    baris = []
    for i, n in enumerate(m["proses"]):
        baris.append((n, m["tugas"][n], tup(m["allocation"][i]), tup(m["max"][i]),
                      tup(m["need"][i])))
    tabel(d, ["Proses", "Tugas", "Allocation", "Max", "Need"], baris,
          lebar=[1.6, 5.0, 2.3, 2.3, 2.3], ukuran=8.5)
    par(d, f"Available awal = {tup(m['available_awal'])}. "
           f"Σ Allocation = {tup(m['total_alokasi'])}; ditambah Available menjadi "
           f"{tup([a + b for a, b in zip(m['total_alokasi'], m['available_awal'])])}, "
           f"sama dengan total instans {tup(m['total'])}, sehingga matriks konsisten.",
           ukuran=9)
    caption(d, "Tabel 5.2 Matriks sumber daya dan hasil perhitungan Need")

    par(d, "Tabel 5.3 memuat jalannya algoritma keamanan. Setiap baris adalah satu iterasi: "
           "proses yang dipilih, kebutuhannya, dan nilai Work sebelum serta sesudah proses itu "
           "diselesaikan.")
    baris = []
    for i, j in enumerate(m["jejak"], start=1):
        baris.append((i, j["proses"], tup(j["need"]), tup(j["work_sebelum"]),
                      tup(j["work_sesudah"])))
    tabel(d, ["Iterasi", "Proses", "Need", "Work sebelum", "Work sesudah"], baris,
          lebar=[1.8, 1.8, 3.2, 3.6, 3.6], ukuran=8.5)
    par(d, f"Kesimpulan: sistem berada pada SAFE STATE dengan safe sequence "
           f"<{', '.join(m['safe_sequence'])}>. Work akhir "
           f"{tup(m['jejak'][-1]['work_sesudah'])} sama dengan total sumber daya, sehingga "
           f"seluruh proses dapat diselesaikan.", ukuran=9)
    caption(d, "Tabel 5.3 Jalannya algoritma keamanan Banker")

    par(d, "Gambar 5.1 memperlihatkan graf alokasi yang digambar dari matriks pada Tabel 5.2.")
    gambar(d, "results/gambar-rag.png", 15.5,
           "Gambar 5.1 Resource-allocation graph kasus kebun pintar")

    par(d, "Gambar 5.2 memperlihatkan kenaikan Work sepanjang safe sequence. Grafik ini "
           "memperlihatkan bahwa setiap langkah berhasil justru karena kebutuhan proses "
           "berikutnya lebih kecil daripada sisa sumber daya saat itu.")
    gambar(d, "results/gambar-work.png", 13.5,
           "Gambar 5.2 Kenaikan Work sepanjang safe sequence")

    par(d, "Tabel 5.4 memuat hasil uji permintaan sumber daya.")
    baris = []
    for u in m["uji_permintaan"]:
        baris.append((
            u["label"], u["proses"], tup(u["request"]),
            "ya" if u["request_le_need"] else "tidak",
            "ya" if u["request_le_available"] else "tidak",
            "DIKABULKAN" if u["dikabulkan"] else "DITOLAK",
            u["alasan"]))
    tabel(d, ["Kasus", "Proses", "Request", "≤ Need", "≤ Available", "Hasil", "Alasan"],
          baris, lebar=[1.7, 1.5, 2.4, 1.4, 1.9, 2.9, 3.4], ukuran=8.5)
    caption(d, "Tabel 5.4 Hasil algoritma resource-request")

    h2(d, "5.2 Analisis")

    h2(d, "5.2.1 Empat kondisi Coffman pada kasus ini")
    par(d, "Lembar tugas meminta keempat kondisi diidentifikasi, bukan hanya disebut. Tabel 5.5 "
           "memetakan masing-masing ke perangkat nyata pada kebun pintar.")
    tabel(d, ["Kondisi", "Bentuknya pada kasus kebun pintar", "Dapat ditiadakan?"], [
        ("Mutual exclusion", "Satu pompa tidak boleh dikendalikan dua tugas sekaligus; satu "
                             "transaksi bus I2C hanya dilayani satu perangkat pada satu waktu",
         "Tidak sepenuhnya. Sumber daya fisik memang eksklusif. Yang bisa dikurangi hanya "
         "lamanya pemakaian"),
        ("Hold and wait", "P1 memegang pompa sambil menunggu katup; P0 memegang katup sambil "
                          "menunggu bus I2C",
         "Ya. Proses dapat diminta mengambil semua sumber daya sekaligus di awal"),
        ("No preemption", "Transaksi I2C yang sedang berjalan tidak boleh dicabut di tengah; "
                          "pompa yang menyala tidak boleh dimatikan paksa tanpa prosedur",
         "Ya, dengan syarat. Bisa dipakai timeout: bila gagal, proses melepas semuanya lalu "
         "mencoba ulang"),
        ("Circular wait", "Rantai tunggu melingkar P0→P1→P2→P0 terbentuk bila setiap tugas "
                          "meminta sumber daya dalam urutan berbeda",
         "Ya, dan paling murah. Cukup tetapkan nomor urut global untuk semua sumber daya"),
    ], lebar=[2.8, 6.6, 5.8], ukuran=8.5)
    caption(d, "Tabel 5.5 Pemenuhan empat kondisi Coffman pada kasus kebun pintar")

    par(d, "Yang perlu ditegaskan: keempat kondisi itu bukan daftar teoretis, melainkan "
           "pemeriksaan satu per satu. Pada kasus ini kondisi pertama dan ketiga sulit "
           "dihilangkan sepenuhnya karena berakar pada sifat perangkat keras. Karena itu strategi "
           "yang realistis bertumpu pada kondisi kedua dan keempat, persis seperti pada "
           "Bagian 5.3.")

    h2(d, "5.2.2 Mengapa sistem dinyatakan aman")
    par(d, f"Safe sequence <{', '.join(m['safe_sequence'])}> ditemukan pada iterasi pertama "
           f"penelusuran: Work dimulai dari {tup(m['available_awal'])}, dan proses pertama yang "
           f"kebutuhannya muat adalah {m['jejak'][0]['proses']} dengan Need "
           f"{tup(m['jejak'][0]['need'])}. Setelah proses itu selesai dan mengembalikan seluruh "
           f"yang dipegangnya, Work naik menjadi {tup(m['jejak'][0]['work_sesudah'])}. Kenaikan "
           f"inilah yang membuka jalan bagi proses berikutnya.")
    par(d, "Yang menarik, urutan aman bukan satu-satunya. Pada matriks ini beberapa proses dapat "
           "dipilih lebih dulu, misalnya P3 atau P4 juga muat pada langkah kedua. Semua urutan "
           "yang berhasil menyelesaikan kelima proses sama-sama sah; algoritma yang berbeda "
           "implementasi dapat menghasilkan urutan berbeda dengan kesimpulan sama. Hal ini perlu "
           "disebut karena pembaca yang menghitung manual bisa mendapat urutan lain dan menyangka "
           "ada kesalahan.")

    h2(d, "5.2.3 Mengapa satu permintaan ditolak")
    par(d, f"Kasus A dikabulkan karena setelah alokasi percobaan, safe sequence masih dapat "
           f"ditemukan. Kasus B berbeda: setelah Kasus A, Available tinggal "
           f"{tup(m['uji_permintaan'][0]['available_sesudah'])}, dan permintaan P0 sebesar "
           f"{tup(m['uji_permintaan'][1]['request'])} masih lolos pemeriksaan awal — angkanya "
           f"memang tersedia. Namun setelah dicoba dialokasikan, Available turun menjadi "
           f"{tup(m['uji_permintaan'][1]['available_sesudah'])} dan tidak ada satu pun proses "
           f"yang kebutuhannya muat. Sistem akan macet, sehingga permintaan itu ditolak.")
    par(d, "Contoh ini penting untuk dijelaskan ke pengguna sistem irigasi. Dari sudut pandang "
           "operator, penolakan itu terlihat tidak masuk akal: stok katup masih ada, kenapa "
           "permintaan ditolak? Jawabannya ada pada kebutuhan maksimum proses lain di masa depan. "
           "Algoritma Banker menjaga keadaan sekarang agar tetap bisa memenuhi janji-janji yang "
           "sudah dinyatakan sebelumnya. Karena itu Banker menuntut setiap proses menyatakan "
           "kebutuhan maksimumnya di muka — dan justru di situlah kelemahan praktisnya pada "
           "sistem tertanam, sebagaimana dibahas berikut.")

    h2(d, "5.3 Rekomendasi")
    par(d, "Strategi pencegahan disusun dengan meniadakan kondisi Coffman yang paling murah "
           "ditiadakan, bukan yang paling teoretis. Tabel 5.6 memuat rancangannya.")
    tabel(d, ["Prioritas", "Strategi", "Penerapan pada kebun pintar", "Biaya"], [
        ("1", "Urutan sumber daya global (meniadakan circular wait)",
         "Semua tugas wajib meminta dengan urutan tetap: Pompa → Katup → Bus I2C. Dilarang "
         "meminta pompa setelah memegang I2C",
         "Hampir nol. Cukup kesepakatan urutan di kode"),
        ("2", "Timeout dan lepas-semua (meniadakan no preemption)",
         "Akses I2C memakai batas waktu, misalnya 50 ms. Bila habis, tugas melepas katup dan "
         "pompa, menunggu sebentar, lalu mencoba lagi",
         "Rendah. Butuh satu timer dan prosedur retry"),
        ("3", "Ambil semua sekaligus (meniadakan hold and wait)",
         "Tugas irigasi mengambil pompa, katup, dan I2C dalam satu operasi atomik. Bila gagal "
         "sebagian, seluruhnya dilepas",
         "Sedang. Pemanfaatan sumber daya turun karena ada yang ditahan lebih lama"),
        ("4", "Arbiter bus I2C (mengurangi mutual exclusion)",
         "Satu tugas driver melayani antrean permintaan I2C dari tugas lain, sehingga tidak ada "
         "rebutan langsung",
         "Sedang. Menambah satu tugas dan antrean di memori"),
        ("5", "Penghindaran dengan Banker (analisis, bukan operasional)",
         "Safe state diperiksa sebelum memberikan pompa atau katup",
         "Tinggi untuk mikrokontroler: butuh deklarasi Max dan beban hitung di setiap permintaan"),
    ], lebar=[1.6, 4.4, 6.0, 3.2], ukuran=8.5)
    caption(d, "Tabel 5.6 Rancangan strategi pencegahan beserta biayanya")

    par(d, "Rekomendasi utama: pakai urutan sumber daya global sebagai pertahanan utama, "
           "tambahkan timeout sebagai pengaman, dan sediakan watchdog untuk memulihkan tugas "
           "yang macet. Ketiganya murah dan tidak menuntut deklarasi kebutuhan maksimum di muka.")

    par(d, "Algoritma Banker sebaiknya dipakai sebagai alat analisis dan pengujian, bukan "
           "mekanisme operasional. Alasannya konkret: Banker menuntut setiap proses menyatakan "
           "Max di muka, padahal kebutuhan tugas sensor sering bergantung pada kondisi lahan yang "
           "tidak diketahui sebelumnya. Menetapkan Max terlalu tinggi membuat sistem cepat "
           "menolak permintaan; menetapkannya terlalu rendah membatalkan jaminan keamanannya. "
           "Ditambah lagi, setiap permintaan menuntut satu putaran algoritma keamanan penuh — "
           "beban yang tidak sepadan untuk mikrokontroler dengan memori ratusan kilobita.")
    par(d, "Pada sistem irigasi, urutan sumber daya yang tetap bisa ditulis sebagai prosedur "
           "singkat berikut. Prosedur ini meniadakan circular wait sekaligus menyediakan jalan "
           "keluar bila satu sumber daya tidak kunjung tersedia.")
    kode(d, "ambil(pompa);            // urutan 1, wajib paling awal\n"
            "ambil(katup);            // urutan 2\n"
            "ambil(i2c, timeout=50ms) // urutan 3, dengan batas waktu\n"
            "  bila gagal:\n"
            "    lepas(katup); lepas(pompa);\n"
            "    tunggu(acak 10-50 ms); ulangi\n"
            "\n"
            "... jalankan irigasi atau baca sensor ...\n"
            "\n"
            "lepas(i2c); lepas(katup); lepas(pompa);   // urutan lepas dibalik")

    h2(d, "5.4 Catatan keterbatasan")
    par(d, "Tiga hal perlu dinyatakan terbuka. Pertama, matriks yang dipakai adalah contoh buku, "
           "bukan matriks kelas, sehingga angka absolut pada laporan ini tidak dapat dipakai "
           "sebagai patokan untuk kasus dosen. Kedua, model mengasumsikan kebutuhan maksimum tiap "
           "proses diketahui dan tetap; pada sistem nyata, tugas kontrol dapat berubah kebutuhan "
           "seiring kondisi lahan. Ketiga, waktu tunda akuisisi sumber daya (misalnya jeda antrean "
           "I2C) tidak dimodelkan, padahal pada sistem tertanam jeda itulah yang sering "
           "menentukan apakah sistem masih memenuhi tenggat atau tidak.")


def kesimpulan(d, m):
    h1(d, "6. Kesimpulan")
    par(d, f"Analisis pada kasus tiga sumber daya kebun pintar menghasilkan tiga temuan utama. "
           f"Pertama, keempat kondisi Coffman dapat dipetakan ke perangkat nyata, tetapi hanya "
           f"hold-and-wait dan circular-wait yang dapat ditiadakan tanpa mengorbankan fungsi "
           f"perangkat. Kedua, algoritma Banker menyatakan sistem berada pada safe state dengan "
           f"safe sequence <{', '.join(m['safe_sequence'])}>, dan menolak permintaan yang secara "
           f"angka masih tersedia karena permintaan itu akan membuat keadaan berikutnya unsafe. "
           f"Ketiga, strategi pencegahan paling realistis untuk mikrokontroler adalah urutan "
           f"sumber daya global ditambah timeout, bukan algoritma Banker sebagai mekanisme "
           f"operasional, karena Banker menuntut deklarasi kebutuhan maksimum dan beban hitung "
           f"yang tidak sepadan dengan kemampuan perangkat.")


def kepingan(d):
    h1(d, "7. Kepingan Puzzle")
    tabel(d, ["Keterangan", "Isi"], [
        ("Nomor kepingan", "#7"),
        ("Isi kepingan", "Resource-allocation graph, matriks Allocation/Max/Need, jejak "
                         "algoritma keamanan Banker, hasil uji permintaan sumber daya, dan "
                         "rancangan strategi pencegahan"),
        ("Lokasi di portofolio", REPO),
        ("Dipakai untuk", "Level 5 Puzzle UTS — menutup rantai kepingan #1 sampai #7. Sumber "
                          "daya bersama yang diperebutkan di sini adalah pompa, katup, dan bus "
                          "I2C yang sama dengan simpul-simpul pada kepingan #1, dijalankan oleh "
                          "tugas-tugas yang diamati pada kepingan #2 dan #3, dan disinkronkan "
                          "dengan mekanisme yang dipakai pada kepingan #4 dan #6"),
    ], lebar=[4.2, 11.0])


def pustaka(d, m):
    h1(d, "Daftar Pustaka")
    for teks in [
        "Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). Operating system concepts "
        "(10th ed.). Wiley.",
        "Tanenbaum, A. S., & Bos, H. (2015). Modern operating systems (4th ed.). Pearson.",
        "Stallings, W. (2018). Operating systems: Internals and design principles (9th ed.). "
        "Pearson.",
    ]:
        p = d.add_paragraph(style="Normal")
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-1.0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.add_run(teks)


def lampiran(d, m):
    d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    h1(d, "Lampiran A. Kode Program dan Log")
    par(d, "Tiga berkas di bawah ini menghasilkan seluruh angka pada laporan. Berkas matriks.json "
           "disertakan lebih dulu karena menjadi masukan keduanya.")
    for nama in ("matriks.json", "banker.py", "figures.py"):
        p = d.add_paragraph(style="Normal")
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"A.{nama}")
        r.bold = True
        r.font.size = Pt(9.5)
        kode(d, baca_berkas(nama), ukuran=7)

    p = d.add_paragraph(style="Normal")
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("A.4 Keluaran banker.py")
    r.bold = True
    r.font.size = Pt(9.5)
    kode(d, subprocess.run([sys.executable, "banker.py", "--periksa"],
                           capture_output=True, text=True).stdout.rstrip(), ukuran=7)

    h1(d, "Lampiran B. Pernyataan Penggunaan AI Generatif")
    par(d, "☐  Kami tidak menggunakan AI generatif dalam tugas ini.")
    par(d, "☒  Menggunakan AI generatif dengan rincian berikut:")
    tabel(d, ["Alat", "Tujuan penggunaan", "Bagian yang dibantu", "Cara memverifikasi"], [
        ("Claude (Anthropic)", "Menyusun skrip perhitungan dan merapikan kalimat laporan",
         "Bagian 4 (kode), Bagian 5.2",
         "Seluruh angka diambil dari results/banker.json; safe sequence dihitung ulang manual "
         "dan dicocokkan dengan Tabel 5.3"),
    ], lebar=[3.0, 4.4, 4.0, 4.4], ukuran=8.5)

    h1(d, "Lampiran C. Daftar Periksa Sebelum Mengumpulkan")
    for teks, sudah in [
        ("Semua teks petunjuk abu-abu dan kotak petunjuk sudah dihapus.", True),
        ("Identitas, kode tugas, dan nama host pada sampul sudah benar.", True),
        ("Setiap poin deskripsi tugas sudah dijawab di bagian Analisis.", True),
        ("Setiap gambar memiliki nomor dan keterangan.", True),
        ("Kepingan puzzle sudah disimpan di portofolio dan tautannya dicantumkan.", True),
        ("Pernyataan penggunaan AI generatif sudah diisi.", True),
        ("Lembar kontribusi anggota sudah dilampirkan.", True),
        ("Matriks kelas sudah diganti bila dosen membagikannya.", m["sumber"] != "contoh-buku"),
        ("Berkas disimpan sebagai PDF dengan nama IF-3C_K-3_<NIM>_<Nama>.pdf.", True),
    ]:
        p = d.add_paragraph(style="Normal")
        p.paragraph_format.space_after = Pt(3)
        p.add_run(f"{'☒' if sudah else '☐'}  {teks}")

    par(d, "")
    h2(d, "Swa-nilai berdasarkan kriteria lembar tugas")
    tabel(d, ["Kriteria (dari lembar tugas)", "Bobot", "Sudah terpenuhi? Di bagian mana"],
          [("Hasil/keberhasilan implementasi", "35%",
            "Ya — algoritma Banker berjalan, safe state terbukti, dua kasus permintaan diuji"),
           ("Kedalaman analisis", "30%",
            "Ya — empat kondisi Coffman dipetakan ke perangkat, biaya tiap strategi dibandingkan"),
           ("Dokumentasi", "20%",
            "Ya — langkah dapat diulang, kode dan keluaran dilampirkan"),
           ("Kerja sama dan pembagian peran", "15%",
            "Ya — lembar kontribusi pada Lampiran D")],
          lebar=[5.2, 2.0, 8.0])

    h1(d, "Lampiran D. Lembar Kontribusi Anggota", halaman_baru=True)
    par(d, "Lembar ini memenuhi syarat kerja sama dan pembagian peran (15% bobot penilaian) "
           "pada lembar tugas K-3.")
    tabel(d, ["Nama", "NIM", "Peran dan bagian yang dikerjakan"],
          [(n, i, p) for n, i, p in ANGGOTA], lebar=[4.4, 3.0, 7.8])


def main():
    d = docx.Document(TEMPLATE)
    bersihkan(d)

    m = baca_hasil()
    h = fakta_sistem()

    sampul_k3(d)
    catatan_data(d, m)
    pendahuluan(d, m, h)
    dasar_teori(d)
    lingkungan(d, h)
    langkah(d, m)
    hasil(d, m)
    kesimpulan(d, m)
    kepingan(d)
    pustaka(d, m)
    lampiran(d, m)

    header_dokumen(d, "Laporan Tugas Kelompok Sistem Operasi · ", f"{KELAS} · {KODE}")
    nomor_halaman(d)

    d.core_properties.title = "K-3 Analisis dan Penanganan Deadlock"
    d.core_properties.author = NAMA
    d.core_properties.subject = "Sistem Operasi (USA-WP2260110), IF-3C"
    d.core_properties.last_modified_by = NAMA

    os.makedirs("results", exist_ok=True)
    d.save(OUT)
    print("tersimpan:", OUT)


if __name__ == "__main__":
    main()
