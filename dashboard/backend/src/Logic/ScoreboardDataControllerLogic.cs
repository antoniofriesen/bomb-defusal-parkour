using Database;
using Database.Entities;
using Logic.Models;

namespace Logic;

public static class ScoreboardDataControllerLogic
{
    public static SpielReadModel[] GetGames()
    {
        using (var con = new DatabaseContext())
        {
            Spiel[] allGames = con.Games.ToArray();
            SpielReadModel[] allModels = new SpielReadModel[allGames.Length];

            for (int i = 0; i < allGames.Length; i++)
            {
                allModels[i] = ToReadModel(allGames[i]);
            }

            return allModels;
        }
    }

    public static StationEvent[] GetAllHistoricalStationData()
    {
        using (var con = new DatabaseContext())
        {
            List<StationEvent> events = new List<StationEvent>();
            StationDaten[] data = con.GameData.ToArray();

            foreach (StationDaten d in data)
            {
                events.Add(new StationEvent(d.SpielId, d.Spiel.Team.TeamName, d.StationId, d.State, d.TimestampStart, d.TimestampEnd));
            }

            return events.ToArray();
        }
    }

    private static SpielReadModel ToReadModel(Spiel instance)
    {
        return new SpielReadModel(instance.SpielId, instance.Outcome, instance.Team.TeamName, instance.StartedAt, instance.EndedAt);
    }
}

public record StationEvent(int GameId, string TeamName, int StationId, string State, DateTime? TimestampStart, DateTime? TimestampEnd);