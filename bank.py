# Import the necessary libraries
from pyzbar import pyzbar
from PIL import Image
import crc16

def extract_data(string):
  # Parse the string to extract the tag numbers, lengths, and values
  tags = []
  i = 0
  while i < len(string):
    tag = string[i:i+2]
    length = int(string[i+2:i+4])
    value = string[i+4:i+4+length]
    tags.append((tag, length, value))
    i = i + 4 + length
  
    print(tags)
  # Use the tag numbers to extract the transaction reference ID and sending bank ID
  ref_id = None
  bank_id = None
  for tag, length, value in tags:
    if tag == "02":
      ref_id = value
    elif tag == "01":
      bank_id = value

  # Return the extracted values
  return ref_id, bank_id
# Open the image containing the bank slip and convert it to a format that can be processed by pyzbar
image = Image.open('bank.png')

# Detect and decode the QR code in the image
codes = pyzbar.decode(image)
# Loop through the detected QR codes
for code in codes:
    # Extract the data from the QR code
    data = code.data.decode('utf-8')
    # Use string manipulation techniques to extract the amount from the data string
    a = extract_data(data)
    print(a)

    # Print the extracted amount

import requests

url = "https://api-sandbox.partners.scb/partners/sandbox/v1/payment/billpayment/transactions/202212154H4p2SCo0aA8wo5OZ"

payload={'sendingBank':'014'}
headers = {
  'authorization': 'Bearer 63dd19fa-8b65-4b06-91ea-fb005ca211e7',
  'requestUID': 'Bearer 67cf833b-7752-41e9-b403-eaea1f8fed83',
  'resourceOwnerID': 'l7bdbb9e7557434128b81691e5dab1b73b',
  'accept-language': 'EN',
}

response = requests.request("GET", url, params=payload,headers=headers)

print(response.text)
print(response.url)

