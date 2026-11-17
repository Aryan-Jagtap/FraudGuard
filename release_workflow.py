
import json
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

RELEASE_VERSION = "v1.0.0"

PRODUCTION_DIR = Path("deployment/production_simulation")
REPORT_DIR = Path("reports")

PRODUCTION_DIR.mkdir(parents=True, exist_ok=True)

checks = []


def record_check(name, passed, details):
    checks.append({
        "check": name,
        "status": "PASS" if passed else "FAIL",
        "details": details
    })


# ---------------------------------------
# STAGE 1: TEST ENVIRONMENT
# ---------------------------------------

print("\n========== STAGE 1: TEST ==========")

transaction_file = Path("data/analyzed_transactions.csv")
rule_file = Path("rule_engine.py")

transaction_test = transaction_file.exists()
rule_test = rule_file.exists()

record_check(
    "Analyzed transaction file",
    transaction_test,
    "data/analyzed_transactions.csv exists"
)

record_check(
    "Rule engine",
    rule_test,
    "rule_engine.py exists"
)

# ---------------------------------------
# STAGE 2: UAT VALIDATION
# ---------------------------------------

print("\n========== STAGE 2: UAT ==========")

uat_file = REPORT_DIR / "uat_report.csv"

uat_passed = False

if uat_file.exists():

    uat = pd.read_csv(uat_file)

    uat_passed = (
        len(uat) > 0
        and (uat["status"] == "PASS").all()
    )

    details = (
        f"{(uat['status'] == 'PASS').sum()}/{len(uat)} "
        "test cases passed"
    )

else:
    details = "UAT report not found"

record_check(
    "UAT approval",
    uat_passed,
    details
)

# ---------------------------------------
# STAGE 3: PRODUCTION SIMULATION
# ---------------------------------------

print("\n========== STAGE 3: RELEASE ==========")

database_file = Path("database/fraudguard.db")

database_valid = False
database_count = 0

if database_file.exists():

    connection = sqlite3.connect(database_file)

    try:
        database_count = pd.read_sql_query(
            "SELECT COUNT(*) AS total FROM transactions",
            connection
        ).iloc[0]["total"]

        database_valid = database_count == 5000

    except Exception:
        database_valid = False

    finally:
        connection.close()

record_check(
    "Database validation",
    database_valid,
    f"{database_count} transaction records found"
)

# Check release prerequisites
prerequisites_passed = all(
    item["status"] == "PASS"
    for item in checks
)

if not prerequisites_passed:
    print("\nRelease blocked. Resolve failed checks first.")

else:

    # Package release files
    files_to_package = [
        Path("rule_engine.py"),
        Path("app.py"),
        Path("database.py"),
        Path("requirements.txt"),
        Path("data/analyzed_transactions.csv"),
        Path("database/fraudguard.db"),
        Path("reports/uat_report.csv"),
        Path("reports/performance_report.csv"),
        Path("reports/rule_analysis.csv")
    ]

    package_dir = PRODUCTION_DIR / "release_package"
    package_dir.mkdir(parents=True, exist_ok=True)

    for source in files_to_package:

        if source.exists():

            destination = package_dir / source.name

            shutil.copy2(source, destination)

    # Generate release manifest
    manifest = {
        "project": "FraudGuard",
        "release_version": RELEASE_VERSION,
        "release_type": "Academic Production Simulation",
        "release_timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "transaction_records": int(database_count),
        "uat_status": "APPROVED",
        "release_status": "SIMULATED"
    }

    manifest_path = PRODUCTION_DIR / "release_manifest.json"

    with open(manifest_path, "w") as file:
        json.dump(manifest, file, indent=4)

    print("Release package created successfully.")

# ---------------------------------------
# STAGE 4: POST-VERIFICATION
# ---------------------------------------

print("\n========== STAGE 4: PVT ==========")

package_dir = PRODUCTION_DIR / "release_package"

required_release_files = [
    "rule_engine.py",
    "app.py",
    "database.py",
    "analyzed_transactions.csv",
    "fraudguard.db",
    "uat_report.csv",
    "performance_report.csv",
    "rule_analysis.csv"
]

package_valid = (
    package_dir.exists()
    and all(
        (package_dir / filename).exists()
        for filename in required_release_files
    )
)

record_check(
    "Release package integrity",
    package_valid,
    "Required release artifacts are present"
)

manifest_valid = (
    PRODUCTION_DIR / "release_manifest.json"
).exists()

record_check(
    "Release manifest",
    manifest_valid,
    "Release version and approval information recorded"
)

pvt_report = pd.DataFrame(checks)

pvt_report.to_csv(
    REPORT_DIR / "pvt_report.csv",
    index=False
)

print("\n========== RELEASE VERIFICATION REPORT ==========")
print(pvt_report.to_string(index=False))

print("\nRelease checks passed:",
      (pvt_report["status"] == "PASS").sum())

print("Release checks failed:",
      (pvt_report["status"] == "FAIL").sum())

if (pvt_report["status"] == "PASS").all():
    print("\nFRAUDGUARD RELEASE SIMULATION SUCCESSFUL.")
else:
    print("\nRELEASE VERIFICATION FAILED. CHECK REPORT.")
