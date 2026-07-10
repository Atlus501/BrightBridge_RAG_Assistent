from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib
import base64
import logging
import warnings

"""
This is the class responsible for symmetrical encryption in this workflow. It has a method
for encryption and decryption. Currently it uses AES-GCM.
"""
class Cryptographer:

  """
  Initializes the Cryptography_Manager. It has many preset values for the lengths
  of cryptographic elements like the salt, iv, ect. For the iteration_count, it is
  recommended to set the value to at least 600000 to meet modern security standards.
  """
  def __init__(self, salt_length=16, iv_length=12, tag_length=16, hash_name="SHA512",
               iteration_count=700000, key_length=32):

    #sets key value for cryptographer
    self.salt_length = salt_length
    self.iv_length = iv_length
    self.tag_length = tag_length
    self.hash_name = hash_name
    self.iteration_count = iteration_count
    self.key_length = key_length

    #initialize logger
    self.logger = logging.getLogger(__name__)

    if iteration_count < 600000:
      warnings.warn("It is generally recommended to have an iteration count >= 600000")

  """
  Encrypts a message using a password and AES-GCM. Required inputs are a secure password
  and the message to be encrypted. Returns the encrypted message if successful.
  Otherwise, runtime and value errors may be raised (depending on the situation).
  """
  def encrypt(self, password: str, message: str) -> str:
    try:
      #generating the salt, iv, secret, and cipher
      salt = get_random_bytes(self.salt_length)
      iv = get_random_bytes(self.iv_length)
      secret = self.get_secret_key(password, salt)
      cipher = AES.new(secret, AES.MODE_GCM, iv)

      #encrypts the message and combining all elements to create the ciphertext
      ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
      ciphertext = salt + iv + ciphertext + tag

      encoded_ciphertext = base64.b64encode(ciphertext)
      return bytes.decode(encoded_ciphertext)

    except Exception as e:
      self.logger.error(f"A problem has occured during encryption: {str(e)}")
      raise RuntimeError(f"A problem has occured during message encryption") from e

  """
  Decrypts a message using a password and AES-GCM. Required inputs are a secure password
  and the encrypted message. Returns the decrypted message if successful.
  Otherwise, runtime errors will be raised.
  """
  def decrypt(self, password: str, encrypted_message: str) -> str:
    try:
      encrypted_message = base64.b64decode(encrypted_message)
      iv_end = self.salt_length + self.iv_length

      #extracting key values from the encrypted message
      salt = encrypted_message[:self.salt_length]
      iv = encrypted_message[self.salt_length:iv_end]
      tag = encrypted_message[-self.tag_length:]
      ciphertext = encrypted_message[iv_end: -self.tag_length]

      #retrieving the secret and creating the cipher
      secret = self.get_secret_key(password, salt)
      cipher = AES.new(secret, AES.MODE_GCM, iv)

      plaintext = cipher.decrypt_and_verify(ciphertext, tag)
      return plaintext.decode('utf-8')
    except ValueError as e:
      self.logger.error(f"Decryption failed due to authentication tag mismatch or invalid data: {e}")
      raise ValueError("Authentication failed or message tampered") from e
    except Exception as e:
      self.logger.error(f"A problem has occured during decryption: {str(e)}")
      raise RuntimeError(f"A problem has occured during message decryption") from e

  """
  Uses pbkdf2 to create a secure secret using the password and salt from the user.
  May raise runtime errors if the password, hashing method, or salt are invalid.
  """
  def get_secret_key(self, password: str, salt):
    try:
      return hashlib.pbkdf2_hmac(self.hash_name, password.encode('utf-8'), salt, self.iteration_count, self.key_length)
    except Exception as e:
      self.logger.error(f"A problem has occured during secret key creation: {str(e)}")
      raise RuntimeError(f"A problem has occured during secret key creation") from e
