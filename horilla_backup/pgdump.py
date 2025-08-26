import os
import subprocess


def dump_postgres_db(
    db_name, username, output_file, password=None, host="localhost", port=5432, format="sql"
):
    # Set environment variable for the password if provided
    if password:
        os.environ["PGPASSWORD"] = password

    # Construct the pg_dump command
    dump_command = [
        "pg_dump",
        "-h",
        host,
        "-p",
        str(port),
        "-U",
        username,
        "-f",
        output_file,
        db_name,
    ]
    
    # Add format-specific options
    if format == "sql":
        # SQL format (plain text)
        dump_command.extend(["-F", "p"])
    elif format == "custom":
        # Custom format (compressed)
        dump_command.extend(["-F", "c"])
    elif format == "directory":
        # Directory format
        dump_command.extend(["-F", "d"])
    elif format == "tar":
        # Tar format
        dump_command.extend(["-F", "t"])

    try:
        # Execute the pg_dump command
        result = subprocess.run(
            dump_command, check=True, text=True, capture_output=True
        )
    except subprocess.CalledProcessError as e:
        pass
    finally:
        # Clean up the environment variable
        if password:
            del os.environ["PGPASSWORD"]
