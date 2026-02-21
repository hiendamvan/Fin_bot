import os
import pandas as pd
from vnstock import Quote
from strategy import generate_strategy
from plot_chart import plot_signals
from test import professional_backtest


if __name__ == "__main__":

    stock_lists = ["MBB", "STB", "VCI", "SSI", "PVD", "BSR","OIL", "VGI", "VTP", "VNM", "VGC"]

    start_date = "2025-01-01"
    end_date = "2026-02-20"

    all_metrics = []

    # Tạo thư mục chung
    base_output_dir = "output"
    os.makedirs(base_output_dir, exist_ok=True)

    for stock_name in stock_lists:
        print(f"\n===== ĐANG BACKTEST {stock_name} =====")

        try:
            # ===== 1️⃣ Tạo thư mục riêng =====
            output_dir = os.path.join(base_output_dir, stock_name)
            os.makedirs(output_dir, exist_ok=True)

            # ===== 2️⃣ Lấy dữ liệu =====
            quote = Quote(symbol=stock_name, source='VCI')
            df = quote.history(start=start_date,
                               end=end_date,
                               interval="1D")

            if df is None or len(df) < 100:
                print(f"{stock_name}: Không đủ dữ liệu")
                continue

            # ===== 3️⃣ Strategy =====
            df = generate_strategy(df)

            # ===== 4️⃣ Plot =====
            plot_signals(df, output_dir, stock_name)

            # ===== 5️⃣ Backtest =====
            metrics, trades = professional_backtest(df, plot_equity=True)

            # ===== 6️⃣ Lưu trades =====
            trades.to_csv(
                os.path.join(output_dir,
                             f"{stock_name}_trades.csv"),
                index=False
            )

            # ===== 7️⃣ Gộp metrics =====
            metrics["Stock"] = stock_name
            all_metrics.append(metrics)

            print(f"{stock_name} DONE")

        except Exception as e:
            print(f"Lỗi với {stock_name}: {e}")

    # =========================
    # 8️⃣ Lưu metrics chung CSV
    # =========================
    if len(all_metrics) > 0:
        summary_df = pd.DataFrame(all_metrics)

        summary_df = summary_df.sort_values(
            by="Total Return %",
            ascending=False
        )

        summary_df.to_csv(
            os.path.join(base_output_dir,
                         "summary_backtest.csv"),
            index=False
        )

        print("\n===== BẢNG XẾP HẠNG =====")
        print(summary_df)

        print("\nĐã lưu file: output/summary_backtest.csv")

    else:
        print("Không có dữ liệu để tổng hợp.")