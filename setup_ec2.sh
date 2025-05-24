#!/bin/bash

# Script para configurar o ambiente na instância EC2
# Execute este script como sudo: sudo bash setup_ec2.sh

# Atualizar o sistema
echo "Atualizando o sistema..."
apt-get update
apt-get upgrade -y

# Instalar dependências
echo "Instalando dependências..."
apt-get install -y python3-pip python3-dev libmysqlclient-dev nginx supervisor git

# Criar diretório para logs do Gunicorn
mkdir -p /var/log/gunicorn
chmod 777 /var/log/gunicorn

# Configurar o MySQL
echo "Instalando MySQL..."
apt-get install -y mysql-server

# Iniciar e habilitar o MySQL
systemctl start mysql
systemctl enable mysql

# Configurar o banco de dados (você precisará executar estes comandos manualmente)
echo "Para configurar o banco de dados, execute os seguintes comandos:"
echo "mysql -u root -p"
echo "CREATE DATABASE sistema_eleicao CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "CREATE USER 'seu_usuario_mysql'@'localhost' IDENTIFIED BY 'sua_senha_mysql';"
echo "GRANT ALL PRIVILEGES ON sistema_eleicao.* TO 'seu_usuario_mysql'@'localhost';"
echo "FLUSH PRIVILEGES;"
echo "EXIT;"

# Configurar o ambiente Python
echo "Configurando ambiente Python..."
pip3 install --upgrade pip
pip3 install virtualenv

# Criar e configurar arquivo .env
echo "Criando arquivo .env a partir do exemplo..."
cp .env.example .env
echo "Edite o arquivo .env com suas configurações reais: nano .env"

# Configurar o Supervisor para gerenciar o Gunicorn
echo "Configurando o Supervisor..."
cat > /etc/supervisor/conf.d/evoto.conf << EOF
[program:evoto]
command=/home/ubuntu/e-voto-main/venv/bin/gunicorn --config=/home/ubuntu/e-voto-main/gunicorn_config.py sistema_eleicao.wsgi:application
directory=/home/ubuntu/e-voto-main
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gunicorn/evoto.log
EOF

# Configurar o Nginx
echo "Configurando o Nginx..."
cat > /etc/nginx/sites-available/evoto << EOF
server {
    listen 80;
    server_name seu_dominio_ou_ip;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/ubuntu/e-voto-main/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/e-voto-main/media/;
    }

    location / {
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_pass http://localhost:8000;
    }
}
EOF

# Ativar o site no Nginx
ln -sf /etc/nginx/sites-available/evoto /etc/nginx/sites-enabled
rm -f /etc/nginx/sites-enabled/default

# Verificar a configuração do Nginx
nginx -t

# Reiniciar o Nginx e o Supervisor
systemctl restart nginx
systemctl restart supervisor

echo "Configuração concluída! Lembre-se de editar o arquivo .env com suas configurações reais."
echo "Você também precisa configurar o banco de dados conforme as instruções acima."
