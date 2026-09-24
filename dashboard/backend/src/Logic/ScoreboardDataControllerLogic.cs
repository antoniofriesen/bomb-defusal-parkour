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

    private static SpielReadModel ToReadModel(Spiel instance)
    {
        return new SpielReadModel(instance.SpielId, instance.Outcome, instance.Team.TeamName, instance.StartedAt, instance.EndedAt);
    }
}