# E-Voto - Sistema de Eleição

Sistema de votação eletrônica desenvolvido em Django.

## Requisitos

- Python 3.8+
- MySQL 5.7+
- Nginx
- Supervisor

## Implantação na AWS EC2

### 1. Preparação Local

1. Certifique-se de que seu código está funcionando localmente
2. Adicione seu código ao GitHub:
   ```bash
   git init
   git add .
   git commit -m "Preparação para implantação"
   git remote add origin https://github.com/seu-usuario/seu-repositorio.git
   git push -u origin main
   ```

### 2. Configuração da Instância EC2

1. Conecte-se à sua instância EC2 via SSH:
   ```bash
   ssh -i "sua-chave.pem" ubuntu@seu-ec2-dns.amazonaws.com
   ```

2. Clone seu repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git e-voto-main
   cd e-voto-main
   ```

3. Execute o script de configuração:
   ```bash
   sudo bash setup_ec2.sh
   ```

4. Configure o arquivo .env com suas credenciais reais:
   ```bash
   nano .env
   ```

5. Configure o banco de dados MySQL:
   ```bash
   sudo mysql -u root -p
   ```
   
   No prompt do MySQL, execute:
   ```sql
   CREATE DATABASE sistema_eleicao CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'seu_usuario_mysql'@'localhost' IDENTIFIED BY 'sua_senha_mysql';
   GRANT ALL PRIVILEGES ON sistema_eleicao.* TO 'seu_usuario_mysql'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

6. Crie e ative um ambiente virtual:
   ```bash
   python3 -m virtualenv venv
   source venv/bin/activate
   ```

7. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

8. Execute as migrações do Django:
   ```bash
   python manage.py migrate
   ```

9. Colete os arquivos estáticos:
   ```bash
   python manage.py collectstatic --noinput
   ```

10. Crie um superusuário do Django:
    ```bash
    python manage.py createsuperuser
    ```

11. Reinicie os serviços:
    ```bash
    sudo systemctl restart supervisor
    sudo systemctl restart nginx
    ```

12. Verifique se o Gunicorn está rodando:
    ```bash
    sudo supervisorctl status evoto
    ```

13. Verifique os logs se necessário:
    ```bash
    sudo tail -f /var/log/gunicorn/evoto.log
    ```

### 3. Configuração do Grupo de Segurança

1. No console da AWS, vá para EC2 > Grupos de segurança
2. Selecione o grupo de segurança associado à sua instância
3. Adicione regras de entrada para:
   - HTTP (porta 80)
   - HTTPS (porta 443) se estiver usando SSL
   - SSH (porta 22)

### 4. Atualizações Futuras

Para atualizar seu aplicativo após alterações:

1. Envie as alterações para o GitHub
2. Na instância EC2:
   ```bash
   cd e-voto-main
   git pull
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   sudo systemctl restart supervisor
   ```

## Solução de Problemas

- **Erro de conexão com o banco de dados**: Verifique as credenciais no arquivo .env
- **Erro 502 Bad Gateway**: Verifique os logs do Gunicorn e do Nginx
- **Arquivos estáticos não carregam**: Verifique a configuração do Nginx e execute collectstatic novamente
