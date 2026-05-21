#!/usr/bin/env python3
"""Generate Tim_Dime_Resume.pdf from the canonical content used on timdime.com."""

from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit


OUTPUT = Path(__file__).resolve().parent.parent / "Tim_Dime_Resume.pdf"

NAVY = HexColor("#0A1F44")
NAVY_DEEP = HexColor("#061328")
GOLD = HexColor("#C9A961")
INK = HexColor("#15233B")
INK_SOFT = HexColor("#475569")
MUTED = HexColor("#6B7280")
LINE = HexColor("#E4E7EC")
SIDEBAR_BG = HexColor("#F4F6FA")

PAGE_W, PAGE_H = LETTER
MARGIN = 0.55 * 72
SIDEBAR_W = 2.40 * 72
GUTTER = 0.28 * 72
MAIN_X = MARGIN + SIDEBAR_W + GUTTER
MAIN_W = PAGE_W - MAIN_X - MARGIN


def wrap(text, font, size, width):
    return simpleSplit(text, font, size, width)


def draw_text_block(c, text, x, y, font, size, color, width, leading=None):
    """Draw wrapped text and return the new y position."""
    if leading is None:
        leading = size * 1.35
    c.setFont(font, size)
    c.setFillColor(color)
    for line in wrap(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_bullet_block(c, text, x, y, font, size, color, width, leading=None):
    if leading is None:
        leading = size * 1.4
    c.setFont(font, size)
    c.setFillColor(color)
    # bullet glyph
    bullet_indent = 10
    text_x = x + bullet_indent
    text_w = width - bullet_indent
    lines = wrap(text, font, size, text_w)
    if not lines:
        return y
    # bullet (small filled circle in gold)
    c.setFillColor(GOLD)
    c.circle(x + 2.5, y + size * 0.32, 1.4, stroke=0, fill=1)
    c.setFillColor(color)
    for i, line in enumerate(lines):
        c.drawString(text_x, y, line)
        y -= leading
    return y


def section_title(c, label, x, y, width, color_text=NAVY, color_rule=GOLD):
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(color_text)
    c.drawString(x, y, label.upper())
    # underline rule in gold
    c.setStrokeColor(color_rule)
    c.setLineWidth(0.8)
    c.line(x, y - 4, x + width, y - 4)
    return y - 18


def sidebar_section(c, label, x, y, width):
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(NAVY)
    c.drawString(x, y, label.upper())
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(x, y - 4, x + 26, y - 4)
    return y - 13


def draw_header(c):
    # Top navy band
    band_h = 1.45 * 72
    c.setFillColor(NAVY_DEEP)
    c.rect(0, PAGE_H - band_h, PAGE_W, band_h, stroke=0, fill=1)

    # Gold accent stripe
    c.setFillColor(GOLD)
    c.rect(0, PAGE_H - band_h - 3, PAGE_W, 3, stroke=0, fill=1)

    # Name
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 26)
    c.drawString(MARGIN, PAGE_H - 0.55 * 72, "TIMOTHY J. DIME")

    # Title
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(
        MARGIN,
        PAGE_H - 0.82 * 72,
        "DIRECTOR  ·  IT OPERATIONS & INFRASTRUCTURE",
    )

    # Tagline
    c.setFillColor(HexColor("#C9D2DE"))
    c.setFont("Helvetica-Oblique", 9.5)
    c.drawString(
        MARGIN,
        PAGE_H - 1.02 * 72,
        "Capital Partner, Belvedere Trading  ·  Chicago, IL",
    )

    # Contact line (right side)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica", 9)
    right_x = PAGE_W - MARGIN
    contact_lines = [
        "tim@timdime.com",
        "linkedin.com/in/tim10",
        "timdime.com",
    ]
    yy = PAGE_H - 0.55 * 72
    for line in contact_lines:
        tw = c.stringWidth(line, "Helvetica", 9)
        c.drawString(right_x - tw, yy, line)
        yy -= 13


def draw_sidebar_bg(c, top, bottom):
    c.setFillColor(SIDEBAR_BG)
    c.rect(MARGIN, bottom, SIDEBAR_W, top - bottom, stroke=0, fill=1)


# ============================================================
# Content
# ============================================================

SUMMARY = (
    "Director of IT Operations & Infrastructure with 20+ years building and leading the "
    "technology behind a top-tier proprietary options trading firm. Owner of the firm's "
    "production trading environment and the teams that keep it running, with deep "
    "experience across low-latency networks, exchange colocation, FPGA-accelerated "
    "trading, hybrid cloud identity on Azure Entra and Google Cloud, and the "
    "automation and observability that make it all reliable. Capital Partner at "
    "Belvedere Trading since 2011."
)

EXPERIENCE = [
    {
        "title": "Director, IT Operations & Infrastructure",
        "company": "Belvedere Trading, LLC",
        "location": "Chicago, IL",
        "dates": "Sep 2017 — Present",
        "bullets": [
            "Oversee Infrastructure, Release, Support, and Trading Desk Technology teams.",
            "Steward the firm's low-latency edge: exchange colocation, Layer 1 switching, "
            "FPGA-accelerated trading platforms, line-rate PCAP capture, and "
            "GPS-disciplined time precision.",
            "Modernized identity and access with Azure Entra ID — conditional access, "
            "MFA, and Entra-registered apps for the firm's SSO portfolio.",
            "Built out the firm's Google Cloud footprint — VPC peering & private "
            "interconnect for BigQuery-backed analytics — alongside the on-prem "
            "trading stack.",
            "Produce annual budget forecasts, authorize expenditures, and negotiate "
            "multi-year service contracts.",
            "Manage firm-wide projects spanning trading systems, exchange connectivity, "
            "and operational risk.",
        ],
    },
    {
        "title": "Business Intelligence Team Lead",
        "company": "Belvedere Trading, LLC",
        "location": "Chicago, IL",
        "dates": "Mar 2013 — Sep 2017",
        "bullets": [
            "Launched the Business Intelligence function from the ground up.",
            "Normalized data across proprietary software systems to deliver reporting "
            "metrics and trading desk dashboards.",
            "Built a complete employee review platform used by 175+ employees.",
        ],
    },
    {
        "title": "Capital Partner",
        "company": "Belvedere Trading, LLC",
        "location": "Chicago, IL",
        "dates": "Jan 2011 — Present",
        "bullets": [
            "Invited into the partnership in recognition of long-term contribution and "
            "impact to the firm.",
            "Participate in firm-level strategy, risk, and growth discussions.",
        ],
    },
    {
        "title": "Infrastructure & Support Lead",
        "company": "Belvedere Trading, LLC",
        "location": "Chicago, IL",
        "dates": "Dec 2007 — Mar 2013",
        "bullets": [
            "Led the team responsible for the firm's trading desks, internal users, and "
            "core infrastructure — 400+ endpoints across six sites in mixed Linux and "
            "Windows environments.",
            "Built out the firm's trading edge: HP servers, Force10 (Dell) / Arista "
            "switching, exchange colocation, Layer 1 / cut-through switching, and "
            "GPS-disciplined NTP/PTP time sources.",
            "Implemented and supported options trading systems including OptionsCity, "
            "ProOpticus, Orc, Trading Technologies, and Actant.",
            "Built PCAP capture and tick-to-trade measurement to quantify network and "
            "application latency end-to-end.",
            "Introduced proactive monitoring and SLA reporting that improved uptime and "
            "time-to-resolution.",
        ],
    },
    {
        "title": "IT Specialist",
        "company": "Belvedere Trading, LLC",
        "location": "Chicago, IL",
        "dates": "Dec 2006 — Dec 2007",
        "bullets": [
            "Performed all IT functions to support the business as the sole IT "
            "resource — application support, systems administration, network "
            "administration, telecom, and more.",
        ],
    },
    {
        "title": "Level II Desktop Support & Special Projects",
        "company": "Peoples Gas Company, LLC",
        "location": "Chicago, IL",
        "dates": "May 2005 — Dec 2006",
        "bullets": [
            "Promoted to the Special Projects group after six months.",
            "Led the mobile command center initiative and a company-wide infrastructure "
            "upgrade.",
        ],
    },
]

IMPACT = [
    ("Workflow Automation", "Designed and shipped the Belvedere Software Authorization "
     "System, Employee Management System, and Employee Change Notification platform."),
    ("Low-Latency Trading Edge", "Drove the firm's colocation footprint across major "
     "options exchanges, delivered Layer 1 cut-through switching, FPGA-accelerated "
     "market data and order entry, line-rate PCAP capture, and GPS-disciplined "
     "PTP/NTP time distribution."),
    ("Internal Tooling Suite", "Delivered company directory, crypto positions tracking, "
     "interview rooms coordination, Belvedere office maps, and automated authorization "
     "workflows driven by org-chart updates — including market data entitlement and "
     "software access request approval automations."),
    ("Performance Monitoring", "Built custom monitoring, PCAP-based tick-to-trade "
     "measurement, and load-testing tooling to surface latency regressions and "
     "inefficiencies before they affected trading."),
    ("Datacenter & Office Build-outs", "Led 10+ datacenter and office migrations, "
     "moves, and expansions across multiple offices and trading venues."),
    ("Environment Segmentation", "Implemented secure development and production "
     "environment separation to safeguard trading systems from unauthorized access."),
]

SIDEBAR_SKILLS = [
    ("Low-Latency Trading", [
        "Exchange Colocation", "FPGA", "Layer 1 Switching",
        "PCAP Capture", "GPS Time Precision", "PTP / NTP",
        "Tick-to-Trade Measurement", "Kernel Bypass",
    ]),
    ("Cloud & Identity", [
        "Microsoft Azure", "Azure Entra ID", "Entra Apps",
        "Conditional Access", "MFA / SSO", "Google Cloud",
        "GCP VPC Peering", "Private Interconnect", "IAM",
    ]),
    ("Networking & Infrastructure", [
        "BGP", "Multicast", "Arista", "Juniper", "Cisco",
        "Palo Alto", "Data Center Ops",
    ]),
    ("Operating Systems & Virtualization", [
        "Linux", "Windows Server", "AlmaLinux / CentOS / RHEL",
        "macOS", "VMware", "Citrix", "oVirt",
    ]),
    ("Automation & Observability", [
        "SaltStack", "Puppet", "Splunk", "Nagios", "Grafana",
        "Telegraf", "SmokePing", "Claude",
    ]),
    ("Programming & Scripting", [
        "Python", "Bash", "Perl", "PowerShell", "SQL",
        "BigQuery", "Flask", "HTML / CSS",
    ]),
    ("Trading Systems", [
        "OptionsCity", "Trading Technologies", "ProOpticus",
        "Orc", "Actant", "Bloomberg",
    ]),
    ("Data & Storage", [
        "MariaDB", "PostgreSQL", "MSSQL", "InfluxDB",
        "OneTick", "SAN / NAS",
    ]),
    ("Leadership", [
        "Team Management", "Project Management", "Budgeting",
        "Contract Negotiation", "Strategic Planning", "Mentorship",
    ]),
]

EDUCATION = [
    {
        "school": "Western Illinois University",
        "degree": "B.S., Information Management",
        "dates": "2000 — 2004",
    },
]

CREDENTIALS = [
    "FINRA Registered Representative",
    "Capital Partner, Belvedere Trading (2011 — Present)",
]


# ============================================================
# Layout
# ============================================================

def draw_resume():
    c = canvas.Canvas(str(OUTPUT), pagesize=LETTER)
    c.setTitle("Tim Dime — Résumé")
    c.setAuthor("Timothy J. Dime")
    c.setSubject("Director, IT Operations & Infrastructure")

    draw_header(c)

    # Sidebar background (from below header band to bottom margin)
    sidebar_top = PAGE_H - 1.45 * 72 - 18
    sidebar_bottom = MARGIN
    draw_sidebar_bg(c, sidebar_top, sidebar_bottom)

    # ============ Sidebar content ============
    sx = MARGIN + 14
    sw = SIDEBAR_W - 28
    sy = sidebar_top - 18

    sy = sidebar_section(c, "Contact", sx, sy, sw)
    for line in [
        "Chicago, Illinois",
        "tim@timdime.com",
        "linkedin.com/in/tim10",
        "timdime.com",
    ]:
        sy = draw_text_block(c, line, sx, sy, "Helvetica", 9, INK_SOFT, sw, leading=11.5)
    sy -= 4

    sy = sidebar_section(c, "Education", sx, sy, sw)
    for edu in EDUCATION:
        c.setFont("Helvetica-Bold", 9.3)
        c.setFillColor(NAVY)
        c.drawString(sx, sy, edu["degree"])
        sy -= 11
        sy = draw_text_block(c, edu["school"], sx, sy, "Helvetica", 9, INK_SOFT, sw, leading=11)
        c.setFont("Helvetica-Oblique", 8.5)
        c.setFillColor(MUTED)
        c.drawString(sx, sy, edu["dates"])
        sy -= 12
    sy -= 2

    sy = sidebar_section(c, "Credentials", sx, sy, sw)
    for cred in CREDENTIALS:
        sy = draw_bullet_block(c, cred, sx, sy, "Helvetica", 9, INK_SOFT, sw, leading=11.5)
    sy -= 4

    sy = sidebar_section(c, "Skills", sx, sy, sw)
    for header, items in SIDEBAR_SKILLS:
        c.setFont("Helvetica-Bold", 8.8)
        c.setFillColor(NAVY)
        c.drawString(sx, sy, header)
        sy -= 10
        text = "  ·  ".join(items)
        sy = draw_text_block(c, text, sx, sy, "Helvetica", 8.3, INK_SOFT, sw, leading=10.5)
        sy -= 3

    # ============ Main content ============
    mx = MAIN_X
    mw = MAIN_W
    my = sidebar_top - 18

    # Summary
    my = section_title(c, "Summary", mx, my, mw)
    my = draw_text_block(c, SUMMARY, mx, my, "Helvetica", 9.5, INK, mw, leading=13)
    my -= 10

    # Experience
    my = section_title(c, "Experience", mx, my, mw)
    for role in EXPERIENCE:
        # Title row
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(NAVY)
        c.drawString(mx, my, role["title"])

        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(GOLD)
        dates = role["dates"]
        tw = c.stringWidth(dates, "Helvetica-Bold", 9)
        c.drawString(mx + mw - tw, my, dates)
        my -= 13

        # Company line
        c.setFont("Helvetica-Oblique", 9.5)
        c.setFillColor(INK_SOFT)
        c.drawString(
            mx,
            my,
            f"{role['company']}  ·  {role['location']}",
        )
        my -= 12

        for bullet in role["bullets"]:
            my = draw_bullet_block(c, bullet, mx, my, "Helvetica", 9.5, INK, mw, leading=12.6)
            my -= 1

        my -= 7

        # If running near bottom of page and more roles remain, start a new page
        if my < MARGIN + 1.4 * 72 and role is not EXPERIENCE[-1]:
            c.showPage()
            # On continuation page, draw a slim header
            c.setFillColor(NAVY_DEEP)
            c.rect(0, PAGE_H - 0.5 * 72, PAGE_W, 0.5 * 72, stroke=0, fill=1)
            c.setFillColor(GOLD)
            c.rect(0, PAGE_H - 0.5 * 72 - 3, PAGE_W, 3, stroke=0, fill=1)
            c.setFillColor(HexColor("#FFFFFF"))
            c.setFont("Helvetica-Bold", 12)
            c.drawString(MARGIN, PAGE_H - 0.32 * 72, "TIMOTHY J. DIME")
            c.setFont("Helvetica", 9)
            c.setFillColor(HexColor("#C9D2DE"))
            tw = c.stringWidth("tim@timdime.com  ·  linkedin.com/in/tim10", "Helvetica", 9)
            c.drawString(
                PAGE_W - MARGIN - tw,
                PAGE_H - 0.32 * 72,
                "tim@timdime.com  ·  linkedin.com/in/tim10",
            )
            my = PAGE_H - 0.5 * 72 - 28
            my = section_title(c, "Experience (continued)", mx, my, mw)

    # Impact / Selected projects
    my -= 4
    if my < MARGIN + 1.4 * 72:
        c.showPage()
        my = PAGE_H - MARGIN
    my = section_title(c, "Selected Impact", mx, my, mw)
    for title, body in IMPACT:
        c.setFont("Helvetica-Bold", 9.8)
        c.setFillColor(NAVY)
        c.drawString(mx, my, title)
        my -= 12
        my = draw_text_block(c, body, mx, my, "Helvetica", 9.3, INK, mw, leading=12.4)
        my -= 5

    c.save()
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    draw_resume()
