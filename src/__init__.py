import bcrypt

password = 'admin'

print(bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode())