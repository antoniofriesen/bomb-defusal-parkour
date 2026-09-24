namespace Database.Entities;

public class Spiel
{
    public int SpielId {get; set;}
    public string Outcome {get; set;} = "running";
    public int TeamId {get; set;}
    public Team Team {get; set;} = null!;
    public ICollection<StationDaten> StationDaten {get; set;} = new List<StationDaten>();
    public DateTime StartedAt {get; set;} = DateTime.UtcNow;
    public DateTime? EndedAt {get; set;} = null!;
}