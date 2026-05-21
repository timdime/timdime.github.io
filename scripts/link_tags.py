#!/usr/bin/env python3
"""One-off script to convert <span class="tag">X</span> to anchor tags with appropriate
external links across every skill card in the Expertise section, and to insert the
Corvil tag in Networking & Infrastructure.

Idempotent enough to run once.
"""

from pathlib import Path
import re

HTML = Path(__file__).resolve().parent.parent / "index.html"

# Mapping of tag label -> external URL
TAG_LINKS = {
    # Operating Systems & Virtualization
    "Linux": "https://www.kernel.org/",
    "Windows Server": "https://www.microsoft.com/en-us/windows-server",
    "AlmaLinux / CentOS / RHEL": "https://almalinux.org/",
    "macOS": "https://www.apple.com/macos/",
    "VMware": "https://www.vmware.com/",
    "Citrix": "https://www.citrix.com/",
    "oVirt": "https://www.ovirt.org/",

    # Networking & Infrastructure
    "BGP": "https://en.wikipedia.org/wiki/Border_Gateway_Protocol",
    "Multicast": "https://en.wikipedia.org/wiki/IP_multicast",
    "Layer 1 Switching": "https://www.arista.com/en/products/7130-quantum-series-platform",
    "Colocation": "https://en.wikipedia.org/wiki/Colocation_centre",
    "Arista": "https://www.arista.com/",
    "Juniper": "https://www.juniper.net/",
    "Cisco": "https://www.cisco.com/",
    "Palo Alto": "https://www.paloaltonetworks.com/",
    "Corvil": "https://www.pico.net/corvil/",
    "Data Center Ops": "https://en.wikipedia.org/wiki/Data_center",

    # Automation & Observability
    "SaltStack": "https://saltproject.io/",
    "Puppet": "https://www.puppet.com/",
    "Splunk": "https://www.splunk.com/",
    "Nagios": "https://www.nagios.org/",
    "Grafana": "https://grafana.com/",
    "Telegraf": "https://www.influxdata.com/time-series-platform/telegraf/",
    "SmokePing": "https://oss.oetiker.ch/smokeping/",
    "Claude": "https://www.anthropic.com/claude",

    # Programming & Scripting
    "Python": "https://www.python.org/",
    "Bash": "https://www.gnu.org/software/bash/",
    "Perl": "https://www.perl.org/",
    "PowerShell": "https://learn.microsoft.com/en-us/powershell/",
    "SQL": "https://en.wikipedia.org/wiki/SQL",
    "BigQuery": "https://cloud.google.com/bigquery",
    "Flask": "https://flask.palletsprojects.com/",
    "HTML / CSS": "https://developer.mozilla.org/en-US/docs/Web",

    # Trading Systems
    "OptionsCity": "https://en.wikipedia.org/wiki/OptionsCity_Software",
    "Trading Technologies": "https://www.tradingtechnologies.com/",
    "ProOpticus": "https://www.options-it.com/",
    "Orc": "https://en.wikipedia.org/wiki/Orc_Software",
    "Actant": "https://www.actant.com/",
    "Bloomberg": "https://www.bloomberg.com/professional/",
    "Exchange Access": "https://en.wikipedia.org/wiki/Direct_market_access",

    # Low-Latency Trading
    "Exchange Colocation": "https://en.wikipedia.org/wiki/Co-location_(business)",
    "FPGA": "https://en.wikipedia.org/wiki/Field-programmable_gate_array",
    "PCAP Capture": "https://en.wikipedia.org/wiki/Pcap",
    "GPS Time Precision": "https://en.wikipedia.org/wiki/GPS_disciplined_oscillator",
    "PTP / NTP": "https://en.wikipedia.org/wiki/Precision_Time_Protocol",
    "Tick-to-Trade Measurement": "https://en.wikipedia.org/wiki/High-frequency_trading",
    "Kernel Bypass": "https://en.wikipedia.org/wiki/Kernel_(operating_system)",

    # Cloud & Identity
    "Microsoft Azure": "https://azure.microsoft.com/",
    "Azure Entra ID": "https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id",
    "Entra Apps": "https://learn.microsoft.com/en-us/entra/identity-platform/",
    "Conditional Access": "https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview",
    "MFA / SSO": "https://learn.microsoft.com/en-us/entra/identity/authentication/concept-mfa-howitworks",
    "Google Cloud": "https://cloud.google.com/",
    "GCP VPC Peering": "https://cloud.google.com/vpc/docs/vpc-peering",
    "Private Interconnect": "https://cloud.google.com/network-connectivity/docs/interconnect",
    "IAM": "https://cloud.google.com/iam",

    # Data & Storage
    "MariaDB": "https://mariadb.org/",
    "PostgreSQL": "https://www.postgresql.org/",
    "MSSQL": "https://www.microsoft.com/en-us/sql-server",
    "InfluxDB": "https://www.influxdata.com/",
    "OneTick": "https://www.onetick.com/",
    "SAN / NAS": "https://en.wikipedia.org/wiki/Storage_area_network",

    # Leadership
    "Team Management": "https://en.wikipedia.org/wiki/Team_management",
    "Project Management": "https://en.wikipedia.org/wiki/Project_management",
    "Budgeting": "https://en.wikipedia.org/wiki/Budget",
    "Contract Negotiation": "https://en.wikipedia.org/wiki/Negotiation",
    "Strategic Planning": "https://en.wikipedia.org/wiki/Strategic_planning",
    "Mentorship": "https://en.wikipedia.org/wiki/Mentorship",

    # Industry & Compliance
    "Equity Derivatives": "https://en.wikipedia.org/wiki/Equity_derivative",
    "Commodity Derivatives": "https://en.wikipedia.org/wiki/Commodity_market",
    "Market Data": "https://en.wikipedia.org/wiki/Market_data",
    "FINRA Registered": "https://www.finra.org/registration-exams-ce",
    "Risk Management": "https://en.wikipedia.org/wiki/Risk_management",
}


def main() -> None:
    text = HTML.read_text()

    # Insert Corvil after Palo Alto in the Networking & Infrastructure card if not present
    if 'class="tag">Corvil<' not in text:
        text = text.replace(
            '<span class="tag">Palo Alto</span>\n                        <span class="tag">Data Center Ops</span>',
            '<span class="tag">Palo Alto</span>\n                        <span class="tag">Corvil</span>\n                        <span class="tag">Data Center Ops</span>',
        )

    # Convert each <span class="tag">LABEL</span> to an anchor with the mapped URL
    missing: list[str] = []

    def replace(match: re.Match) -> str:
        label = match.group(1)
        url = TAG_LINKS.get(label)
        if not url:
            missing.append(label)
            return match.group(0)
        return (
            f'<a class="tag" href="{url}" target="_blank" rel="noopener">'
            f'{label}</a>'
        )

    new_text, n = re.subn(
        r'<span class="tag">([^<]+)</span>',
        replace,
        text,
    )

    if missing:
        unique_missing = sorted(set(missing))
        print("Missing URL mapping for:", unique_missing)
        raise SystemExit(1)

    HTML.write_text(new_text)
    print(f"Linked {n} tag(s) and ensured Corvil is present.")


if __name__ == "__main__":
    main()
