# Data Query Server

A Streamlit-based application integrated with LangChain and MySQL for querying a database using natural language. This project includes a MySQL database setup via Docker Compose.

## Prerequisites

- **Python 3.8+**: Ensure Python is installed.
- **Docker**: Install Docker and Docker Compose for the MySQL service.
- **Dependencies**: Install Python packages listed in `requirements.txt`.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Python Dependencies

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Note**: Create a `requirements.txt` with:

```txt
streamlit
langchain
mysql-connector-python
openai
```

### 3. Set Up MySQL with Docker Compose

1. Ensure `docker-compose.yml` is in the project root (see below for sample).
2. Start the MySQL container:

   ```bash
   docker-compose up -d
   ```

3. Verify the container is running:

   ```bash
   docker ps
   ```

   - Container name: `mysql_db`
   - Default credentials:
     - Host: `localhost`
     - Port: `3306`
     - User: `user`
     - Password: `password`
     - Database: `test_db`
     - Root Password: `rootpassword`

4. (Optional) Populate the database:

   - Use a MySQL client to run the SQL script (e.g., `populate.sql`):

     ```bash
     docker exec -i mysql_db mysql -uuser -ppassword test_db < populate.sql
     ```

### 4. Run the Streamlit App

1. Ensure you're in the virtual environment (`source venv/bin/activate`).
2. Start the app:

   ```bash
   streamlit run app.py
   ```

3. Open your browser to `http://localhost:8501`.

### 5. Usage

- In the sidebar, enter MySQL credentials (e.g., `localhost`, `user`, `password`, `test_db`) and your OpenAI API key.
- Connect to the database, explore the structure, view sample data, and generate/execute SQL queries.

## Docker Compose File

Save this as `docker-compose.yml`:

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:latest
    container_name: mysql_db
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: test_db
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped
volumes:
  mysql_data:
```

## Stopping the Project

- Stop the Streamlit app: `Ctrl+C` in the terminal.
- Stop Docker Compose:

  ```bash
  docker-compose down
  ```

  - To remove data: `docker-compose down -v`.

## Notes

- Replace `<repository-url>` and `<repository-directory>` with your actual repo details.
- Ensure you have an OpenAI API key for LLM functionality.
