using Database;
using Database.Entities;
using Logic.Models;

namespace Logic;

public static class GameControllerLogic
{
    public static StationDatenReadModel? StoreStationData(StationDatenCreateModel model)
    {
        try
        {
            StationDaten newInstance = new StationDaten
            {
                Rating = model.Rating,
                TimestampEnd = model.TimestampEnd,
                TimestampStart = model.TimestampStart,
                StationId = model.StationId,
                State = model.State,
            };
            newInstance.StationId = model.StationId;

            using (DatabaseContext con = new DatabaseContext())
            {
                con.GameData.Add(newInstance);
                con.SaveChanges();
            }

            return ToReadModel(newInstance);
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
