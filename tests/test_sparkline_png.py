import base64
import os
import sys

from PIL import Image

# Add project root and engine to path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root)
sys.path.append(os.path.join(root, "engine"))

from engine.email_market_synopsis import SovereignIntelligenceEngine


def test_png_sparkline_generation():
    print("[TEST] Initializing SIE...")
    sie = SovereignIntelligenceEngine()

    # Mock data: Simple uptrend
    points = [10, 12, 11, 14, 13, 16, 15, 18, 17, 20]
    color = "#00FF00"  # Green

    print(f"[TEST] Generating PNG sparkline for {len(points)} points...")
    img_tag = sie.generate_sparkline_svg(points, color, width=60, height=18)

    if not img_tag:
        print("[FAIL] Sparkline generation returned None")
        return False

    print(f"[TEST] Tag generated: {img_tag[:100]}...")

    # Verify it is an <img> tag with base64 PNG
    if '<img src="data:image/png;base64,' not in img_tag:
        print("[FAIL] Tag is not a base64 PNG img")
        return False

    # Extract base64 and verify it opens as an image
    try:
        b64_data = img_tag.split("base64,")[1].split('"')[0]
        img_data = base64.b64decode(b64_data)

        # Write to temp file for manual inspection if needed
        tmp_path = "tests/last_spark_test.png"
        with open(tmp_path, "wb") as f:
            f.write(img_data)

        with Image.open(tmp_path) as img:
            print(f"[SUCCESS] Valid PNG generated: {img.size} {img.format}")

            # Verify dimensions (should be width x height)
            if img.size != (60, 18):
                print(f"[FAIL] Unexpected dimensions: {img.size} vs (60, 18)")
                return False

        os.remove(tmp_path)
        return True
    except Exception as e:
        print(f"[FAIL] Image validation errored: {e}")
        return False


if __name__ == "__main__":
    success = test_png_sparkline_generation()
    sys.exit(0 if success else 1)
