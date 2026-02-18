from vnstock import Quote 
from utils import generate_full_strategy
import matplotlib.pyplot as plt
quote = Quote(symbol='PVD', source='VCI')

# Hoặc lấy theo khoảng thời gian cụ thể
df = quote.history(start='2025-01-01', end='2026-02-20', interval="1D")

df = generate_full_strategy(df)

# ===== VẼ BIỂU ĐỒ =====
plt.figure(figsize=(14,7))

# Giá đóng cửa
plt.plot(df["time"], df["close"], label="Close Price")

# MA50
plt.plot(df["time"], df["MA50"], label="MA50")

add_signals = df[df["Signal"] == 2]

plt.scatter(add_signals["time"],
            add_signals["close"],
            marker="o",
            s=80)

# BUY
buy_signals = df[df["Signal"] == 1]
plt.scatter(buy_signals["time"],
            buy_signals["close"],
            marker="^",
            s=120)

# SELL
sell_signals = df[df["Signal"] == -1]
plt.scatter(sell_signals["time"],
            sell_signals["close"],
            marker="v",
            s=120)

plt.title("PVD - MA50 Trading Signals")
plt.xlabel("Time")
plt.ylabel("Price")
plt.legend()
plt.grid()

# ===== SAVE IMAGE =====
plt.tight_layout()
plt.savefig("PVD_MA50_signals.png", dpi=300)
plt.close()

print("Đã lưu biểu đồ vào file PVD_MA50_signals.png")