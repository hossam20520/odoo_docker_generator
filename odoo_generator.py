import os
import argparse
import subprocess

def generate_docker_compose(odoo_version = 17 , port = 8078 , postgres_version = 15 , postgres_db = "postgres" , postgres_user="odoo" , enterprise_addons = "/enterprise-addons" , extra_addons = "/addons"):
    template = f"""
version: '3.1'
services:
  web:
    image: odoo:{odoo_version}
    depends_on:
      - db
    ports:
      - "{port}:8069"
    volumes:
      - ./odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
      - .{extra_addons}:/mnt/extra-addons
      - .{enterprise_addons}:/mnt/enterprise-addons

    environment:
      - PASSWORD_FILE=/run/secrets/postgresql_password
    secrets:
      - postgresql_password
  db:
    image: postgres:{postgres_version}
    environment:
      - POSTGRES_DB={postgres_db}
      - POSTGRES_PASSWORD_FILE=/run/secrets/postgresql_password
      - POSTGRES_USER={postgres_user}
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - ./odoo-db-data:/var/lib/postgresql/data
    secrets:
      - postgresql_password

secrets:
  postgresql_password:
    file: postgresql_password
"""
    with open("docker-compose.yaml", "w") as f:
        f.write(template)

# if __name__ == "__main__":
#     odoo_version = input("Enter Odoo version: ")  # Prompt user for Odoo version
#     generate_docker_compose(odoo_version)

def create_postgresql_password_file(password="admin"):
    with open("postgresql_password", "w") as f:
        f.write(password)


def create_odoo_conf_file(admin_password = "admin"):
    options = f"[options]\naddons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons,/mnt/enterprise-addons\nadmin_passwd = {admin_password}"
    with open(os.path.join("config", "odoo.conf"), "w") as f:
        f.write(options)

def create_folders():
    folders = ["odoo-db-data", "odoo-web-data", "config" , "addons" , "enterprise-addons" , "odoo-logs" ]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            pass
            # print(f"Folder '{folder}' created.")
        else:
            pass
            # print(f"Folder '{folder}' already exists.")

if __name__ == "__main__":
    print("""  
        #  ######                                     #    ######  ### 
        #  #     #   ##   #####  #####  # #####      # #   #     #  #  
        #  #     #  #  #  #    # #    # #   #       #   #  #     #  #  
        #  ######  #    # #####  #####  #   #      #     # ######   #  
        #  #   #   ###### #    # #    # #   #      ####### #        #  
        #  #    #  #    # #    # #    # #   #      #     # #        #  
        #  #     # #    # #####  #####  #   #      #     # #       ### 
        #                                                              """)
    
    parser = argparse.ArgumentParser(description="Generate Docker Compose file for Odoo")
    parser.add_argument("--odoo_version", type=str, default="17", help="Odoo version")
    parser.add_argument("--port", type=int, default=8078, help="Port for Odoo")
    parser.add_argument("--postgres_version", type=int, default=15, help="PostgreSQL version")
    parser.add_argument("--postgres_db", type=str, default="postgres", help="PostgreSQL database name")
    parser.add_argument("--odoo_user", type=str, default="odoo", help="Odoo user")
    args = parser.parse_args()

    # generate_docker_compose(args.odoo_version, args.port, args.postgres_version, args.postgres_db, args.odoo_user)


    create_folders()
    odoo_versions = [13.0, 14, 15 , 16 , 17]

    print("Select an Odoo version:")
    for i, version in enumerate(odoo_versions):
        print(f"{i+1}. Version {version}")

    while True:
        choice = input("Enter your choice (1/2/3/4/5): ")
        try:
            choice = int(choice)
            if choice in range(1, len(odoo_versions) + 1):
                selected_version = odoo_versions[choice - 1]
                break
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    port = args.port
    current_path = os.getcwd()
    postgres_version = input("Enter PostgreSQL version (default: 15): ") or 15
    postgres_db = input("Enter PostgreSQL database name (default: postgres): ") or "postgres"
    postgres_user = input("Enter PostgreSQL user (default: odoo): ") or "odoo"
    postgres_password = input("Enter PostgreSQL passowrd (default: admin): ") or "admin"
    odoo_port = input("Enter Odoo Port (default: 8078): ") or 8078
    master_password = input("Enter MasterPassword   (default: admin): ") or "admin"
    # enterprise_addons_path = input("Enter Enterprise Addons path (default: {current_path}): ") or 8078
    custom_path_choice = input("Do you want to use the current Folder ( ./enterprise-addons ) for the Enterprise Addons folder? (Y/N): ")

    while custom_path_choice.upper() not in ['Y', 'N']:
        custom_path_choice = input("Invalid input. Please enter 'Y' or 'N': ")

    if custom_path_choice.upper() == "Y":
        enterprise_addons_path = "/enterprise-addons"
    else:
        enterprise_addons_path = input("Enter Enterprise Addons path: ")

    custom_path_choice_ad = input("Do you want to use the current Folder ( ./addons ) for the Extra Addons folder? (Y/N): ")
    while custom_path_choice_ad.upper() not in ['Y', 'N']:
          custom_path_choice_ad = input("Invalid input. Please enter 'Y' or 'N': ")

    if custom_path_choice_ad.upper() == "Y":
        extra_addons = "/addons"
    else:
        extra_addons = input("Enter Extra Addons path: ")
    create_postgresql_password_file(password=postgres_password)
    create_odoo_conf_file(admin_password = master_password)
    generate_docker_compose(odoo_version=selected_version, port=odoo_port, postgres_version=postgres_version, postgres_db=postgres_db, postgres_user=postgres_user , enterprise_addons=enterprise_addons_path , extra_addons = extra_addons)
    print("\033[92mDocker Compose file and other necessary files created successfully!\033[0m")

    run_docker_compose = input("Do you want to run 'Odoo' now? (Y/N): ")
    while run_docker_compose.upper() not in ['Y', 'N']:
          run_docker_compose = input("Invalid input. Please enter 'Y' or 'N': ")

    if run_docker_compose.upper() == "Y":
        # Run `docker-compose up -d`
        try:
            subprocess.run(["docker", "compose" , "up", "-d"])
            print("\033[92mDocker Compose services started successfully!\033[0m")
        except Exception as e:
            print("\033[91mError:", e, "\033[0m")
    else:
        print("\033[93mPlease remember to run 'docker compose up -d' to start the services.\033[0m")
    # generate_docker_compose(args.odoo_version, args.port, args.postgres_version, args.postgres_db, args.odoo_user)
