# Discord Bot

This is a Discord bot application. Follow the instructions below to run the app using Docker.

## Prerequisites

- Docker installed on your machine
- SQLite3 installed (for database management)

## Running the App

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/discord_bot.git
    cd discord_bot
    ```

2. Install SQLite3 (if not already installed):
    ```
    sudo apt install sqlite3
    ```

3. Create a `.env` file in the root directory and add your environment variables:

    ```env
    DISCORD_TOKEN=your_discord_token
    TIMEZONE="YOUR_TIMEZONE" # For example "Asia/Bangkok"
    ```

## Running the App

1. Build the Docker image:

    ```sh
    docker build -t discord_bot .
    ```

2. Run the Docker container:

    ```sh
    docker run --rm --name discord_bot -d discord_bot
    ```

## Stopping the App

If you run Docker without -d (detached mode), you can stop the bot using `Ctrl+C` in the terminal.
If running in detached mode, use:

    ```sh
    docker stop discord_bot
    ```

## Task Commands

The bot provides four main task management commands:

1. Add a Task

    ```/task add <task>```

    - Adds a new task to the list.
    - Example:

    ```/task add Complete project report```

2. Clear a Task

    ```/task clear <index>```

    - Removes a task by its index.
    - Example:

    ```/task clear 2```

    (Removes task at index 2)

3. Show Tasks

    ```/task show [@user]```

    - Shows all tasks if no user is specified.
    - If a user is mentioned, only tasks assigned to that user will be displayed.
    - Example:

    ```/task show @JohnDoe```

    (Displays tasks assigned to @JohnDoe)

4. Assign or Remove Task Assignment

    ```/task assign <index> [@user]```

    - Assigns a task to a specified user.
    - If no user is mentioned, the task assignment is removed.
    - Example:

    ```/task assign 1 @JaneDoe```

    (Assigns task 1 to @JaneDoe)

    ```/task assign 1```

    (Removes assignment from task 1)


## Accessing the Database

To check the stored tasks in the database:

1. Open a terminal and navigate to the project directory.
2. Run the following command to open the SQLite database:

    ```sh
    sqlite3 todo.db
    ```

3. To view all tasks stored in the database, run:

    ```sh
    SELECT * FROM tasks;
    ```

4. Exit SQLite by typing:

    ```sh
    .exit
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
