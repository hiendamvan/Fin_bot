from vnstock import Quote 
from strategy import generate_full_strategy
import matplotlib.pyplot as plt
import pandas as pd

def professional_backtest(df, plot_equity=True):
    """
    Backtest chuyên nghiệp dựa trên cột:
    - close
    - Signal (1 = Buy, -1 = Sell)

    Trả về:
    - metrics dict
    - trades dataframe
    """

    df = df.copy()

    # =========================
    # 1️⃣ Lấy điểm vào / ra
    # =========================
    buys = df[df["Signal"] == 1][["time", "close"]].copy()
    sells = df[df["Signal"] == -1][["time", "close"]].copy()

    buys.reset_index(drop=True, inplace=True)
    sells.reset_index(drop=True, inplace=True)

    # Nếu buy nhiều hơn sell → dùng giá cuối
    if len(buys) > len(sells):
        last_row = df.iloc[-1]
        sells = pd.concat([
            sells,
            pd.DataFrame([{
                "time": last_row["time"],
                "close": last_row["close"]
            }])
        ], ignore_index=True)

    # Cắt cho bằng nhau
    n = min(len(buys), len(sells))
    buys = buys.iloc[:n]
    sells = sells.iloc[:n]

    # =========================
    # 2️⃣ Tính return từng trade
    # =========================
    trades = pd.DataFrame({
        "Buy Time": buys["time"],
        "Buy Price": buys["close"],
        "Sell Time": sells["time"],
        "Sell Price": sells["close"],
    })

    trades["Return"] = sells["close"].values / buys["close"].values
    trades["Return %"] = (trades["Return"] - 1) * 100

    # =========================
    # 3️⃣ Metrics
    # =========================
    total_return = trades["Return"].prod() - 1
    win_rate = (trades["Return"] > 1).mean()
    avg_return = trades["Return %"].mean()

    # Equity curve
    trades["Equity"] = trades["Return"].cumprod()

    # Max Drawdown
    rolling_max = trades["Equity"].cummax()
    drawdown = trades["Equity"] / rolling_max - 1
    max_drawdown = drawdown.min()

    # Buy & Hold
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
    # 4️⃣ Plot equity
    # =========================
    if plot_equity and len(trades) > 0:
        plt.figure(figsize=(12,6))
        plt.plot(trades["Sell Time"], trades["Equity"])
        plt.title("Equity Curve")
        plt.xlabel("Time")
        plt.ylabel("Equity (Compounded)")
        plt.grid()
        plt.tight_layout()
        plt.savefig("equity_curve.png", dpi=300)
        plt.close()
        print("Đã lưu equity_curve.png")

    return metrics, trades
