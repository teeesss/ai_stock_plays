/**
 * Regression Test: MCap Formatting Logic
 * Ensures trillions, billions, and millions are formatted per user specs
 * and do not exceed space constraints.
 */

function formatMCap(b) {
    if (!b || b <= 0) return '--';
    let res = '';
    if (b >= 1000) {
        const t = b / 1000;
        res = (t < 10 ? t.toFixed(2) : t.toFixed(1)).replace('.00','').replace('.0','') + 'T';
    } else if (b >= 1) {
        res = b.toFixed(1).replace('.0','') + 'B';
    } else {
        const m = b * 1000;
        res = m.toFixed(1).replace('.0','') + 'M';
    }
    return res.length > 7 ? res.substring(0, 7) : res;
}

const testCases = [
    { in: 1210,   expected: "1.21T",  label: "Low Trillion (2 decimals)" },
    { in: 12100,  expected: "12.1T",  label: "High Trillion (1 decimal)" },
    { in: 22.5,   expected: "22.5B",  label: "Billion (decimal)" },
    { in: 243,    expected: "243B",   label: "Billion (whole)" },
    { in: 0.2544, expected: "254.4M", label: "Million (decimal)" },
    { in: 0.243,  expected: "243M",   label: "Million (whole)" },
    { in: 9999.9, expected: "10T",    label: "Rounding boundary" }
];

let failures = 0;
console.log("Running MCap Formatting Regression tests...");

testCases.forEach(tc => {
    const actual = formatMCap(tc.in);
    if (actual === tc.expected) {
        console.log(`[PASS] ${tc.label.padEnd(30)} | Out: ${actual.padStart(7)}`);
    } else {
        console.log(`[FAIL] ${tc.label.padEnd(30)} | Expected: ${tc.expected} | Actual: ${actual}`);
        failures++;
    }
    
    // Check 7 char limit strictly
    if (actual.length > 7) {
        console.log(`[FAIL] ${tc.label} EXCEEDS 7 CHARS: ${actual}`);
        failures++;
    }
});

if (failures === 0) {
    console.log("\nAll MCap tests passed! Data integrity preserved.");
    process.exit(0);
} else {
    console.log(`\nTests failed with ${failures} errors.`);
    process.exit(1);
}
