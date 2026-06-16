from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


def get_version_family(version):
    """
    Converts a version like 4.13.0 into OpenCV 4.x.
    """
    version = str(version)
    major = version.split(".")[0]
    return f"OpenCV {major}.x"


def load_benchmark_files():
    """
    Loads all OpenCV benchmark result CSV files from the results folder.
    Example:
    - opencv4_benchmark_results.csv
    - opencv5_benchmark_results.csv
    """
    benchmark_files = sorted(RESULTS_DIR.glob("opencv*_benchmark_results.csv"))

    if not benchmark_files:
        print("No benchmark result files found.")
        print("Run: python scripts/run_benchmark.py")
        return pd.DataFrame()

    all_results = []

    for file in benchmark_files:
        df = pd.read_csv(file)

        required_columns = {"opencv_version", "operation", "runs", "avg_time_ms"}
        if not required_columns.issubset(df.columns):
            print(f"Skipping invalid file: {file}")
            continue

        df["source_file"] = file.name
        df["version_family"] = df["opencv_version"].apply(get_version_family)
        all_results.append(df)

    if not all_results:
        return pd.DataFrame()

    return pd.concat(all_results, ignore_index=True)


def save_combined_results(df):
    output_path = RESULTS_DIR / "combined_benchmark_results.csv"
    df.to_csv(output_path, index=False)
    print(f"Combined benchmark results saved to: {output_path}")


def create_comparison_chart(df):
    chart_path = RESULTS_DIR / "benchmark_comparison_chart.png"

    pivot_df = df.pivot_table(
        index="operation",
        columns="version_family",
        values="avg_time_ms",
        aggfunc="mean"
    )

    ax = pivot_df.plot(kind="bar", figsize=(12, 6))

    ax.set_title("OpenCV Version Benchmark Comparison")
    ax.set_xlabel("Computer Vision Operation")
    ax.set_ylabel("Average Time in Milliseconds")
    ax.tick_params(axis="x", rotation=35)

    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    print(f"Benchmark comparison chart saved to: {chart_path}")


def create_version_status(df):
    status_data = []

    available_versions = sorted(df["version_family"].unique())

    status_data.append({
        "item": "Current benchmark versions available",
        "status": ", ".join(available_versions)
    })

    if "OpenCV 5.x" not in available_versions:
        status_data.append({
            "item": "OpenCV 5.x benchmark",
            "status": "Pending - run again when OpenCV 5 Python support is available in this environment"
        })
    else:
        status_data.append({
            "item": "OpenCV 5.x benchmark",
            "status": "Completed"
        })

    status_df = pd.DataFrame(status_data)
    status_path = RESULTS_DIR / "version_status.csv"
    status_df.to_csv(status_path, index=False)

    print(f"Version status saved to: {status_path}")


def main():
    print("OpenCV VersionLens Comparison")
    df = load_benchmark_files()

    if df.empty:
        return

    save_combined_results(df)
    create_comparison_chart(df)
    create_version_status(df)

    print("\nComparison summary:")
    print(df[["version_family", "operation", "avg_time_ms"]])


if __name__ == "__main__":
    main()