"""
OpenClaw OpenRouter Usage Daily Alert
Screenshots the usage chart from the OpenClaw app page on OpenRouter and emails it as a PDF.
"""

import io
import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import img2pdf
from PIL import Image
from playwright.sync_api import sync_playwright

URL = "https://openrouter.ai/apps?url=https%3A%2F%2Fopenclaw.ai%2F"


def capture_screenshot():
    """Capture the OpenClaw usage chart section."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        print("Loading OpenClaw app page...")
        page.goto(URL, wait_until="networkidle", timeout=60000)

        # Wait for JS-rendered chart to finish drawing
        page.wait_for_timeout(8000)

        screenshot_bytes = None
        try:
            # Locate the chart container by its heading text
            heading = page.locator("text=OpenClaw OpenRouter Usage").first
            heading.wait_for(timeout=10000)

            # Walk up to the section container that wraps the badges + chart
            # The badges (#1 in Productivity etc.) sit just above the chart card,
            # so we go up a few levels from the heading to capture them too.
            container = heading.locator("xpath=ancestor::div[3]").first
            box = container.bounding_box()

            if box:
                # Add a small padding around the element
                padding = 16
                clip = {
                    "x": max(0, box["x"] - padding),
                    "y": max(0, box["y"] - padding),
                    "width": box["width"] + padding * 2,
                    "height": box["height"] + padding * 2,
                }
                screenshot_bytes = page.screenshot(clip=clip)
                print(f"Chart screenshot captured ({int(box['width'])}x{int(box['height'])}px).")
            else:
                raise RuntimeError("Could not get bounding box for chart container.")

        except Exception as e:
            print(f"Could not isolate chart, falling back to full viewport: {e}")
            screenshot_bytes = page.screenshot()

        browser.close()

    return screenshot_bytes


def convert_to_pdf(screenshot_bytes):
    """Convert screenshot to PDF."""
    img = Image.open(io.BytesIO(screenshot_bytes)).convert("RGB")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img2pdf.convert(img_bytes.read())


def send_email(pdf_bytes, recipient_email):
    """Send the PDF as an email attachment via Gmail SMTP."""
    sender_email = os.environ.get("GMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        raise ValueError("GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables must be set.")

    date_str = datetime.now().strftime("%Y-%m-%d")

    msg = MIMEMultipart()
    msg["Subject"] = f"OpenClaw Usage — {date_str}"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    body = MIMEText(
        f"Attached: OpenClaw OpenRouter usage chart for {date_str}.",
        "plain",
    )
    msg.attach(body)

    attachment = MIMEBase("application", "pdf")
    attachment.set_payload(pdf_bytes)
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        f"attachment; filename=openclaw-usage-{date_str}.pdf",
    )
    msg.attach(attachment)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

    print(f"Email sent to {recipient_email}")


def main():
    recipient_email = "jt@lokoyacap.com"

    print(f"OpenClaw alert — {datetime.now().strftime('%Y-%m-%d')}")
    screenshot_bytes = capture_screenshot()

    print("Generating PDF...")
    pdf_bytes = convert_to_pdf(screenshot_bytes)

    print("Sending email...")
    send_email(pdf_bytes, recipient_email)


if __name__ == "__main__":
    main()
