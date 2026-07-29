DEMO_CATEGORIES = [
    ("概念钻孔系列", "demo-drilling", "drill.webp"),
    ("概念冲击系列", "demo-impact", "rotary-hammer.webp"),
    ("概念切割系列", "demo-cutting", "cut-off-saw.webp"),
    ("概念打磨系列", "demo-grinding", "angle-grinder.webp"),
]

DEMO_PRODUCTS = [
    ("demo-drilling", "概念无刷电钻", "DEMO-DR101", [("额定功率", "600W"), ("空载转速", "0-1800rpm"), ("夹头规格", "13mm"), ("重量", "1.5kg")]),
    ("demo-drilling", "概念冲击钻", "DEMO-DR201", [("额定功率", "850W"), ("空载转速", "0-3000rpm"), ("冲击频率", "48000bpm"), ("重量", "1.9kg")]),
    ("demo-drilling", "概念工业钻", "DEMO-DR301", [("额定功率", "1100W"), ("空载转速", "0-1200rpm"), ("夹头规格", "16mm"), ("重量", "3.2kg")]),
    ("demo-impact", "概念轻型电锤", "DEMO-IH101", [("额定功率", "800W"), ("冲击能量", "2.8J"), ("冲击频率", "4200bpm"), ("重量", "3.1kg")]),
    ("demo-impact", "概念专业电锤", "DEMO-IH201", [("额定功率", "1100W"), ("冲击能量", "5.2J"), ("冲击频率", "3500bpm"), ("重量", "5.6kg")]),
    ("demo-impact", "概念破拆电镐", "DEMO-IH301", [("额定功率", "1500W"), ("冲击能量", "12J"), ("冲击频率", "1900bpm"), ("重量", "11.8kg")]),
    ("demo-cutting", "概念手持圆锯", "DEMO-CT101", [("额定功率", "1400W"), ("空载转速", "5200rpm"), ("锯片规格", "185mm"), ("重量", "4.2kg")]),
    ("demo-cutting", "概念型材切割机", "DEMO-CT201", [("额定功率", "2200W"), ("空载转速", "3800rpm"), ("锯片规格", "355mm"), ("重量", "18kg")]),
    ("demo-cutting", "概念精密斜切锯", "DEMO-CT301", [("额定功率", "1800W"), ("空载转速", "4500rpm"), ("锯片规格", "305mm"), ("重量", "16kg")]),
    ("demo-grinding", "概念迷你角磨机", "DEMO-GR101", [("额定功率", "750W"), ("空载转速", "11000rpm"), ("砂轮规格", "100mm"), ("重量", "1.6kg")]),
    ("demo-grinding", "概念专业角磨机", "DEMO-GR201", [("额定功率", "1200W"), ("空载转速", "10000rpm"), ("砂轮规格", "125mm"), ("重量", "2.2kg")]),
    ("demo-grinding", "概念工业打磨机", "DEMO-GR301", [("额定功率", "2000W"), ("空载转速", "6500rpm"), ("砂轮规格", "230mm"), ("重量", "5.3kg")]),
]

STANDARD_PARAMETERS = [
    ("额定功率", "rated-power", "Rated power", "W", ["功率"]),
    ("空载转速", "no-load-speed", "No-load speed", "rpm", ["转速"]),
    ("冲击频率", "impact-rate", "Impact rate", "bpm", ["冲击率"]),
    ("冲击能量", "impact-energy", "Impact energy", "J", ["冲击能"]),
    ("重量", "weight", "Weight", "kg", []),
    ("夹头规格", "chuck-size", "Chuck size", "mm", ["夹头"]),
    ("锯片规格", "blade-size", "Blade size", "mm", ["锯片"]),
    ("砂轮规格", "disc-size", "Disc size", "mm", ["砂轮"]),
]
