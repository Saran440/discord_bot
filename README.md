# Discord Bot

This is a Discord bot application. Follow the instructions below to run the app using Docker.

## Prerequisites

- Docker installed on your machine

## Running the App

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/discord_bot.git
    cd discord_bot
    ```

2. Create a `.env` file in the root directory and add your environment variables:

    ```env
    DISCORD_TOKEN=your_discord_token
    TIMEZONE="YOUR_TIMEZONE" # For example "Asia/Bangkok"
    ```

3. Build the Docker image:

    ```sh
    docker build -t discord_bot .
    ```

4. Run the Docker container:

    ```sh
    docker run --rm --name discord_bot -d discord_bot
    ```

## Stopping the App

In case you run Docker without -d
To stop the Docker container, press `Ctrl+C` in the terminal where the container is running.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
