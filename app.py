"""
=============================================================
  SISTEM DETEKSI BAHASA BAKU DAN TIDAK BAKU - VERSI 2.1
=============================================================
Framework : Flask
Fitur Baru: Upload PDF/DOCX/TXT, Highlight Kata, Statistik
Metode    : Dictionary-based + Rule-based NLP
Update    : Kamus diperluas dengan slang & gaul terbaru 2025
=============================================================
"""

from flask import Flask, render_template, request, jsonify
import re
import os
import tempfile
from collections import Counter
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Max 10MB
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}


# ============================================================
# BAGIAN 1: KAMUS KATA TIDAK BAKU (UPGRADED v2.1)
# ============================================================

KAMUS_TIDAK_BAKU = {

    # ----------------------------------------------------------
    # [A] SINGKATAN KLASIK & UMUM
    # ----------------------------------------------------------
    "yg": "yang", "dg": "dengan", "dgn": "dengan",
    "krn": "karena", "karna": "karena",
    "udah": "sudah", "udh": "sudah", "sdh": "sudah",
    "blm": "belum", "blom": "belum",
    "mo": "mau",
    "gak": "tidak", "ga": "tidak", "nggak": "tidak",
    "ngga": "tidak", "enggak": "tidak", "gk": "tidak",
    "tdk": "tidak", "kagak": "tidak", "kaga": "tidak",
    "emang": "memang", "emg": "memang",
    "kmrn": "kemarin", "kemaren": "kemarin",
    "bwt": "untuk", "trus": "terus",
    "abis": "habis", "abiz": "habis",
    "gimana": "bagaimana", "gmn": "bagaimana", "bgmn": "bagaimana",
    "banget": "sekali", "bgt": "sekali", "bngt": "sekali",
    "lo": "kamu", "lu": "kamu", "loe": "kamu",
    "gue": "saya", "gw": "saya", "gu": "saya",
    "tau": "tahu", "tw": "tahu",
    "doang": "saja", "dong": "lah", "nih": "ini",
    "ntu": "itu", "tuh": "itu",
    "kek": "seperti", "kayak": "seperti", "kaya": "seperti",
    "pake": "pakai", "pke": "pakai",
    "bikin": "membuat", "bikinin": "membuatkan",
    "ampe": "sampai", "sampe": "sampai", "nyampe": "sampai",
    "kalo": "kalau", "klo": "kalau", "klw": "kalau",
    "oke": "baik", "ok": "baik",
    "iya": "ya", "yep": "ya", "yups": "ya",
    "ntar": "nanti", "tar": "nanti",
    "bakal": "akan", "bakalan": "akan",
    "nyari": "mencari", "nemu": "menemukan",
    "ngomong": "berbicara", "bilang": "mengatakan",
    "liat": "melihat", "liad": "melihat",
    "diem": "diam", "minta": "meminta",
    "kasih": "memberikan",
    "temen": "teman", "tman": "teman", "tmn": "teman",
    "cuma": "hanya", "cman": "hanya", "cm": "hanya",
    "aja": "saja", "aj": "saja",
    "jg": "juga",
    "dll": "dan lain-lain", "dsb": "dan sebagainya",
    "dst": "dan seterusnya",
    "yuk": "mari", "yukk": "mari",
    "hrs": "harus",
    "lg": "lagi", "skrg": "sekarang",
    "skg": "sekarang", "skr": "sekarang",
    "msh": "masih", "msih": "masih",
    "sdg": "sedang", "pny": "punya",
    "keren": "bagus", "mantap": "bagus", "mantul": "sangat bagus",
    "bro": "saudara", "sob": "sahabat",
    "btw": "omong-omong", "fyi": "sebagai informasi",
    "cmiiw": "koreksi jika salah", "otw": "dalam perjalanan",
    "napa": "mengapa", "ngapain": "untuk apa",
    "cape": "lelah", "capek": "lelah",
    "gitu": "begitu", "gini": "begini",
    "sempet": "sempat",
    "macem": "macam",
    "bareng": "bersama", "barengan": "bersama-sama",
    "dapet": "dapat", "buat": "untuk",
    "entar": "nanti", "bentar": "sebentar",
    "pengen": "ingin", "kepingin": "ingin",
    "bete": "kesal", "males": "malas",

    # ----------------------------------------------------------
    # [B] KATA KERJA TIDAK BAKU (me- / ber- / ter- dilesapkan)
    # ----------------------------------------------------------
    "ngerti": "mengerti", "ngertiin": "memahamkan",
    "nyalahin": "menyalahkan", "nyuruh": "menyuruh",
    "ngasih": "memberikan", "ngambil": "mengambil",
    "numpahin": "menumpahkan", "ngebuang": "membuang",
    "ngebahas": "membahas", "ngedatengin": "mendatangi",
    "ngejagain": "menjaga", "ngebantu": "membantu",
    "ngejual": "menjual", "ngobrol": "berbicara",
    "nganterin": "mengantar", "ngerasain": "merasakan",
    "ngejar": "mengejar", "ngejaga": "menjaga",
    "ngebuat": "membuat", "ngepoin": "memata-matai",
    "ngehapus": "menghapus", "ngecheck": "memeriksa",
    "ngepost": "memposting", "ngeshare": "membagikan",
    "ngedownload": "mengunduh", "ngeupload": "mengunggah",
    "ngelist": "mendaftar", "ngitung": "menghitung",
    "ngajak": "mengajak", "ngelamar": "melamar",
    "ngomelin": "memarahi", "ngebenerin": "membetulkan",
    "ngeliat": "melihat", "ngedenger": "mendengar",
    "ngerasain": "merasakan", "ngetik": "mengetik",
    "ngeklik": "mengklik", "ngebaca": "membaca",
    "ngajarin": "mengajarkan", "ngitung": "menghitung",
    "nyimpen": "menyimpan", "nyerahin": "menyerahkan",
    "nyebut": "menyebut", "nyiapin": "menyiapkan",
    "nyoba": "mencoba", "nyontek": "mencontek",
    "nyanyi": "bernyanyi", "nari": "menari",
    "nonton": "menonton", "nungguin": "menunggu",
    "nulis": "menulis", "ngedit": "mengedit",
    "mesen": "memesan", "miara": "memelihara",
    "mikir": "berpikir", "moto": "memotret",
    "matiin": "mematikan", "munculin": "memunculkan",
    "bisikin": "membisikkan", "beliin": "membelikan",
    "bayangin": "membayangkan", "bacain": "membacakan",

    # ----------------------------------------------------------
    # [C] BAHASA GAUL / SLANG POPULER (2020–2022)
    # ----------------------------------------------------------
    "gabut": "tidak ada kegiatan", "mager": "malas bergerak",
    "baper": "terbawa perasaan", "kepo": "ingin tahu",
    "lebay": "berlebihan", "galau": "bimbang",
    "bucin": "budak cinta", "php": "pemberi harapan palsu",
    "apdet": "pembaruan", "japri": "jalur pribadi",
    "kondangan": "menghadiri pesta",
    "julid": "iri dan dengki", "nyinyir": "berkomentar sinis",
    "bonyok": "orang tua", "ortu": "orang tua",
    "cogan": "cowok tampan", "cece": "kakak perempuan",
    "kece": "keren", "cetar": "memukau",
    "modus": "memiliki niat tersembunyi",
    "baper": "terbawa perasaan",
    "selow": "santai", "selo": "santai",
    "awkarin": "pengaruh negatif",
    "bego": "bodoh", "goblok": "bodoh",
    "sotoy": "sok tahu", "songong": "sombong",
    "santuy": "santai", "santai": "tenang",
    "garing": "tidak lucu", "jayus": "tidak lucu",
    "receh": "murahan/tidak lucu",
    "pedes": "pedas", "asin": "tidak menyenangkan",
    "hits": "populer", "viral": "menyebar luas",
    "ngehits": "menjadi populer",
    "halu": "berhalusinasi", "halusinasi": "khayalan",
    "bodo amat": "tidak peduli",
    "sombong": "angkuh", "geer": "terlalu percaya diri",
    "cringe": "memalukan", "awkward": "canggung",
    "baper parah": "sangat terbawa perasaan",
    "kepo banget": "sangat ingin tahu",

    # ----------------------------------------------------------
    # [D] SLANG GEN Z TERBARU (2023–2025)
    # ----------------------------------------------------------
    # Ungkapan positif / persetujuan
    "no cap": "sungguh-sungguh", "nocap": "sungguh-sungguh",
    "real": "benar sekali", "fr": "sungguh",
    "frfr": "sungguh-sungguh", "slay": "tampil memukau",
    "slaying": "tampil memukau", "based": "berpendapat berani",
    "lowkey": "diam-diam", "highkey": "terang-terangan",
    "fire": "luar biasa bagus", "lit": "seru sekali",
    "bussin": "sangat enak/bagus", "bussing": "sangat bagus",
    "goated": "terbaik", "goat": "terbaik",
    "rizz": "daya tarik", "rizzed": "berhasil menarik perhatian",
    "rizzing": "menarik perhatian",
    "vibe": "suasana/nuansa", "vibes": "suasana",
    "valid": "benar/tepat", "legit": "asli/benar",
    "bet": "setuju/baik", "sip": "baik sekali",
    "periodt": "titik, sudah pasti", "period": "sudah pasti",
    "understood the assignment": "memahami tugas dengan baik",
    "ate": "berhasil tampil sempurna",
    "iconic": "tak terlupakan", "legendary": "luar biasa",
    "rent free": "selalu terpikirkan",
    "main character": "tokoh utama (percaya diri)",
    "understood": "dimengerti",
    "iykyk": "jika kamu tahu kamu tahu",
    "ngl": "jujur saja", "imo": "menurut saya",
    "imho": "menurut pendapat saya yang rendah",
    "tbh": "jujur saja", "istg": "demi Tuhan",
    "irl": "di kehidupan nyata",

    # Ungkapan negatif / kritik
    "mid": "biasa saja/tidak istimewa",
    "cap": "bohong", "capping": "berbohong",
    "cooked": "habis/dalam masalah besar",
    "sus": "mencurigakan", "sussy": "mencurigakan",
    "ratio": "kalah perdebatan di media sosial",
    "ratioed": "komentar lebih banyak dari suka",
    "L": "kekalahan", "taking an L": "mengalami kekalahan",
    "W": "kemenangan", "taking a W": "meraih kemenangan",
    "NPC": "orang yang bertindak tanpa pikiran sendiri",
    "pick me": "mencari perhatian dengan merendahkan sesama",
    "simp": "terlalu memuja seseorang",
    "simping": "terlalu memuja",
    "red flag": "tanda peringatan", "redflag": "tanda peringatan",
    "green flag": "tanda baik", "greenflag": "tanda baik",
    "toxic": "bersifat merusak",
    "boomer": "orang dengan pola pikir kuno",
    "karen": "orang yang suka komplain berlebihan",
    "doomscrolling": "terus menggulir berita buruk",
    "doom scroll": "menggulir konten negatif terus-menerus",

    # Ekspresi emosi & reaksi
    "ded": "sangat lucu hingga seolah mati",
    "im dead": "sangat lucu",
    "sending me": "membuat tertawa terbahak",
    "screaming": "sangat terkejut/lucu",
    "living for this": "sangat menyukainya",
    "obsessed": "sangat terobsesi",
    "shook": "terkejut", "shookt": "sangat terkejut",
    "pressed": "kesal/tersinggung",
    "salty": "kesal/iri",
    "triggered": "terpancing emosi",
    "stressed": "tertekan",
    "ghosting": "mengabaikan tanpa kabar",
    "ghosted": "diabaikan tanpa kabar",
    "breadcrumbing": "memberi harapan palsu tipis-tipis",
    "situationship": "hubungan tanpa status jelas",
    "talking stage": "tahap pendekatan",
    "catching feelings": "mulai jatuh cinta",
    "soft launch": "memperkenalkan pasangan secara samar",
    "hard launch": "mengumumkan hubungan secara terang-terangan",

    # Kata sifat gaul
    "delulu": "berangan-angan tidak realistis",
    "delusion": "khayalan",
    "cheugy": "ketinggalan zaman",
    "basic": "tidak orisinal/umum",
    "extra": "berlebihan",
    "petty": "dendam hal kecil",
    "shady": "mencurigakan/licik",
    "messy": "tidak teratur/dramatis",
    "thirsty": "sangat ingin perhatian",
    "slay queen": "wanita yang tampil memukau",
    "unbothered": "tidak terganggu",
    "that girl": "perempuan yang produktif dan percaya diri",
    "glowup": "perubahan penampilan menjadi lebih baik",
    "glow up": "perubahan menjadi lebih baik",

    # ----------------------------------------------------------
    # [E] ISTILAH MEDIA SOSIAL & INTERNET
    # ----------------------------------------------------------
    "feed": "beranda", "timeline": "linimasa",
    "story": "cerita", "reels": "video pendek",
    "fyp": "untuk halaman kamu",
    "fypシ": "untuk halaman kamu",
    "xyzbca": "tag algoritma",
    "pov": "sudut pandang", "ootd": "pakaian hari ini",
    "throwback": "kenangan masa lalu", "tbt": "kenangan masa lalu",
    "selfie": "foto diri sendiri", "wefie": "foto bersama",
    "unboxing": "membuka kemasan produk baru",
    "haul": "belanjaan/koleksi baru",
    "mukbang": "makan bersama di depan kamera",
    "vlog": "blog video", "vlogger": "pembuat blog video",
    "influencer": "pemengaruh", "konten kreator": "pencipta konten",
    "endorse": "mendukung berbayar",
    "collab": "kolaborasi", "collabs": "kolaborasi",
    "dm": "pesan langsung", "dms": "pesan-pesan langsung",
    "pm": "pesan pribadi",
    "spam": "kiriman massal tak diinginkan",
    "spoiler": "bocoran cerita",
    "spoileran": "bocoran cerita",
    "react": "bereaksi", "reaction": "reaksi",
    "thread": "utas", "unroll": "buka utas",
    "trending": "sedang populer",
    "ngetrend": "sedang populer",
    "explore": "halaman jelajah",
    "followers": "pengikut", "following": "mengikuti",
    "unfoll": "berhenti mengikuti", "unfollow": "berhenti mengikuti",
    "mute": "bisukan", "block": "blokir",
    "report": "laporkan",
    "like": "suka", "dislike": "tidak suka",
    "subscribe": "berlangganan", "sub": "berlangganan",
    "unsub": "berhenti berlangganan",
    "komen": "komentar", "komen dong": "beri komentar",
    "save": "simpan", "share": "bagikan",
    "repost": "memposting ulang", "retweet": "meneruskan cuitan",
    "quote tweet": "membalas sambil meneruskan",
    "caption": "keterangan foto",
    "hashtag": "tagar",

    # ----------------------------------------------------------
    # [F] BAHASA ALAY / LEBAY / LEBAY 2.0
    # ----------------------------------------------------------
    "wkwk": "[ekspresi tawa]", "hehe": "[ekspresi tawa]",
    "haha": "[ekspresi tawa]", "xixi": "[ekspresi tawa]",
    "wkwkwk": "[ekspresi tawa]", "kwkwk": "[ekspresi tawa]",
    "lol": "[ekspresi tawa]", "lmao": "[tertawa keras]",
    "lmfao": "[tertawa sangat keras]", "rofl": "[tertawa berguling]",
    "omg": "astaga", "omgg": "astaga",
    "wtf": "apa-apaan ini", "wth": "apa-apaan ini",
    "nvm": "tidak apa-apa", "nevermind": "tidak apa-apa",
    "idc": "tidak peduli", "idgaf": "benar-benar tidak peduli",
    "smh": "menggelengkan kepala", "ugh": "aduh",
    "uwu": "[ekspresi imut]", "owo": "[ekspresi terkejut imut]",
    "gg": "permainan bagus", "ggs": "permainan bagus sekali",
    "brb": "segera kembali", "bbl": "segera kembali",
    "afk": "jauh dari keyboard", "ttyl": "bicara nanti",
    "ty": "terima kasih", "thx": "terima kasih",
    "tysm": "terima kasih banyak",
    "np": "tidak masalah", "yw": "sama-sama",
    "asl": "umur lokasi jenis kelamin",
    "asap": "sesegera mungkin",
    "rn": "saat ini", "atm": "saat ini",
    "tbf": "jujur saja",
    "nbd": "bukan masalah besar", "no biggie": "tidak masalah",
    "gtg": "harus pergi", "g2g": "harus pergi",
    "imo": "menurut saya", "imho": "menurut hemat saya",
    "jk": "bercanda", "j/k": "bercanda",
    "lmk": "beri tahu saya", "hmu": "hubungi saya",
    "ikr": "iya kan", "ik": "saya tahu",
    "idk": "saya tidak tahu", "idk bro": "saya tidak tahu",
    "idc": "saya tidak peduli",
    "smth": "sesuatu", "sth": "sesuatu",

    # ----------------------------------------------------------
    # [G] ISTILAH GAME & E-SPORTS
    # ----------------------------------------------------------
    "noob": "pemain pemula", "n00b": "pemain pemula",
    "pro": "pemain profesional", "tryhard": "bermain terlalu serius",
    "afk": "meninggalkan permainan sementara",
    "dc": "terputus dari permainan",
    "lag": "koneksi lambat", "ngelag": "mengalami koneksi lambat",
    "gg wp": "permainan bagus dimainkan dengan baik",
    "ez": "mudah", "izi": "mudah",
    "op": "terlalu kuat/unggul", "overpower": "terlalu kuat",
    "buff": "penguatan karakter", "nerf": "pelemahan karakter",
    "meta": "strategi paling efektif saat ini",
    "ranked": "mode peringkat", "casual": "mode santai",
    "bot": "robot/pemain buruk",
    "feeder": "pemain yang terus mati",
    "carry": "pemain yang menanggung tim",
    "joki": "menggunakan jasa pemain lain untuk naik peringkat",
    "push rank": "bermain untuk naik peringkat",
    "tierlist": "daftar peringkat karakter/item",
    "spawn": "kemunculan karakter setelah mati",
    "respawn": "kemunculan kembali",
    "cooldown": "waktu tunggu kemampuan",
    "ulti": "kemampuan pamungkas", "ult": "kemampuan pamungkas",
    "poke": "menyerang dari jarak jauh",
    "gank": "menyerang secara tiba-tiba dari luar jalur",
    "backdoor": "menyerang markas langsung tanpa diketahui",
    "rotasi": "berpindah jalur dalam permainan",
    "push": "maju menyerang",

    # ----------------------------------------------------------
    # [H] ISTILAH FINANSIAL / CRYPTO / INVESTASI INFORMAL
    # ----------------------------------------------------------
    "cuan": "keuntungan", "profit": "keuntungan",
    "boncos": "rugi", "buntung": "rugi",
    "bullish": "optimis pasar naik",
    "bearish": "pesimis pasar turun",
    "mooning": "harga naik sangat tinggi",
    "dumpor": "harga anjlok drastis",
    "hodl": "tahan aset meski turun",
    "fomo": "takut ketinggalan peluang",
    "fud": "ketakutan ketidakpastian keraguan",
    "whale": "investor besar",
    "rekt": "rugi besar", "liquidated": "dilikuidasi",
    "airdrop": "pembagian koin gratis",
    "token": "mata uang kripto", "coin": "koin kripto",
    "nft": "token yang tidak dapat dipertukarkan",
    "defi": "keuangan terdesentralisasi",
    "rug pull": "penipuan proyek kripto",
    "pump": "menaikkan harga secara buatan",
    "dump": "menjual massal untuk turunkan harga",
    "passive income": "penghasilan pasif",
    "side hustle": "pekerjaan sampingan",
    "freelance": "pekerja lepas",

    # ----------------------------------------------------------
    # [I] KATA GANTI & SAPAAN TIDAK BAKU
    # ----------------------------------------------------------
    "aku": "saya", "kamu": "Anda",
    "dia": "beliau/ia", "mereka": "mereka (konteks formal: para pihak)",
    "kalian": "Anda sekalian",
    "si": "seseorang (jangan digunakan formal)",
    "si doi": "orang tersebut", "doi": "dia/orang itu",
    "gebetan": "seseorang yang disukai",
    "mantan": "mantan pasangan",
    "pacar": "kekasih", "cowok": "pria", "cewek": "wanita",
    "bokap": "ayah", "nyokap": "ibu",
    "kakak": "saudara perempuan/laki-laki lebih tua",
    "adek": "saudara lebih muda", "adik": "saudara lebih muda",

    # ----------------------------------------------------------
    # [J] KATA SERAPAN ASING TIDAK BAKU (DISERAP SETENGAH)
    # ----------------------------------------------------------
    "meeting": "rapat", "meetup": "pertemuan",
    "update": "pembaruan", "upgrade": "peningkatan",
    "download": "unduh", "upload": "unggah",
    "chat": "percakapan", "chatting": "bercakap-cakap",
    "texting": "berkirim pesan", "calling": "menelepon",
    "googling": "mencari di Google",
    "browsing": "menjelajah internet",
    "nge-google": "mencari menggunakan Google",
    "streaming": "menonton secara daring",
    "ngestream": "menonton secara daring",
    "password": "kata sandi", "username": "nama pengguna",
    "email": "surel", "online": "daring", "offline": "luring",
    "handle": "nama akun", "account": "akun",
    "link": "tautan", "click": "klik",
    "screenshot": "tangkapan layar", "ss": "tangkapan layar",
    "screenshoot": "tangkapan layar",
    "copy paste": "salin tempel",
    "nge-zoom": "melakukan rapat video",
    "zoom-an": "rapat via video",
    "hybrid": "campuran daring dan luring",
    "wfh": "bekerja dari rumah", "wfo": "bekerja dari kantor",
    "remote": "jarak jauh",

    # ----------------------------------------------------------
    # [K] EKSPRESI KERESAHAN / KELUHAN TIDAK BAKU
    # ----------------------------------------------------------
    "aduh": "astaga", "duh": "astaga",
    "hadeh": "astaga", "haduh": "astaga",
    "lah": "partikel penegas", "lho": "partikel kejutan",
    "sih": "partikel penegas", "kok": "partikel tanya",
    "toh": "partikel penegas akhir kalimat",
    "deh": "partikel pelembut", "kan": "bukan begitu",
    "nah": "nah (tidak baku di teks formal)",
    "ya ampun": "astaga", "ampun deh": "astaga",
    "ya elah": "astaga", "elah": "astaga",
    "anjir": "ekspresi kejutan/kekesalan",
    "anjay": "ekspresi kejutan/kekesalan",
    "astagfirullah": "mohon ampun Allah",
    "masyaallah": "sungguh luar biasa",
    "alhamdulillah": "puji syukur kepada Allah",

    # ----------------------------------------------------------
    # [L] KATA PENGISI / FILLER TIDAK BAKU
    # ----------------------------------------------------------
    "genre": "jenis", "type": "jenis/tipe",
    "literally": "secara harfiah", "basically": "pada dasarnya",
    "actually": "sebenarnya", "honestly": "sejujurnya",
    "seriously": "sungguh-sungguh",
    "like": "seperti (filler)",
    "you know": "Anda tahu",
    "i mean": "maksud saya",
    "so": "jadi (filler di awal kalimat)",
    "well": "nah (filler)",
    "kind of": "semacam", "sort of": "semacam",
    "stuff": "hal-hal", "things": "hal-hal",

    # ----------------------------------------------------------
    # [M] ISTILAH PENDIDIKAN / PELAJAR TIDAK BAKU
    # ----------------------------------------------------------
    "pr": "pekerjaan rumah", "tugas": "tugas",
    "matkul": "mata kuliah", "dospem": "dosen pembimbing",
    "dosen": "pengajar perguruan tinggi",
    "skripsi": "tugas akhir strata satu",
    "kelas online": "pembelajaran daring",
    "absen": "absensi/ketidakhadiran",
    "izin": "memohon izin",
    "cabut": "meninggalkan sekolah tanpa izin",
    "bolos": "tidak masuk tanpa izin",
    "nyontek": "mencontek",
    "remedial": "perbaikan nilai",
    "ujian": "evaluasi",
    "les": "kursus/bimbingan belajar",
    "ospek": "orientasi mahasiswa baru",
    "wisuda": "upacara kelulusan",
    "cumlaude": "lulus dengan pujian",
    "ipk": "indeks prestasi kumulatif",

    # ----------------------------------------------------------
    # [N] KATA MAJEMUK TIDAK BAKU
    # ----------------------------------------------------------
    "banyak bgt": "sangat banyak",
    "pengen bgt": "sangat ingin",
    "suka bgt": "sangat suka",
    "capek bgt": "sangat lelah",
    "gak mau": "tidak mau",
    "gak bisa": "tidak bisa",
    "gak tau": "tidak tahu",
    "gak ngerti": "tidak mengerti",
    "gak ada": "tidak ada",
    "gak punya": "tidak memiliki",
    "gak jelas": "tidak jelas",
    "gak penting": "tidak penting",
    "gak nyambung": "tidak nyambung",
    "bodo amat": "tidak peduli sama sekali",
    "terserah": "terserah (agak kasar dalam konteks formal)",
    "malas bgt": "sangat malas",
    "hampir2": "hampir-hampir",
    "macem2": "bermacam-macam",
    "barengan": "bersama-sama",
    "dipikir2": "dipikir-pikir",
    "sebentar2": "sebentar-sebentar",
    "gimana2": "bagaimana pun juga",

    # ----------------------------------------------------------
    # [O] SINGKATAN TIDAK RESMI BARU
    # ----------------------------------------------------------
    "btw": "omong-omong",
    "ngl": "jujur saja",
    "imo": "menurut saya",
    "tbh": "jujur saja",
    "istg": "sungguh-sungguh",
    "irl": "di kehidupan nyata",
    "idk": "saya tidak tahu",
    "imo": "menurut saya",
    "smh": "menggelengkan kepala",
    "lmk": "beri tahu saya",
    "hmu": "hubungi saya",
    "wyd": "sedang apa",
    "wbu": "bagaimana denganmu",
    "rn": "saat ini juga",
    "nvm": "tidak apa-apa",
    "jk": "hanya bercanda",
    "ikr": "iya betul kan",
    "ofc": "tentu saja", "obvs": "jelas sekali",
    "imo": "menurut pendapat saya",
    "tbf": "harus diakui",
    "imo": "menurut saya",
    "iirc": "jika saya ingat benar",
    "afaik": "sejauh yang saya ketahui",
    "tl;dr": "ringkasnya",
    "ama": "tanya saya apa saja",
    "eli5": "jelaskan seperti kepada anak lima tahun",
    "nsfw": "tidak cocok ditonton di tempat kerja",
    "sfw": "aman ditonton di tempat kerja",
    "ama": "tanya apa saja",

    # ----------------------------------------------------------
    # [P] KATA SLANG REGIONAL POPULER
    # ----------------------------------------------------------
    # Betawi/Jakarta
    "nyak": "ibu", "babe": "ayah",
    "ente": "kamu", "ane": "saya",
    "die": "dia", "kagak": "tidak",
    "nyang": "yang", "aje": "saja",
    "kite": "kita", "same": "sama",
    "entar": "nanti", "mane": "mana",
    # Jawa (populer di media sosial)
    "awakmu": "kamu", "aku": "saya",
    "ngono": "begitu", "ngene": "begini",
    "piye": "bagaimana", "ngopo": "kenapa",
    "ra": "tidak", "ora": "tidak",
    "iso": "bisa", "gelem": "mau",
    "wes": "sudah", "durung": "belum",
    "melu": "ikut", "mrene": "kemari",
    # Sunda (populer di media sosial)
    "maneh": "kamu", "abdi": "saya",
    "aing": "saya (kasar)", "sia": "kamu (kasar)",
    "kumaha": "bagaimana", "naon": "apa",
    "naha": "kenapa", "enya": "ya/iya",
    "henteu": "tidak", "moal": "tidak akan",
    "geulis": "cantik", "kasep": "tampan",
    # Batak (populer di Medan & sekitarnya)
    "au": "saya", "ho": "kamu",
    "aha": "apa", "dia": "dia",
    "unang": "jangan", "sai": "selalu",
    "gabe": "jadi/menjadi",
    # Makassar/Bugis
    "ki": "partikel hormat",
    "mi": "partikel penegas",
    "ji": "saja/juga",
    "ko": "kamu", "ku": "saya",
    "iye": "ya/iya",

    # ----------------------------------------------------------
    # [Q] KATA TIDAK BAKU EKSTRA (SEBELUMNYA TERLEWAT)
    # ----------------------------------------------------------
    "mending": "lebih baik", "mendingan": "lebih baik",
    "ogah": "tidak mau", "males": "malas",
    "rajin": "tekun (baku, tapi sering salah konteks)",
    "sering": "kerap",
    "jarang": "jarang (baku)",
    "pernah": "pernah (baku)",
    "belom": "belum",
    "udah dong": "sudah lah",
    "kelamaan": "terlalu lama",
    "kebanyakan": "terlalu banyak",
    "kesorean": "terlalu sore",
    "kemaleman": "terlalu malam",
    "kepagian": "terlalu pagi",
    "keburu": "tergesa-gesa",
    "keteteran": "kewalahan",
    "kekeuh": "teguh pendirian (Sunda)",
    "bawel": "banyak bicara", "cerewet": "banyak bicara",
    "curcol": "curahan hati dan kolom",
    "curhat": "curahan hati",
    "nangis": "menangis", "nangisin": "menangisi",
    "ketawa": "tertawa", "ketawain": "menertawai",
    "senyum": "tersenyum (baku)",
    "senyumin": "tersenyumi",
    "dikit": "sedikit", "banyakan": "lebih banyak",
    "sedikit2": "sedikit-sedikit",
    "pelan2": "pelan-pelan",
    "cepet": "cepat", "cepetan": "lebih cepat",
    "lelet": "lambat", "lemot": "lambat memproses",
    "ribet": "rumit", "mumet": "pusing",
    "pusying": "pusing",
    "bingung": "bingung (baku, tapi sering informal)",
    "mumet": "pusing", "puyeng": "pusing",
    "capek": "lelah", "kecapean": "kelelahan",
    "ngantuk": "mengantuk", "ketiduran": "tertidur tidak sengaja",
    "kebablasan": "terlalu jauh/kelewatan",
    "ngebut": "melaju cepat",
    "ngerem": "mengerem",
    "nyopir": "mengemudi",
    "naik grab": "menggunakan layanan Grab",
    "naik gojek": "menggunakan layanan Gojek",
    "ojol": "ojek daring",
    "gofood": "layanan pesan antar makanan Gojek",
    "grabfood": "layanan pesan antar makanan Grab",
    "shopee": "platform belanja daring Shopee",
    "tokped": "Tokopedia",
    "bukalapak": "platform belanja daring Bukalapak",
    "toped": "Tokopedia",
}

POLA_TIDAK_BAKU = [
    (r'\b\w*[0-9]+\w*\b', "Penggunaan angka sebagai pengganti huruf (misalnya: 4ku, t3man)"),
    (r'\b\w*(.)(?:\1){2,}\w*\b', "Pengulangan huruf berlebihan (misalnya: bangeeet, okeeee)"),
    (r'[?!]{2,}', "Tanda baca berulang (!!, ??, !?)"),
    (r'\b(wkwk|hehe|haha|xixi|hihi|xoxo|lol|lmao|lmfao|rofl)+\b', "Ekspresi tawa tidak baku"),
    (r'\b(yg|dg|dgn|krn|blm|sdh|tdk|dll|dsb|dst|jg|lg|skrg|msh|sdg|pny|fr|ngl|tbh|idk|rn|nvm|jk|ikr|ofc)\b',
     "Singkatan tidak resmi"),
    (r'\b(no cap|low key|high key|red flag|green flag|rent free|glow up|main character)\b',
     "Ungkapan slang bahasa Inggris tidak baku"),
]


# ============================================================
# BAGIAN 2: PARSING DOKUMEN
# ============================================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_txt(filepath):
    """Baca file TXT biasa."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def extract_text_from_pdf(filepath):
    """Ekstrak teks dari file PDF menggunakan PyMuPDF atau pypdf."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except ImportError:
            return None


def extract_text_from_docx(filepath):
    """Ekstrak teks dari file DOCX menggunakan python-docx."""
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except ImportError:
        return None


# ============================================================
# BAGIAN 3: PREPROCESSING & DETEKSI
# ============================================================

def preprocessing(teks):
    teks_lower = teks.lower()
    token_kata = re.findall(r'\b[a-z]+\b', teks_lower)
    return teks_lower, token_kata


def build_highlighted_text(teks, kata_tidak_baku_set, saran_perbaikan):
    """
    Buat HTML dengan highlight pada kata tidak baku.
    Setiap kata tidak baku dibungkus dengan <mark> dan tooltip saran.
    """
    def replace_word(match):
        word = match.group(0)
        word_lower = word.lower()
        if word_lower in kata_tidak_baku_set:
            saran = saran_perbaikan.get(word_lower, "-")
            return (
                f'<mark class="highlight-kata" '
                f'data-saran="{saran}" '
                f'title="Saran: {saran}">{word}</mark>'
            )
        return word

    pattern = r'\b[a-zA-Z]+\b'
    return re.sub(pattern, replace_word, teks)


def deteksi_bahasa(teks):
    """
    Fungsi utama deteksi bahasa baku/tidak baku.
    Mengembalikan hasil lengkap termasuk highlighted text.
    """
    if not teks or len(teks.strip()) == 0:
        return {"error": "Teks kosong"}

    teks_lower, token_kata = preprocessing(teks)

    if not token_kata:
        return {"error": "Tidak ada kata yang dapat dianalisis"}

    # Deteksi kata tidak baku dari kamus
    temuan_tidak_baku = []
    saran_perbaikan = {}
    frekuensi_tidak_baku = Counter()

    for kata in token_kata:
        if kata in KAMUS_TIDAK_BAKU:
            temuan_tidak_baku.append(kata)
            saran_perbaikan[kata] = KAMUS_TIDAK_BAKU[kata]
            frekuensi_tidak_baku[kata] += 1

    # Deteksi pola tidak baku (regex)
    temuan_pola = []
    for pola, keterangan in POLA_TIDAK_BAKU:
        if re.search(pola, teks_lower):
            temuan_pola.append(keterangan)

    # Hitung statistik
    total_kata = len(token_kata)
    kata_tidak_baku_count = len(temuan_tidak_baku)
    kata_tidak_baku_unik = list(set(temuan_tidak_baku))

    persentase_tidak_baku = (kata_tidak_baku_count / total_kata) * 100
    penalti_pola = len(temuan_pola) * 5
    persentase_tidak_baku = min(100, persentase_tidak_baku + penalti_pola)
    skor_baku = round(100 - persentase_tidak_baku, 1)

    # Top 5 kata tidak baku paling sering muncul
    top_kata_tidak_baku = [
        {"kata": k, "frekuensi": v, "saran": saran_perbaikan.get(k, "-")}
        for k, v in frekuensi_tidak_baku.most_common(5)
    ]

    # Klasifikasi
    if skor_baku >= 80:
        status, label, warna = "baku", "BAHASA BAKU", "success"
        pesan = "Teks ini menggunakan bahasa Indonesia yang baku dan sesuai standar."
    elif skor_baku >= 60:
        status, label, warna = "campuran", "CAMPURAN", "warning"
        pesan = "Teks ini mengandung beberapa kata tidak baku. Perlu perbaikan untuk konteks formal."
    else:
        status, label, warna = "tidak_baku", "BAHASA TIDAK BAKU", "danger"
        pesan = "Teks ini banyak menggunakan kata tidak baku. Tidak disarankan untuk komunikasi formal."

    # Buat highlighted text
    highlighted = build_highlighted_text(teks, set(kata_tidak_baku_unik), saran_perbaikan)

    return {
        "status": status,
        "label": label,
        "pesan": pesan,
        "warna": warna,
        "skor_baku": skor_baku,
        "persentase_tidak_baku": round(persentase_tidak_baku, 1),
        "total_kata": total_kata,
        "jumlah_tidak_baku": kata_tidak_baku_count,
        "kata_tidak_baku": kata_tidak_baku_unik,
        "saran_perbaikan": saran_perbaikan,
        "temuan_pola": temuan_pola,
        "top_kata_tidak_baku": top_kata_tidak_baku,
        "highlighted_text": highlighted,
        "teks_asli": teks,
        "total_entri_kamus": len(KAMUS_TIDAK_BAKU),
    }


# ============================================================
# BAGIAN 4: ROUTES FLASK
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/deteksi", methods=["POST"])
def deteksi():
    """Endpoint deteksi dari input teks manual."""
    data = request.get_json()
    if not data or "teks" not in data:
        return jsonify({"error": "Data tidak valid"}), 400
    hasil = deteksi_bahasa(data["teks"])
    return jsonify(hasil)


@app.route("/upload", methods=["POST"])
def upload():
    """Endpoint untuk upload dan analisis dokumen (PDF, DOCX, TXT)."""
    if "file" not in request.files:
        return jsonify({"error": "Tidak ada file yang diunggah"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nama file kosong"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Format file tidak didukung. Gunakan PDF, DOCX, atau TXT"}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        teks = None
        if ext == "txt":
            teks = extract_text_from_txt(filepath)
        elif ext == "pdf":
            teks = extract_text_from_pdf(filepath)
            if teks is None:
                return jsonify({"error": "Library PDF tidak tersedia. Install: pip install PyMuPDF"}), 500
        elif ext == "docx":
            teks = extract_text_from_docx(filepath)
            if teks is None:
                return jsonify({"error": "Library DOCX tidak tersedia. Install: pip install python-docx"}), 500

        if not teks or not teks.strip():
            return jsonify({"error": "File tidak mengandung teks yang dapat dibaca"}), 400

        hasil = deteksi_bahasa(teks)
        hasil["nama_file"] = filename
        hasil["ukuran_teks"] = len(teks)
        return jsonify(hasil)

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    print("=" * 60)
    print("  Bahasa Baku Detector v2.1")
    print(f"  Kamus: {len(KAMUS_TIDAK_BAKU)} entri kata tidak baku")
    print("  Buka browser: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True)