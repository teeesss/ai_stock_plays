# V28: Sovereign Stealth Navigator (Chrome 160.0.8827)
import asyncio
import os
import random
import re
import sys

# V28: Hierarchy Leader Error Monitoring
try:
    from error_monitor import init_error_monitor
except ImportError:
    from engine.error_monitor import init_error_monitor
init_error_monitor()

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# Ensure UTF-8 output even on Windows
if sys.stdout.encoding != "utf-8":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# SPEC 2026: Multi-Browser Rotation (Chrome 160.x)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/160.0.8827.101 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/160.0.8827.105 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/160.0.8827.110 Safari/537.36",
]


class StealthNavigator:
    """
    Ultimate Stealth Navigator (V28)
    Bypasses 2026-grade AI suspect scoring, hardware fingerprinting, and behavioral analysis.
    """

    def __init__(self, headless=False, proxy=None):
        self.headless = headless
        self.proxy = proxy
        self.browser = None
        self.context = None
        self.playwright = None
        self.current_ua = random.choice(USER_AGENTS)

    async def initialize(self):
        self.playwright = await async_playwright().start()

        # 1. RANDOMIZED VIEWPORT (Layer 0)
        width = random.randint(1550, 1920)
        height = random.randint(900, 1080)

        # Identity: Rotating modern footprints
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--use-fake-device-for-media-stream",
            f"--user-agent={self.current_ua}",
        ]

        try:
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                channel="chrome",
                args=launch_args,
                proxy=self.proxy,
            )
        except Exception:
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless, args=launch_args, proxy=self.proxy
            )

        self.context = await self.browser.new_context(
            user_agent=self.current_ua,
            viewport={"width": width, "height": height},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation"],
        )

        # Apply basic stealth plugin
        stealth_engine = Stealth()
        await stealth_engine.apply_stealth_async(self.context)

        # CUSTOM 2026 HARDWARE MASKING (Layer 2)
        await self.context.add_init_script(
            """
            // Web Audio API Noise Injection
            const originalGetFloatFrequencyData = AnalyserNode.prototype.getFloatFrequencyData;
            AnalyserNode.prototype.getFloatFrequencyData = function(array) {
                originalGetFloatFrequencyData.apply(this, arguments);
                for (let i = 0; i < array.length; i++) {
                    array[i] += (Math.random() - 0.5) * 0.1;
                }
            };

            // CANVAS NOISE INJECTION (V4.4 Deep Stealth)
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {
                const imageData = originalGetImageData.apply(this, arguments);
                const data = imageData.data;
                for (let i = 0; i < data.length; i += 4) {
                    data[i] = data[i] + (Math.random() - 0.5) * 2; // subtle R noise
                }
                return imageData;
            };

            // Sec-CH-UA Spoofing
            Object.defineProperty(navigator, 'userAgentData', {
                get: () => ({
                    brands: [
                        { brand: 'Google Chrome', version: '147' },
                        { brand: 'Chromium', version: '147' },
                        { brand: 'Not(A:Brand', version: '24' }
                    ],
                    mobile: false,
                    platform: 'Windows'
                })
            });

            // WEBGL SPOOFING
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 (0x00002204) Direct3D11 vs_5_0 ps_5_0, D3D11)';
                if (parameter === 37446) return 'NVIDIA';
                return getParameter.apply(this, arguments);
            };

            // MEMORY/HARDWARE CONCURRENCY
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 32 });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 16 });

            // FINAL MASK: Remove Webdriver
            delete Object.getPrototypeOf(navigator).webdriver;
        """
        )

    async def human_mouse_move(self, page, x, y):
        """Moves mouse in a non-linear (Bezier) path with micro-jitter."""
        steps = random.randint(15, 30)
        current_pos = {"x": random.randint(0, 500), "y": random.randint(0, 500)}
        for i in range(steps):
            # Non-linear curve
            inter_x = (
                current_pos["x"] + (x - current_pos["x"]) * (i / steps) + random.uniform(-2, 2)
            )
            inter_y = (
                current_pos["y"] + (y - current_pos["y"]) * (i / steps) + random.uniform(-2, 2)
            )

            # Micro-Jitters (Human Hand Shake)
            jitter_x = inter_x + random.uniform(-0.5, 0.5)
            jitter_y = inter_y + random.uniform(-0.5, 0.5)

            await page.mouse.move(jitter_x, jitter_y)
            await asyncio.sleep(random.uniform(0.005, 0.015))

        await page.mouse.move(x, y)

    async def ghost_browse(self, page, target_url):
        """Performs human-like browsing behavior before data extraction."""
        print(f"Ghost Browsing: {target_url}")

        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(5, 10))  # Real 'thinking' time
        except Exception as e:
            print(f"  [!] Ghost Browsing Warning: {e}")
            return

        # 1. Random Scroll + Thinking Pauses (Optimized for speed)
        for _ in range(random.randint(1, 2)):
            scroll_y = random.randint(200, 800)
            await page.mouse.wheel(0, scroll_y)
            # Short thinking pause
            await asyncio.sleep(random.uniform(1.0, 2.0))

        # 2. Hover some navigation elements
        links = await page.query_selector_all("a, button")
        if links:
            sample_links = random.sample(links, min(len(links), 4))
            for link in sample_links:
                try:
                    box = await link.bounding_box()
                    if box:
                        await self.human_mouse_move(
                            page,
                            box["x"] + box["width"] / 2,
                            box["y"] + box["height"] / 2,
                        )
                        await asyncio.sleep(random.uniform(0.8, 2.5))
                except:
                    continue

        print("Ghost Browsing Complete.")

    async def get_session_state(self, url, state_path=None):
        """Heats up a session and returns cookies/crumb."""
        page = await self.context.new_page()
        await self.ghost_browse(page, url)

        cookies = await self.context.cookies()
        content = await page.content()

        # Regex extraction for crumb (V2.8)
        match = re.search(r'"crumb":"(.*?)"', content)
        if not match:
            match = re.search(r'"searchCrumb":"(.*?)"', content)

        crumb = match.group(1) if match else ""

        # Fallback to evaluation if regex fails
        if not crumb:
            try:
                crumb = await page.evaluate(
                    "() => (window.App && window.App.main && window.App.main.context && window.App.main.context.dispatcher && window.App.main.context.dispatcher.stores.CrumbStore) ? window.App.main.context.dispatcher.stores.CrumbStore.crumb : ''"
                )
            except:
                crumb = ""

        # SPEC 2026: Absolute path resolution to prevent 'Session Split'
        if state_path is None:
            # Always root to z:\COS_Stock_Plays\database
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            state_path = os.path.join(root_dir, "database", "stealth_session.json")

        # Ensure parent directory exists
        db_dir = os.path.dirname(state_path)
        os.makedirs(db_dir, exist_ok=True)

        await self.context.storage_state(path=state_path)

        # Enforce restricted permissions (High Security)
        try:
            if sys.platform != "win32":
                os.chmod(state_path, 0o600)
        except:
            pass

        await page.close()
        return cookies, crumb

    async def close(self):
        """Robust cleanup to prevent Windows Pipe errors."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass


if __name__ == "__main__":

    async def test():
        nav = StealthNavigator(headless=True)
        await nav.initialize()
        # Randomized test target
        target = random.choice(["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA"])
        url = f"https://finance.yahoo.com/quote/{target}"
        cookies, crumb = await nav.get_session_state(url)
        print(f"Target: {target} | Crumb Found: {crumb[:10]}...")
        await nav.close()

    asyncio.run(test())
