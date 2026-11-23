"""Deteksi wajah bersama untuk prep.py dan autocap.py.

Memakai model YuNet bawaan (assets/vendor/models/face_yunet.onnx) lewat OpenCV.
Kalau OpenCV terlalu tua untuk YuNet, jatuh ke Haar cascade bawaan.
Kalau OpenCV tidak ada sama sekali, semua fungsi mengembalikan "tidak ada wajah"
dan pemanggilnya memakai posisi aman default. Tidak pernah membuat pekerjaan berhenti.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "vendor", "models")
os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover
    cv2 = None
    np = None

_det = {"kind": None, "obj": None, "size": None}


def available():
    return cv2 is not None


def _init(w, h):
    if cv2 is None:
        return None
    if _det["kind"] == "yunet":
        if _det["size"] != (w, h):
            _det["obj"].setInputSize((w, h)); _det["size"] = (w, h)
        return _det
    if _det["kind"] == "haar":
        return _det
    yp = os.path.join(MODELS, "face_yunet.onnx")
    if hasattr(cv2, "FaceDetectorYN") and os.path.exists(yp):
        try:
            _det.update(kind="yunet", obj=cv2.FaceDetectorYN.create(yp, "", (w, h), 0.6, 0.3, 5000), size=(w, h))
            return _det
        except Exception:
            pass
    hp = os.path.join(MODELS, "face_haar.xml")
    if not os.path.exists(hp) and hasattr(cv2, "data"):
        hp = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
    if os.path.exists(hp):
        _det.update(kind="haar", obj=cv2.CascadeClassifier(hp))
        return _det
    return None


def faces(img, max_w=640):
    """Kembalikan daftar wajah [(x, y, w, h, skor)] dalam koordinat gambar asli, terbesar dulu."""
    if cv2 is None or img is None:
        return []
    H, W = img.shape[:2]
    k = min(1.0, max_w / float(W))
    small = cv2.resize(img, (int(W * k), int(H * k))) if k < 1 else img
    sh, sw = small.shape[:2]
    d = _init(sw, sh)
    if d is None:
        return []
    out = []
    if d["kind"] == "yunet":
        _, res = d["obj"].detect(small)
        if res is not None:
            for r in res:
                x, y, w, h, s = float(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[-1])
                out.append((x / k, y / k, w / k, h / k, s))
    else:
        g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        for (x, y, w, h) in d["obj"].detectMultiScale(g, 1.1, 5, minSize=(int(sw * .06), int(sw * .06))):
            out.append((x / k, y / k, w / k, h / k, 0.8))
    out = [f for f in out if f[2] > W * 0.04]
    out.sort(key=lambda f: -f[2] * f[3])
    return out


def read_image(path):
    if cv2 is None:
        return None
    return cv2.imread(path)


def luminance(img, y0, y1, x0=0, x1=None):
    """Kecerahan rata-rata 0..1 pada pita gambar (dipakai untuk memilih alat kontras teks)."""
    if cv2 is None or img is None:
        return 0.3
    H, W = img.shape[:2]
    x1 = W if x1 is None else x1
    y0, y1 = max(0, int(y0)), min(H, int(y1))
    if y1 <= y0:
        return 0.3
    band = img[y0:y1, int(x0):int(x1)]
    g = cv2.cvtColor(band, cv2.COLOR_BGR2GRAY)
    # persentil 80: teks harus terbaca di bagian paling terang, bukan rata-rata
    return float(np.percentile(g, 80)) / 255.0
