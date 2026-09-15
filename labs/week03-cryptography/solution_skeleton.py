"""
Week 3 — FIX the misuse here. Fill in the TODOs.
pip install argon2-cffi pycryptodome
"""
import os
import hashlib
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from Crypto.Cipher import AES

ph = PasswordHasher()

# --- Task 6: Password Storage & Migration ---

def store_password(pw: str) -> str:
    # FIX: argon2id, salted automatically
    return ph.hash(pw)

def verify_and_migrate_password(hash_: str, pw: str) -> tuple[bool, str]:
    """
    Verifies a password and returns (is_valid, new_hash_if_needed).
    Handles upgrading legacy MD5 hashes to Argon2id upon login.
    """
    # 1. Check for legacy MD5 (32 hex chars)
    if len(hash_) == 32 and hash_.isalnum():
        legacy_hasher = hashlib.md5()
        legacy_hasher.update(pw.encode('utf-8'))
        
        if legacy_hasher.hexdigest() == hash_:
            # Migration path: Old MD5 is correct, generate new Argon2id hash
            return True, store_password(pw)
        return False, ""

    # 2. Standard Argon2id verification
    try:
        ph.verify(hash_, pw)
        # Check if Argon2 parameters need upgrading based on current server settings
        if ph.check_needs_rehash(hash_):
            return True, store_password(pw)
        return True, ""
    except Exception:
        return False, ""

# --- Task 7: Authenticated Encryption Round-Trip ---

def encrypt_gcm(data: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
    # FIX: authenticated encryption (AES-GCM), random nonce, key from env/KMS
    nonce = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(data)
    return nonce, ct, tag

def decrypt_gcm(nonce: bytes, ct: bytes, tag: bytes, key: bytes) -> bytes:
    """Decrypts and verifies AES-GCM ciphertext."""
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    # decrypt_and_verify will automatically raise a ValueError if the tag is invalid
    return cipher.decrypt_and_verify(ct, tag)

# --- CSPRNG ---

def reset_token() -> str:
    # FIX: CSPRNG
    import secrets
    return secrets.token_urlsafe(16)


if __name__ == "__main__":
    # --- Test Task 6 ---
    print("--- Task 6: Password Migration ---")
    legacy_md5_hash = hashlib.md5(b"password123").hexdigest()
    print(f"Legacy MD5: {legacy_md5_hash}")
    
    is_valid, new_hash = verify_and_migrate_password(legacy_md5_hash, "password123")
    print(f"MD5 Login Valid? {is_valid}")
    print(f"Upgraded Hash:   {new_hash[:30]}...\n")

    # --- Test Task 7 ---
    print("--- Task 7: AEAD Round-Trip & Tamper Check ---")
    key = bytes.fromhex(os.environ.get("ENC_KEY_HEX", os.urandom(32).hex()))
    original_data = b"secret note"
    
    # Round-trip
    nonce, ct, tag = encrypt_gcm(original_data, key)
    print(f"Ciphertext (hex): {ct.hex()}")
    
    decrypted_data = decrypt_gcm(nonce, ct, tag, key)
    print(f"Decrypted: {decrypted_data.decode()}")
    print("Status: Round-trip successful!\n")

    # Tampered-fails proof
    print("Tampering with ciphertext...")
    tampered_ct = bytearray(ct)
    tampered_ct[0] ^= 0xFF # Flip bits in the first byte
    tampered_ct = bytes(tampered_ct)
    
    try:
        decrypt_gcm(nonce, tampered_ct, tag, key)
        print("Status: Decryption succeeded (WARNING: THIS SHOULD NOT HAPPEN)")
    except ValueError as e:
        print(f"Status: Decryption blocked! Caught exception: {e}")