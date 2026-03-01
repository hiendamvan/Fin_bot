import matplotlib.pyplot as plt
import os

def plot_signals(df, output_dir, stock_name):  
    # Đảm bảo thư mục output tồn tại
    os.makedirs(output_dir, exist_ok=True)
    
    # ===== VẼ BIỂU ĐỒ =====
    plt.figure(figsize=(16, 8)) # Phóng to biểu đồ một chút để dễ nhìn chữ

    # Giá đóng cửa & MA50
    plt.plot(df["time"], df["close"], label="Close Price", color='royalblue', alpha=0.7)
    plt.plot(df["time"], df["MA50"], label="MA50", color='darkorange', alpha=0.9)

    # Lọc tín hiệu
    buy_signals = df[df["Signal"] == 1]
    sell_signals = df[df["Signal"] == -1]

    # VẼ MUA VÀ IN ĐIỂM SỐ
    plt.scatter(buy_signals["time"], buy_signals["close"], 
                marker="^", color='green', s=150, label="Buy", zorder=5)
    
    for _, row in buy_signals.iterrows():
        plt.annotate(f"Score: {int(row['Score'])}", 
                     (row["time"], row["close"]),
                     textcoords="offset points", 
                     xytext=(0, 10), # Dịch chữ lên trên mũi tên 10 pixel
                     ha='center', 
                     color='green', 
                     fontsize=10, 
                     fontweight='bold')

    # VẼ BÁN VÀ IN ĐIỂM SỐ
    plt.scatter(sell_signals["time"], sell_signals["close"], 
                marker="v", color='red', s=150, label="Sell", zorder=5)
    
    for _, row in sell_signals.iterrows():
        plt.annotate(f"Score: {int(row['Score'])}", 
                     (row["time"], row["close"]),
                     textcoords="offset points", 
                     xytext=(0, -15), # Dịch chữ xuống dưới mũi tên 15 pixel
                     ha='center', 
                     color='red', 
                     fontsize=10, 
                     fontweight='bold')

    # Xử lý các tín hiệu khác (nếu có, ví dụ Signal == 2)
    add_signals = df[df["Signal"] == 2]
    if not add_signals.empty:
        plt.scatter(add_signals["time"], add_signals["close"], 
                    marker="o", color='purple', s=80, label="Add Position", zorder=5)

    # Format biểu đồ
    plt.title(f"{stock_name} - Trading Signals & Condition Scores", fontsize=14, fontweight='bold')
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    # Xoay nhãn trục X nếu ngày tháng bị đè lên nhau
    plt.xticks(rotation=45)

    # ===== SAVE IMAGE ====
    plt.tight_layout()
    file_path = f"{output_dir}/{stock_name}_MA50_signals.png"
    plt.savefig(file_path, dpi=300)
    plt.close()

    print(f"✅ Đã lưu biểu đồ kèm điểm số vào: {file_path}")