# Build Stage
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /source

# Copy csproj files for optimal layer caching
COPY src/Database/Database.csproj src/Database/
COPY src/Logic/Logic.csproj src/Logic/
COPY src/API/API.csproj src/API/

# Restore dependencies
RUN dotnet restore src/API/API.csproj

# Copy source and publish
COPY src/ src/
RUN dotnet publish src/API/API.csproj -c Release -o /app/publish --no-restore

# Runtime Stage
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app

# Copy published binaries
COPY --from=build /app/publish .

# Default configuration
ENV ASPNETCORE_URLS=http://0.0.0.0:5175
ENV MQTT_BROKER_HOST=192.168.50.1
ENV MQTT_BROKER_PORT=1883
ENV DATABASE_CONNECTION_STRING="Data Source=/app/data/Backend.db"

# Directory for persistent database
RUN mkdir -p /app/data

EXPOSE 5175

ENTRYPOINT ["dotnet", "API.dll"]
