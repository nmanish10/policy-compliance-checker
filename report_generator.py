from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white


def wrap_text(text, max_len=85):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        if len(current + word) < max_len:
            current += word + " "
        else:
            lines.append(current.strip())
            current = word + " "

    lines.append(current.strip())
    return lines


def generate_pdf_report(data, path):

    c = canvas.Canvas(path, pagesize=letter)

    width, height = letter
    y = height - 50

    score = data["compliance_score"]

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, y, "Policy Compliance Report")

    y -= 35

    c.setStrokeColor(HexColor("#CBD5F5"))
    c.line(50, y, width - 50, y)

    y -= 30

    # --------------------------------------------------
    # STATUS BANNER
    # --------------------------------------------------

    if score >= 80:
        banner_color = HexColor("#16A34A")
        status = "COMPLIANT"
    elif score >= 50:
        banner_color = HexColor("#F59E0B")
        status = "PARTIALLY COMPLIANT"
    else:
        banner_color = HexColor("#DC2626")
        status = "NON-COMPLIANT"

    c.setFillColor(banner_color)
    c.rect(50, y, 500, 25, fill=1)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y + 7, f"COMPLIANCE STATUS: {status}")

    c.setFillColor(HexColor("#000000"))

    y -= 40

    # --------------------------------------------------
    # META INFORMATION
    # --------------------------------------------------

    c.setFont("Helvetica", 11)

    c.drawString(50, y, f"Run ID: {data['run_id']}")
    y -= 18

    c.drawString(50, y, f"Timestamp: {data['timestamp']}")
    y -= 18

    c.drawString(50, y, f"Rule Version: {data['rule_version']}")

    y -= 30

    c.setStrokeColor(HexColor("#CBD5F5"))
    c.line(50, y, width - 50, y)

    y -= 25

    # --------------------------------------------------
    # COMPLIANCE SUMMARY
    # --------------------------------------------------

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Compliance Summary")

    y -= 25

    # Score color
    if score >= 80:
        score_color = HexColor("#16A34A")
    elif score >= 50:
        score_color = HexColor("#F59E0B")
    else:
        score_color = HexColor("#DC2626")

    # Score badge
    c.setFillColor(score_color)
    c.rect(60, y - 5, 90, 24, fill=1)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(70, y + 2, f"{score}%")

    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica", 12)
    c.drawString(160, y + 2, "Compliance Score")

    y -= 25

    c.setFont("Helvetica", 11)
    c.drawString(60, y, f"Risk Level: {data['risk_level']}")

    y -= 30

    c.setStrokeColor(HexColor("#CBD5F5"))
    c.line(50, y, width - 50, y)

    y -= 25

    # --------------------------------------------------
    # VIOLATION TABLE
    # --------------------------------------------------

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Detected Violations")

    y -= 20

    c.setFont("Helvetica-Bold", 11)

    c.drawString(60, y, "Rule Description")
    c.drawString(420, y, "Severity")

    y -= 10
    c.line(50, y, 550, y)

    y -= 15

    c.setFont("Helvetica", 11)

    if data["violations"]:

        for v in data["violations"]:

            rule_text = v["description"]
            severity = v["severity"]

            lines = wrap_text(rule_text, 60)

            # description
            c.drawString(60, y, lines[0])

            # severity color
            if severity == "critical":
                c.setFillColor(HexColor("#DC2626"))
            elif severity == "minor":
                c.setFillColor(HexColor("#F59E0B"))
            else:
                c.setFillColor(HexColor("#000000"))

            c.drawString(420, y, severity)

            c.setFillColor(HexColor("#000000"))

            y -= 16

            for line in lines[1:]:
                c.drawString(60, y, line)
                y -= 14

            y -= 6

    else:

        c.drawString(60, y, "No violations detected.")
        y -= 20

    y -= 10

    c.setStrokeColor(HexColor("#CBD5F5"))
    c.line(50, y, width - 50, y)

    y -= 25

    # --------------------------------------------------
    # SUGGESTIONS
    # --------------------------------------------------

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Policy Improvement Recommendations")

    y -= 20

    c.setFont("Helvetica", 11)

    suggestions = data.get("suggestions", [])

    if suggestions:

        for suggestion in suggestions:

            clean = suggestion.replace("```json", "").replace("```", "").strip()

            lines = wrap_text(clean)

            first = True

            for line in lines:

                if first:
                    c.drawString(60, y, f"• {line}")
                    first = False
                else:
                    c.drawString(75, y, line)

                y -= 16

            y -= 8

    else:

        c.drawString(60, y, "No improvement recommendations required.")
        y -= 20

    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    c.setStrokeColor(HexColor("#CBD5F5"))
    c.line(50, 60, width - 50, 60)

    c.setFont("Helvetica-Oblique", 9)

    c.drawString(
        50,
        40,
        "Generated by Policy Compliance Intelligence AI System"
    )

    c.save()