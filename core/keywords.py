"""
Kategori & keyword. Nama kategori HARUS cocok (contains match, case-insensitive)
dengan nama topic di grup WTB!, supaya topic-matcher bisa nemuin topic_id-nya
otomatis tanpa perlu hardcode ID.

Urutan kategori menentukan prioritas kalau satu menfess match lebih dari satu
kategori (kategori pertama yang match yang dipakai).
"""

CATEGORIES = {
    "Joki Tugas Umum": [
        "joktug", "joki tugas", "bimbel", "tugas kuliah", "joki quiz", "joki ujian",
        "joki uas", "joki uts", "rangkuman", "ringkasan materi", "joki absen",
        "joki kelas online", "joki praktikum", "resume jurnal", "tugas akhir", "ta",
        "kkn", "laporan kkn", "laporan magang", "joki magang", "joki hafalan",
        "joki presentasi", "resume buku", "joki resume", "tuton",
    ],
    "Karya Tulis Ilmiah": [
        "makalah", "essai", "essay", "artikel", "laporan", "joki artikel",
        "joki laporan", "proposal", "joki proposal", "skripsi", "joki skripsi",
        "revisi skripsi", "bab 1-5", "bab 1", "bab 2", "bab 3", "bab 4", "bab 5",
        "sidang skripsi", "laprak", "laporan praktikum", "studi kasus",
        "literature review", "review jurnal", "cari jurnal", "pkm",
        "jurnal internasional", "tesis", "disertasi", "revisi tesis", "kuisioner",
        "kuesioner", "survey", "pengolahan data skripsi", "jurnal sinta",
        "artikel ilmiah", "outline skripsi", "judul skripsi",
        "metodologi penelitian", "bab pembahasan", "jurnal scopus", "abstrak",
        "latar belakang", "laporan pkl", "pkl", "laporan pkm",
    ],
    "Penulisan Kreatif": [
        "cerpen", "puisi", "naskah drama", "ebook", "novel", "skenario",
        "lirik lagu", "caption", "copywriting", "cerita pendek", "flash fiction",
        "monolog", "storytelling",
    ],
    "Jasa Ketik & Rulis": [
        "jasa ketik", "jastik", "jasa tulis", "jastul", "resume", "resume materi",
        "transkrip", "transkrip wawancara", "translate", "terjemahan",
        "jasa ketik cepat", "ketik ulang", "input data", "entry data",
        "ketik dokumen", "salin tulisan", "tulis ulang",
    ],
    "Formatting": [
        "formatting", "revisi makalah", "revisi proposal", "daftar isi",
        "daftar pustaka", "nomor halaman", "no halaman", "parafrase", "turnitin",
        "ai detector", "mendeley", "cek plagiarisme", "similarity",
        "convert pdf ke word", "convert word ke pdf", "layout",
        "rapihin dokumen", "edit margin", "spasi", "kutipan", "sitasi",
        "citation", "referensi", "bibliography", "cek similarity", "cek turnitin",
        "styling word", "template skripsi", "template proposal",
    ],
    "Coding & Teknologi": [
        "joki coding", "coding", "ngoding", "website", "apk", "bug fixing",
        "database", "app android", "aplikasi", "joki web", "landing page",
        "joki app", "joki program", "program python", "program java",
        "program c++", "sistem informasi", "si", "joki si", "machine learning",
        "joki ml", "joki database", "joki excel vba", "bug", "debug",
        "error coding", "joki tugas coding", "script python", "aplikasi skripsi",
        "sistem pakar", "joki uas coding", "framework laravel",
        "framework react", "joki html css",
    ],
    "Data & Sains": [
        "spss", "olah data", "kimia", "biologi", "fisika", "akuntansi",
        "matematika", "statistik", "olah data excel", "minitab", "ekonometrika",
        "joki matkul", "r studio", "spss anova", "uji spss", "uji validitas",
        "uji reliabilitas", "regresi", "sample data", "uji normalitas", "uji t",
        "path analysis", "sem", "amos", "lisrel", "joki tugas statistik",
    ],
    "Editing": [
        "infografis", "poster", "banner", "mindmap", "mind mapping", "famplet",
        "logo", "logo kelas", "logo 2d", "logo 3d", "jasa edit", "edit logo",
        "ui/ux", "edit video", "edit vid", "video animasi", "animasi ai",
        "edit feeds ig", "cover buku", "cover proposal", "presentasi", "ppt",
        "sertifikat", "undangan", "thumbnail", "desain grafis", "canva",
        "feeds instagram", "konten ig", "konten sosmed", "id card", "x banner",
        "roll banner", "brosur", "kartu nama", "mockup", "vector", "edit foto",
        "retouch foto", "motion graphic", "intro video", "reels editing",
        "tiktok editing", "desain feed", "konten canva", "template canva",
        "video promosi", "video profile", "wedding invitation",
        "undangan digital",
    ],
    "CV & Organisasi": [
        "cv ats", "cv kreatif", "visi misi", "organisasi", "portofolio",
        "cover letter", "surat lamaran", "ad/art organisasi",
    ],
}


def match_category(text: str):
    """Return (category_name, matched_keyword) for the first category that
    matches, or (None, None) if nothing matches."""
    low = text.lower()
    for category, words in CATEGORIES.items():
        for kw in words:
            if kw in low:
                return category, kw
    return None, None


def all_keywords_flat():
    seen, out = set(), []
    for words in CATEGORIES.values():
        for kw in words:
            if kw not in seen:
                seen.add(kw)
                out.append(kw)
    return out
