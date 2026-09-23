namespace Database.Entities;

public class Spiel
{
    public int SpielId {get; set;}
    public int TeamId {get; set;}
    public Team Team {get; set;} = null!;
    public ICollection<StationDaten> StationDaten {get; set;} = new List<StationDaten>();
}