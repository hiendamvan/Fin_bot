import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def professional_backtest(df, plot_equity=True):
    """
    Backtest chuyên nghiệp, Buy-first, long-only.
    Nếu lệnh cuối cùng là Buy chưa khớp, tự động Sell tại ngày cuối cùng.
    
    Trả về: metrics dict + trades DataFrame
    """
    df = df.copy()
    trades_list = []

    position = 0  # 0 = không nắm giữ, 1 = đang nắm giữ
    equity_val = 1.0

    buy_price = 0
    buy_time = None

    for idx, row in df.iterrows():
        sig = row["Signal"]
        price = row["close"]
        time = row["time"]

        if sig == 1 and position == 0:
            # Mua
            buy_price = price
            buy_time = time
            position = 1

        elif sig == -1 and position == 1:
            # Bán
            sell_price = price
            sell_time = time
            ret = sell_price / buy_price
            equity_val *= ret

            trades_list.append({
                "Buy Time": buy_time,
                "Buy Price": buy_price,
                "Sell Time": sell_time,
                "Sell Price": sell_price,
                "Return": ret,
                "Return %": (ret - 1) * 100,
                "Equity": equity_val
            })
            position = 0

    # Nếu lệnh cuối cùng vẫn là Buy, sell tại ngày cuối cùng
    if position == 1:
        sell_price = df["close"].iloc[-1]
        sell_time = df["time"].iloc[-1]
        ret = sell_price / buy_price
        equity_val *= ret

        trades_list.append({
            "Buy Time": buy_time,
            "Buy Price": buy_price,
            "Sell Time": sell_time,
            "Sell Price": sell_price,
            "Return": ret,
            "Return %": (ret - 1) * 100,
            "Equity": equity_val
        })
        position = 0

    trades = pd.DataFrame(trades_list)

    # =========================
    # Metrics
    # =========================
    if len(trades) > 0:
        total_return = trades["Return"].prod() - 1
        win_rate = (trades["Return"] > 1).mean()
        avg_return = trades["Return %"].mean()
        max_drawdown = (trades["Equity"] / trades["Equity"].cummax() - 1).min()
    else:
        total_return = 0
        win_rate = 0
        avg_return = 0
        max_drawdown = 0

    buy_hold_return = df["close"].iloc[-1] / df["close"].iloc[0] - 1

    metrics = {
        "Total Return %": total_return * 100,
        "Buy & Hold %": buy_hold_return * 100,
        "Win Rate %": win_rate * 100,
        "Average Trade %": avg_return,
        "Max Drawdown %": max_drawdown * 100,
        "Number of Trades": len(trades)
    }

    # =========================
    # Plot equity
    # =========================
    if plot_equity and len(trades) > 0:
        plt.figure(figsize=(12,6))
        plt.plot(trades["Sell Time"], trades["Equity"], marker='o')
        plt.title("Equity Curve")
        plt.xlabel("Sell Time")
        plt.ylabel("Equity (Compounded)")
        plt.grid()
        plt.tight_layout()
        plt.savefig("equity_curve.png", dpi=300)
        plt.close()
        print("Đã lưu equity_curve.png")

    return metrics, trades