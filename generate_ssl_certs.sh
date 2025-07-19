#!/bin/bash

# Generate SSL certificates for IPv4 address
mkdir -p certs

# Get the machine's IPv4 address
IP_ADDRESS="10.0.0.101"

# Create a certificate configuration file
cat > certs/cert.conf <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = Organization
OU = IT Department
CN = ${IP_ADDRESS}

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
IP.1 = ${IP_ADDRESS}
DNS.1 = localhost
DNS.2 = *.localhost
EOF

# Generate private key
openssl genrsa -out certs/server.key 2048

# Generate certificate signing request
openssl req -new -key certs/server.key -out certs/server.csr -config certs/cert.conf

# Generate self-signed certificate
openssl x509 -req -in certs/server.csr -signkey certs/server.key -out certs/server.crt -days 365 -extensions v3_req -extfile certs/cert.conf

# Generate certificate for Traefik (copy the same cert)
cp certs/server.crt certs/traefik.crt
cp certs/server.key certs/traefik.key

# Set proper permissions
chmod 644 certs/*.crt
chmod 600 certs/*.key

echo "SSL certificates generated successfully!"
echo "Certificate: certs/server.crt"
echo "Private Key: certs/server.key"
echo "IP Address: ${IP_ADDRESS}"
