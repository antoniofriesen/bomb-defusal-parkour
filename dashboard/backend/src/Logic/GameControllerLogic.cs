using Database;
using Database.Entities;
using Logic.Models;
using MQTT;

namespace Logic;

public static class GameControllerLogic
{
    public static string StartGame(string teamName, int anzahlMitglieder)
    {
        using (var con = new DatabaseContext())
        {
            Team newTeam = new Team
            {
                TeamName = teamName,
                AnzahlMitglieder = anzahlMitglieder
            };

            Spiel newSpiel = new Spiel
            {
                Team = newTeam
            };
            newTeam.Spiel = newSpiel;
            con.Teams.Add(newTeam);
            con.Games.Add(newSpiel);
            con.SaveChanges();
        }

        string code = "";
        for (int i = 0; i < 6; i++)
        {
            string newDigit = new Random().Next(0, 10).ToString();
            code += newDigit;

            MQTT.MqttManager.PublishMqttMessage($"parkour/station/{i + 1}/start", "{ \"digit\": " + newDigit + " }");
        }

        return code;
    }

    public static void StopGame()
    {
        Console.WriteLine("Stop has been called, noting implemented though!");
    }

    public static StationDatenReadModel? StoreStationData(StationDatenCreateModel model)
    {
        StationDatenReadModel? readModel = null;
        try
        {
            using (DatabaseContext con = new DatabaseContext())
            {
                Spiel currentGame = con.Games.OrderByDescending(g => g.SpielId).First();
                StationDaten newInstance = new StationDaten
                {
                    Rating = model.Rating,
                    TimestampEnd = model.TimestampEnd,
                    TimestampStart = model.TimestampStart,
                    StationId = model.StationId,
                    State = model.State,
                    Spiel = currentGame
                };
                newInstance.StationId = model.StationId;
                con.GameData.Add(newInstance);
                con.SaveChanges();

                readModel = ToReadModel(newInstance);
            }

        }
        catch (Exception e)
        {
            Console.Error.WriteLine(e);
        }

        return readModel;
    }

    public static StationDatenReadModel[]? GetGameStatus()
    {
        try
        {
            using (var con = new DatabaseContext())
            {
                Spiel currentGame = con.Games.OrderByDescending(g => g.SpielId).First();
                Console.WriteLine("Current game: " + currentGame.SpielId);
                List<StationDaten> relevantData = new List<StationDaten>();

                for (int i = 1; i <= 6; i++)
                {
                    
                    if (con.GameData.Any(d => d.SpielId == currentGame.SpielId && d.StationId == i))
                    {
                        relevantData.Add(con.GameData.OrderByDescending(d => d.StationDatenId).First(d => d.SpielId == currentGame.SpielId && d.StationId == i));
                    }
                    else
                        Console.WriteLine($"No data for d.SpielId == {currentGame.SpielId} && d.StationId == {i}!");
                }

                List<StationDatenReadModel> models = new List<StationDatenReadModel>();
                foreach (StationDaten m in relevantData)
                {
                    models.Add(ToReadModel(m));
                }
                return models.ToArray();
            }
        }
        catch (Exception e)
        {
            Console.Error.WriteLine(e);
        }
        return null;
    }

    private static StationDatenReadModel ToReadModel(StationDaten instance)
    {
        return new StationDatenReadModel(instance.StationDatenId, instance.StationId, instance.SpielId, instance.State, instance.Rating, instance.TimestampStart, instance.TimestampEnd);
    }
}
