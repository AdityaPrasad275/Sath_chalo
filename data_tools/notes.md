# Build the image
docker build -t gtfs-gen .
# Run the generator (files will appear in ./gtfs_data)
docker run -v $(pwd)/gtfs_data:/app/gtfs_data gtfs-gen


docker compose up --build -d