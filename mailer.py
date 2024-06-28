import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

SENDER_EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
SENDER_EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

CLIENT_EMAIL_ADDRESS = os.getenv("CLIENT_EMAIL_ADDRESS")
HOST_GROUP_NAME = os.getenv("HOST_GROUP_NAME")

img_b64 = "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"
img_link = "https://media.licdn.com/dms/image/D5622AQEqfXHcwcvefg/feedshare-shrink_800/0/1701459708975?e=2147483647&v=beta&t=cGR7USnrxF5r9TC8jad8X6ueg2xTdsWRjFfEt3uqkME"
# Create the HTML for the image
img_html = f'''
<div class="img-container">
<img alt="Bharath Cloud" src="data:image/jpeg;base64,{img_b64}">
</div>
'''

css = """
<style>
    .outer-div {
        display: flex;
        justify-content: space-between;
        width: fit-screen;
        }
    .inner-div {
        display: flex;
        justify-content: space-between;
        width: fit-content;
        }
    .inner-left {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
        margin-right: 10px;
        border-right: 1px solid blue;
        background-color: #f0f0f0;
        }
    .inner-right {
        margin-left: 10px;
        display: flex;
        justify-content: center;
        padding: 10px;
        background-color: #e0e0e0;
        }
    .img-container img {
            width: 50px; /* Adjust as needed */
            height: 50px; /* Adjust as needed */
            object-fit: cover;
        }
    .description {
        font-family: Arial, Helvetica, sans-serif;
        font-weight: 500;
        font-size: 18px;
        color: black;
    }
    .regards p{
        font-family: Arial, Helvetica, sans-serif;
        font-weight: 500;
        height: 100%;
        font-size: 18px;
        color: black;
    } 
    table {
        width: fit-screen;
        border-collapse: collapse;
    }

    thead {
        background-color: rgb(92, 162, 248);
        color: white;
        border-spacing: none;
    }
    th {
        padding: 3px;
        border-right: 0.5px solid black;
        font-size: larger;
        font-weight: bold;
        text-align: center;
    }
    td {
        color: black;
        width: fit-content;
        padding: 3px;
        text-align: center;
        border-right: 0.5px solid black;
        font-weight: bold;
        font-size: small;
        white-space: nowrap;
    }
    tr {
        border-bottom: 0.1px solid black; 
    }
    body {
        display: flex;
        flex-direction: column;
    }
</style>
"""

description = """
<p class="description" style="color:black;">Hi Sir,<br>
Greetings for the day!!!<br>
Please find the current servers' utilization report.
</p>
"""

signature = f"""
<table cellpadding="0" cellspacing="0" width="100%" border="0">
        <tr>
            <td width="30%" valign="top" style="padding: 10px; border-right:0.5px solid blue;">
                {img_html}
            </td>
            <td width="70%" valign="top" style="padding: 10px; text-align:left;">
                <p>
                <b>GNOC Support</b><br>
                Phone: 040 45209900<br>
                www.bharathcloud.com<br>
                <a href="https://www.linkedin.com/company/bharathcloud/posts/?feedView=all"> BHARATH CLOUD ON LINKEDIN </a><br></p>
            </td>
        </tr>
    </table>
"""

regards = f"""
<div class="regards">
<div>
<p>
Thanks & Regards,<br>
</p>
</div>
{signature}
<p style="font-size:13px;">	
<b>Disclaimer</b>:  This email and any files transmitted with it are confidential and
intended solely for the use of the individual or entity to whom they are addressed. 
If you have received this email in error please notify the system manager. 
This message contains confidential information and is intended only for the individual named. 
If you are not the named addressee you should not disseminate, distribute 
or copy this e-mail. Please notify the sender immediately by e-mail if you have 
received this e-mail by mistake and delete this e-mail from your system. If you are 
not the intended recipient you are notified that disclosing, copying, distributing or 
taking any action in reliance on the contents of this information is strictly prohibited.
</p>
</div>
</div>
"""
# Read the CSV file into a DataFrame
df = pd.read_csv(f'{HOST_GROUP_NAME}.csv')
# df.drop(columns=["diskC_avg", "diskD_avg"], inplace=True)
df[["cpu_avg", "cpu_max", "memory_avg", "memory_max"]] = df[["cpu_avg", "cpu_max", "memory_avg", "memory_max"]].astype(str) + "%"
# df.rename(columns= {"diskC_max": "C: Max Disk Utilization", "diskD_max": "D: Max Disk Utilization"}, inplace=True)

df.columns = df.columns.str.upper()

# Convert the DataFrame to HTML
# Convert the DataFrame to HTML with formatting
table = df.to_html(index=False)
title = f"""
<h1 style="text-decoration:underline; text-align: center; color: black;">{HOST_GROUP_NAME.capitalize()}</h1>
"""
attachment = f"""
<html>
<head>
    {css}
</head>
<body>
    {description}
    {title}
    {table}
    {regards}
</body>
</html>
"""
# html = df.to_html()
# print(html)

# Create a multipart message
msg = MIMEMultipart()
msg['From'] = f'{SENDER_EMAIL_ADDRESS}'
msg['To'] = f"{CLIENT_EMAIL_ADDRESS}"
msg['Subject'] = 'Server Utilization Report'

# Attach the HTML to the message
msg.attach(MIMEText(attachment, 'html'))
print("mail ready")
# Send the email
# Send the email
with smtplib.SMTP('smtp.office365.com', 587) as server:
    server.starttls()
    server.login(f'{SENDER_EMAIL_ADDRESS}', f'{SENDER_EMAIL_PASSWORD}')
    server.send_message(msg)

print("Email sent successfully")
