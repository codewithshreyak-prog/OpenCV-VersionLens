from pathlib import Path
import pandas as pd
import streamlit as st


RESULTS_DIR = Path("results")


st.set_page_config(
    page_title="OpenCV VersionLens",
    layout="wide"
)


st.title("OpenCV VersionLens")
st.subheader("OpenCV 4.x vs OpenCV 5.x Benchmark Comparison")

st.write(
    "This dashboard compares OpenCV versions across common computer vision operations "
    "such as grayscale conversion, Gaussian blur, Canny edge detection, resizing, "
    "thresholding, and contour detection."
)


combined_file = RESULTS_DIR / "combined_benchmark_results.csv"
chart_file = RESULTS_DIR / "benchmark_comparison_chart.png"
status_file = RESULTS_DIR / "version_status.csv"


if not combined_file.exists():
    st.warning("No combined benchmark file found.")
    st.code("Run: python scripts/compare_versions.py")
else:
    df = pd.read_csv(combined_file)

    st.header("Benchmark Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Operations Tested", df["operation"].nunique())

    with col2:
        st.metric("OpenCV Versions Found", df["version_family"].nunique())

    with col3:
        st.metric("Total Benchmark Runs", int(df["runs"].sum()))

    st.dataframe(df, use_container_width=True)

    st.header("Performance Comparison Chart")

    if chart_file.exists():
        st.image(str(chart_file), caption="Average processing time by OpenCV version")
    else:
        st.warning("Chart not found. Run compare_versions.py again.")

    st.header("Average Time by Operation")

    pivot_df = df.pivot_table(
        index="operation",
        columns="version_family",
        values="avg_time_ms",
        aggfunc="mean"
    )

    st.bar_chart(pivot_df)

    st.header("Version Status")

    if status_file.exists():
        status_df = pd.read_csv(status_file)
        st.dataframe(status_df, use_container_width=True)
    else:
        st.info("Version status file not found.")

    st.header("Preview Outputs")

    preview_cols = st.columns(3)

    preview_images = [
        ("Grayscale Output", RESULTS_DIR / "preview_grayscale.png"),
        ("Canny Edge Output", RESULTS_DIR / "preview_edges.png"),
        ("Gaussian Blur Output", RESULTS_DIR / "preview_blur.png"),
    ]

    for col, (title, image_path) in zip(preview_cols, preview_images):
        with col:
            st.write(title)
            if image_path.exists():
                st.image(str(image_path))
            else:
                st.warning("Image not found.")