var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var url = Environment.GetEnvironmentVariable("ASPNETCORE_URLS") ?? "http://0.0.0.0:5175";
builder.WebHost.UseUrls(url);

var app = builder.Build();

using (var db = new Database.DatabaseContext())
{
    db.Database.EnsureCreated();
}

app.UseSwagger();
app.UseSwaggerUI();
app.UseCors();
app.UseAuthorization();
app.MapControllers();

string mqttHost = Environment.GetEnvironmentVariable("MQTT_BROKER_HOST") ?? "172.17.0.1";
int mqttPort = int.TryParse(Environment.GetEnvironmentVariable("MQTT_BROKER_PORT"), out var p) ? p : 1883;
MQTT.MqttManager.StartMqttClient(mqttHost, mqttPort);
app.Run();