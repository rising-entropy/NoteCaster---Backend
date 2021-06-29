import hashlib

str = "GeeksforGeeks"
result = hashlib.sha256(str.encode()).hexdigest()
print(result)
