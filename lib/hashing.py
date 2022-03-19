from hashlib import shake_256, sha256

SHAKE256_3 = 'shake256_3'
SHA256 = 'sha256'


# Hashes are never deleted so table will balloon.
class HashManager:

    HASH_LENGTH = 3

    def __init__(self, dao):
        self._dao = dao
        self._cache = {}
        self._methods = {
            SHAKE256_3: HashManager.shake256_3,
            SHA256: HashManager.sha256,
        }

    @staticmethod
    def shake256_3(to_hash):
        return shake_256(str(to_hash).encode()).hexdigest(3)

    @staticmethod
    def sha256(to_hash):
        return sha256(str(to_hash).encode()).hexdigest()

    def decode(self, hash_str):
        result = self._cache.get(hash_str)
        if result is None:
            results = self._dao.select('hashmap', {'hash': hash_str}, return_one=True)
            result = int(results[2]) if results else None
        return result

    def encode(self, id_int, hash_method=SHA256):
        hash_str = self._methods.get(hash_method)(int(id_int))
        if hash_str not in self._cache:
            self._cache[hash_str] = id_int
            self._dao.insert('hashmap', [hash_str, id_int])
        return hash_str
