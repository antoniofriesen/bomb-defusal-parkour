using System.Buffers;
using System.Text;
using System.Text.Json.Nodes;
using MQTTnet;

namespace MQTT;

public static class MqttManager
{
    private static readonly MQTTnet.MqttClientFactory _mqttFactory = new();
    private static MQTTnet.IMqttClient? _mqttClient;

    public static void StartMqttClient(string brokerAddress, int brokerPort)
    {
        Console.WriteLine("Starting MQTT client...");
        var mqttClientOptions = new MqttClientOptionsBuilder()
            .WithTcpServer(brokerAddress, brokerPort)
            .WithClientId("Dashboard-Backend")
            .WithCredentials("pi_user", "group-1")
            .Build();

        _mqttClient = _mqttFactory.CreateMqttClient();
        if (!_mqttClient.ConnectAsync(mqttClientOptions).Wait(500))
        {
            Console.WriteLine("Failed to connect to MQTT broker!");
            return;
        }

        Console.WriteLine("MQTT client connected!");

        _mqttClient.SubscribeAsync(new MqttTopicFilterBuilder().WithTopic("parkour/station/4/status").Build()).Wait();
        _mqttClient.ApplicationMessageReceivedAsync += HandleReceivedMessage;

        Console.WriteLine("MQTT client ready");
    }

    private static Task HandleReceivedMessage(MqttApplicationMessageReceivedEventArgs e)
    {
        throw new NotImplementedException();
        /*var topic = e.ApplicationMessage.Topic;
        var payload = e.ApplicationMessage.Payload.ToArray().Length == 0 ? null : System.Text.Encoding.UTF8.GetString(e.ApplicationMessage.Payload.ToArray());
        Console.WriteLine($"[MQTT] [{topic}]: {payload}");
        JsonObject? jsonObject = JsonNode.Parse(payload ?? "{}") as JsonObject;
        if (jsonObject == null)
        {
            Console.Error.WriteLine("Failed to parse JSON payload!");
            return Task.CompletedTask;
        }

        if (topic.StartsWith("parkour/station/") && topic.EndsWith("/status"))
        {
            Logic.Models.StationDatenCreateModel stationData = new(
                SpielId: GameManager.CurrentGameId, // NOT IMPLEMENTED
                StationId: jsonObject.TryGetPropertyValue("stationId", out JsonNode? stationIdNode) ? stationIdNode?.GetValue<int>() ?? -1 : -1,
                State: jsonObject.TryGetPropertyValue("state", out JsonNode? stateNode) ? stateNode?.GetValue<string>() ?? "unknown" : "unknown",
                Rating: jsonObject.TryGetPropertyValue("rating", out JsonNode? ratingNode) ? ratingNode?.GetValue<string>() ?? "unknown" : "unknown",
                TimestampStart: jsonObject.TryGetPropertyValue("TimestampStart", out JsonNode? timestampStartNode) ? DateTime.Parse(timestampStartNode?.GetValue<string>() ?? "unknown") : DateTime.MinValue,
                TimestampEnd: jsonObject.TryGetPropertyValue("TimestampEnd", out JsonNode? timestampEndNode) ? DateTime.Parse(timestampEndNode?.GetValue<string>() ?? "unknown") : null
            );
        }
        */

        return Task.CompletedTask;
    }

    private static async Task PublishMqttMessage(string topic, string payload)
    {
        var message = new MqttApplicationMessageBuilder()
            .WithTopic(topic)
            .WithPayload(Encoding.UTF8.GetBytes(payload))
            .Build();
        _ = _mqttClient.PublishAsync(message);
    }
}
