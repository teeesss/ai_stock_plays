import os


def sync_csv_to_js(csv_path, js_path):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    try:
        # We'll store the CSV as a raw string inside the JS file
        # to allow PapaParse to handle the existing parsing logic
        # while bypassing CORS.
        with open(csv_path, "r", encoding="utf-8") as f:
            csv_content = f.read()

        # Safely escape backticks and backslashes for JS template literal
        escaped_content = csv_content.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

        js_content = f"window.CPO_CSV_DATA = `{escaped_content}`;"

        with open(js_path, "w", encoding="utf-8") as f:
            f.write(js_content)

        print(f"Successfully synced {csv_path} to {js_path}")
    except Exception as e:
        print(f"Sync error: {e}")


if __name__ == "__main__":
    sync_csv_to_js("cpo_master_ultimate.csv", "research/dashboard_data.js")
