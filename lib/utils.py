from hashlib import shake_256


# Hashes are never deleted so table will balloon.
class HashMap:

    HASH_LENGTH = 3

    def __init__(self, dao):
        self._dao = dao
        self._cache = {}

    def decode(self, hash_str):
        result = self._cache.get(hash_str)
        if result is None:
            results = self._dao.select('hashmap', {'hash': hash_str}, return_one=True)
            result = int(results[2]) if results else None
        return result

    def encode(self, id_int):
        id_int = int(id_int)
        hash_str = shake_256(str(id_int).encode()).hexdigest(self.HASH_LENGTH)
        if hash_str not in self._cache:
            self._cache[hash_str] = id_int
            self._dao.insert('hashmap', [hash_str, id_int])
        return hash_str