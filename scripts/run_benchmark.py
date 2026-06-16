import cv2
import numpy as np
import pandas as pd
import time
from pathlib import Path


DATA_DIR = Path("data")
RESULTS_DIR = Path("results")

DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)


def create_sample_image():
    """
    Creates a synthetic image so the benchmark can run without downloading data.
    """
    image = np.zeros((480, 640, 3), dtype=np.uint8)

    cv2.rectangle(image, (80, 80), (250, 300), (255, 255, 255), -1)
    cv2.circle(image, (430, 220), 90, (180, 180, 180), -1)
    cv2.line(image, (50, 420), (590, 420), (255, 255, 255), 5)
    cv2.putText(
        image,
        "OpenCV VersionLens",
        (70, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2,
    )

    sample_path = DATA_DIR / "sample_image.png"
    cv2.imwrite(str(sample_path), image)
    return image


def benchmark_operation(operation_name, operation_func, image, runs=50):
    """
    Runs one OpenCV operation multiple times and returns average time in ms.
    """
    start = time.perf_counter()

    for _ in range(runs):
        operation_func(image)

    end = time.perf_counter()
    avg_time_ms = ((end - start) / runs) * 1000

    return {
        "opencv_version": cv2.__version__,
        "operation": operation_name,
        "runs": runs,
        "avg_time_ms": round(avg_time_ms, 4),
    }


def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def gaussian_blur(image):
    return cv2.GaussianBlur(image, (7, 7), 0)


def canny_edges(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(gray, 100, 200)


def resize_image(image):
    return cv2.resize(image, (320, 240))


def threshold_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return thresh


def contour_detection(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def save_preview_outputs(image):
    """
    Saves output images so README/dashboard can use screenshots later.
    """
    gray = grayscale(image)
    edges = canny_edges(image)
    blur = gaussian_blur(image)

    cv2.imwrite(str(RESULTS_DIR / "preview_grayscale.png"), gray)
    cv2.imwrite(str(RESULTS_DIR / "preview_edges.png"), edges)
    cv2.imwrite(str(RESULTS_DIR / "preview_blur.png"), blur)


def main():
    print("OpenCV VersionLens Benchmark")
    print(f"Running OpenCV version: {cv2.__version__}")

    image = create_sample_image()
    save_preview_outputs(image)

    operations = [
        ("grayscale_conversion", grayscale),
        ("gaussian_blur", gaussian_blur),
        ("canny_edge_detection", canny_edges),
        ("image_resize", resize_image),
        ("binary_thresholding", threshold_image),
        ("contour_detection", contour_detection),
    ]

    results = []

    for operation_name, operation_func in operations:
        result = benchmark_operation(operation_name, operation_func, image)
        results.append(result)
        print(f"{operation_name}: {result['avg_time_ms']} ms")

    df = pd.DataFrame(results)

    version_major = cv2.__version__.split(".")[0]
    output_file = RESULTS_DIR / f"opencv{version_major}_benchmark_results.csv"

    df.to_csv(output_file, index=False)

    print(f"\nBenchmark results saved to: {output_file}")


if __name__ == "__main__":
    main()