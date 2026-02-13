#!/bin/bash
#
# iClock Server - Linux Installation Script
# This script automates the installation of iClock Server on Linux systems
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "Please run as root (use sudo)"
        exit 1
    fi
}

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        print_error "Cannot detect OS"
        exit 1
    fi
    print_info "Detected OS: $OS $VER"
}

install_dependencies() {
    print_info "Installing system dependencies..."
    
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
        apt update
        apt install -y python3 python3-pip python3-venv \
            postgresql postgresql-contrib \
            nginx redis-server \
            git build-essential libpq-dev python3-dev
    elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]]; then
        yum install -y python3 python3-pip \
            postgresql postgresql-server \
            nginx redis \
            git gcc postgresql-devel python3-devel
        postgresql-setup --initdb
    else
        print_error "Unsupported OS: $OS"
        exit 1
    fi
    
    print_info "Dependencies installed successfully"
}

setup_database() {
    print_info "Setting up PostgreSQL database..."
    
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql << EOF
SELECT 'CREATE DATABASE iclock_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'iclock_db')\gexec
CREATE USER iclock_user WITH PASSWORD 'changeme123';
ALTER ROLE iclock_user SET client_encoding TO 'utf8';
ALTER ROLE iclock_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE iclock_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE iclock_db TO iclock_user;
EOF
    
    print_warning "Please change the database password in .env file!"
    print_info "Database setup completed"
}

setup_application() {
    print_info "Setting up application..."
    
    APP_DIR="/opt/iclock_server"
    
    # Create directory if doesn't exist
    mkdir -p $APP_DIR
    cd $APP_DIR
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Python packages
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create .env file
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Please configure .env file with your settings"
    fi
    
    # Create necessary directories
    mkdir -p logs media staticfiles
    
    # Set permissions
    chown -R www-data:www-data $APP_DIR
    chmod -R 755 $APP_DIR
    chmod -R 775 media staticfiles logs
    
    print_info "Application setup completed"
}

setup_database_migrations() {
    print_info "Running database migrations..."
    
    cd /opt/iclock_server
    source venv/bin/activate
    
    python manage.py makemigrations
    python manage.py migrate
    
    print_info "Database migrations completed"
}

create_superuser() {
    print_info "Creating superuser..."
    
    cd /opt/iclock_server
    source venv/bin/activate
    
    python manage.py createsuperuser
}

collect_static() {
    print_info "Collecting static files..."
    
    cd /opt/iclock_server
    source venv/bin/activate
    
    python manage.py collectstatic --noinput
    
    print_info "Static files collected"
}

setup_systemd() {
    print_info "Setting up systemd service..."
    
    # Create socket directory
    mkdir -p /run/iclock
    chown www-data:www-data /run/iclock
    
    # Copy service file
    cp /opt/iclock_server/deploy/iclock.service /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    systemctl enable iclock
    systemctl start iclock
    
    print_info "Systemd service configured"
}

setup_nginx() {
    print_info "Setting up Nginx..."
    
    # Copy nginx configuration
    cp /opt/iclock_server/deploy/nginx.conf /etc/nginx/sites-available/iclock
    ln -sf /etc/nginx/sites-available/iclock /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    nginx -t
    
    # Restart nginx
    systemctl restart nginx
    systemctl enable nginx
    
    print_info "Nginx configured successfully"
}

setup_redis() {
    print_info "Setting up Redis..."
    
    systemctl start redis
    systemctl enable redis
    
    print_info "Redis configured"
}

setup_firewall() {
    print_info "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw --force enable
        print_info "UFW firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        print_info "Firewalld configured"
    else
        print_warning "No firewall detected"
    fi
}

print_summary() {
    echo ""
    echo "======================================"
    echo "Installation Complete!"
    echo "======================================"
    echo ""
    echo "Application URL: http://$(hostname -I | awk '{print $1}')"
    echo "Admin Panel: http://$(hostname -I | awk '{print $1}')/admin/"
    echo ""
    echo "Next steps:"
    echo "1. Edit /opt/iclock_server/.env with your configuration"
    echo "2. Change database password"
    echo "3. Review logs: journalctl -u iclock -f"
    echo "4. Access admin panel and create users"
    echo ""
    echo "Service commands:"
    echo "  sudo systemctl start iclock"
    echo "  sudo systemctl stop iclock"
    echo "  sudo systemctl restart iclock"
    echo "  sudo systemctl status iclock"
    echo ""
}

# Main installation
main() {
    print_info "Starting iClock Server installation..."
    
    check_root
    detect_os
    install_dependencies
    setup_redis
    setup_database
    setup_application
    setup_database_migrations
    collect_static
    
    echo ""
    read -p "Do you want to create a superuser now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_superuser
    fi
    
    setup_systemd
    setup_nginx
    setup_firewall
    
    print_summary
}

# Run main function
main
