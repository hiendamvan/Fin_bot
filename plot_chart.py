import matplotlib.pyplot as plt

def plot_signals(df, output_dir, stock_name):  
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

    plt.title(f"{stock_name} - MA50 Trading Signals")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()

    # ===== SAVE IMAGE ====
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{stock_name}_MA50_signals.png", dpi=300)
    plt.close()

    print(f"Đã lưu biểu đồ vào file {output_dir}/{stock_name}_MA50_signals.png")
