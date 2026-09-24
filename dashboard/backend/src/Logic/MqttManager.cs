using System.Buffers;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json.Nodes;
using Logic.Models;
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

        bool clientInactive = false;
        try
        {
            if (!_mqttClient.ConnectAsync(mqttClientOptions).Wait(500))
            {
                Console.Error.WriteLine($"Failed to connect to MQTT broker at {brokerAddress}:{brokerPort}! (Timeout!)");
                clientInactive = true;
            }
        }
        catch (Exception e)
        {
            Console.Error.WriteLine($"Failed to connect to MQTT broker at {brokerAddress}:{brokerPort} (Exception!){Environment.NewLine}{e}");
            clientInactive = true;
        }

        if (clientInactive)
        {
            // Schedule a big, visible warning about the MQTT client not being active as the connection to the broker has failed.
            // Other components of the software will still be available and there might be a situation where the broker is offline but the database still needs to be accessed.
            // The warning gets shown after a 2 second delay due to other components of this software potentially spamming the console with their own initialization outputs.
            Task.Run(() => 
            {
                Task.Delay(2000).Wait();
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine("The MQTT client is not active during this session!" + Environment.NewLine + "The other components of the backend are still available though.");
                Console.ResetColor();
            });
            return;
        }

        Console.WriteLine("MQTT client connected!");

        for (int i = 1; i <= 6; i++)
        {
            string topic = $"parkour/station/{i}/status";
            _mqttClient.SubscribeAsync(new MqttTopicFilterBuilder().WithTopic(topic).Build()).Wait();
            Console.WriteLine("Subscribed to MQTT topic: " + topic);
        }
        _mqttClient.ApplicationMessageReceivedAsync += HandleReceivedMessage;

        Console.WriteLine("MQTT client ready");
    }

    private static Task HandleReceivedMessage(MqttApplicationMessageReceivedEventArgs e)
    {
        var topic = e.ApplicationMessage.Topic;
        var payload = e.ApplicationMessage.Payload.ToArray().Length == 0 ? null : System.Text.Encoding.UTF8.GetString(e.ApplicationMessage.Payload.ToArray());
        Console.WriteLine($"[MQTT, rec] [{topic}]: {payload}");
        JsonObject? jsonObject = JsonNode.Parse(payload ?? "{}") as JsonObject;
        if (jsonObject == null)
        {
            Console.Error.WriteLine("Failed to parse JSON payload!");
            return Task.CompletedTask;
        }

        if (topic.StartsWith("parkour/station/") && topic.EndsWith("/status"))
        {
            StationDatenCreateModel? create = null;
            try
            {
                Logic.Models.StationDatenCreateModel stationData = new(
                    StationId: jsonObject.TryGetPropertyValue("station_id", out JsonNode? stationIdNode)
                        ? stationIdNode?.GetValue<int>() ?? throw new InvalidDataException("Invalid station_id (inner)")
                        : throw new InvalidDataException("Invalid station_id (outer)"),

                    State: jsonObject.TryGetPropertyValue("state", out JsonNode? stateNode)
                        ? stateNode?.GetValue<string>() ?? "unknown"
                        : "unknown",

                    Rating: jsonObject.TryGetPropertyValue("rating", out JsonNode? ratingNode)
                        ? ratingNode?.GetValue<string>() ?? "unknown"
                        : "unknown",

                    TimestampStart: jsonObject.TryGetPropertyValue("timestamp_start", out JsonNode? timestampStartNode)
                        && DateTime.TryParse(timestampStartNode?.GetValue<string>(), out DateTime timestampStart)
                            ? timestampStart
                            : null,

                    TimestampEnd: jsonObject.TryGetPropertyValue("timestamp_end", out JsonNode? timestampEndNode)
                        && DateTime.TryParse(timestampEndNode?.GetValue<string>(), out DateTime timestampEnd)
                            ? timestampEnd
                            : null
                );
                create = stationData;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
            }

            if (create == null || Logic.GameControllerLogic.StoreStationData(create) == null)
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.Error.WriteLine("[MQTT] Failed to store StationData in database!" + Environment.NewLine + "Payload:" + Environment.NewLine + payload);
                Console.ResetColor();
            }
        }
        else
        {
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine($"[MQTT] Unhandled topic [{topic}]");
            Console.ResetColor();
        }
        

        return Task.CompletedTask;
    }

    public static void PublishMqttMessage(string topic, string payload)
    {
        if (_mqttClient == null || !_mqttClient.IsConnected)
        {
            Console.Error.WriteLine("MQTT client is not connected! Cannot publish message.");
            return;
        }

        var message = new MqttApplicationMessageBuilder()
            .WithTopic(topic)
            .WithPayload(Encoding.UTF8.GetBytes(payload))
            .Build();
        _ = _mqttClient.PublishAsync(message);

        Console.WriteLine($"[MQTT, snd] [{topic}]: {payload}");
    }
}
