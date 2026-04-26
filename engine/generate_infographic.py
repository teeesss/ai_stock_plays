import csv

from PIL import Image, ImageDraw, ImageFont


def generate_infographic_pillow(csv_path, output_path):
    # Colors (Matches Terminal Theme)
    BG_COLOR = (15, 23, 42)  # #0f172a
    CARD_COLOR = (30, 41, 59)  # #1e293b
    ACCENT = (56, 189, 248)  # #38bdf8
    GOLD = (251, 191, 36)  # #fbbf24
    TEXT_MAIN = (248, 250, 252)
    TEXT_DIM = (148, 163, 184)

    # Layers
    layers = [
        {
            "name": "SYSTEMS & HYPERSCALE",
            "color": (167, 139, 250),
            "keywords": ["etf", "system", "logic", "broadcom", "nvidia"],
        },
        {
            "name": "ASSEMBLY & PACKAGING",
            "color": (251, 191, 36),
            "keywords": [
                "bonding",
                "assembly",
                "aec",
                "cpo",
                "engine",
                "packaging",
                "interface",
                "metrology",
                "inspection",
            ],
        },
        {
            "name": "PHOTONICS & SILICON",
            "color": (244, 114, 182),
            "keywords": [
                "serdes",
                "modulator",
                "die",
                "foundry",
                "chip",
                "laser die",
                "perkinamine",
            ],
        },
        {
            "name": "MATERIALS & SUBSTRATES",
            "color": (56, 189, 248),
            "keywords": [
                "substrate",
                "inp",
                "glass",
                "ald",
                "chemical",
                "mbe",
                "tecs",
                "thermal",
                "wafer",
            ],
        },
    ]

    # Group data
    grouped_data = {layer["name"]: [] for layer in layers}
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            role = row["Role"].lower()
            bucket = row["Bucket"].lower()
            ticker = row["Ticker"]
            company = row["Company"]

            assigned = "SYSTEMS & HYPERSCALE"
            for layer in reversed(layers):
                if any(k in role for k in layer["keywords"]) or any(
                    k in bucket for k in layer["keywords"]
                ):
                    assigned = layer["name"]
                    break
            grouped_data[assigned].append(f"{ticker} ({company})")

    # Image setup
    WIDTH, HEIGHT = 1400, 1000
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to load a font
    try:
        font_title = ImageFont.truetype("arial.ttf", 40)
        font_layer = ImageFont.truetype("arial.ttf", 24)
        font_ticker = ImageFont.truetype("arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_layer = ImageFont.load_default()
        font_ticker = ImageFont.load_default()

    # Draw Title
    draw.text(
        (WIDTH // 2, 50),
        "CO-PACKAGED OPTICS (CPO) SUPPLY CHAIN MAP",
        fill=GOLD,
        font=font_title,
        anchor="mm",
    )
    draw.text(
        (WIDTH // 2, 90),
        "Layer-by-Layer Physical Bottlenecks & Hidden Alpha",
        fill=TEXT_DIM,
        font=font_ticker,
        anchor="mm",
    )

    # Draw Layers
    margin_x = 100
    layer_height = 180
    y_start = 150
    gap = 40

    for i, layer in enumerate(layers):
        y_pos = y_start + i * (layer_height + gap)
        # Layer Header
        draw.rectangle(
            [margin_x, y_pos, WIDTH - margin_x, y_pos + layer_height],
            fill=CARD_COLOR,
            outline=layer["color"],
            width=2,
        )
        draw.text((margin_x + 20, y_pos + 10), layer["name"], fill=layer["color"], font=font_layer)

        # Draw Tickers
        data = grouped_data[layer["name"]]
        x_off = margin_x + 30
        y_off = y_pos + 50
        col_width = 250
        for idx, item in enumerate(data):
            col = idx % 4
            row_idx = idx // 4
            if row_idx > 4:
                continue  # Cap display
            draw.text(
                (x_off + col * col_width, y_off + row_idx * 25),
                f"• {item}",
                fill=TEXT_MAIN,
                font=font_ticker,
            )

    # Save
    img.save(output_path)
    print(f"Infographic saved to {output_path}")


if __name__ == "__main__":
    generate_infographic_pillow("cpo_master_ultimate.csv", "infographs/cpo_supply_chain.png")
